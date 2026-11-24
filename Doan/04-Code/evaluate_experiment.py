"""Evaluate a Nerfstudio checkpoint and export image, timing, and field-query metrics.

The query count is the number of sampled 3D positions passed through Instant-NGP's
neural field during rendering. It is not a count of HTTP or Internet requests.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import time
from pathlib import Path
from typing import Any

import torch
import torchvision.utils as vutils


def _mean(values: list[float]) -> float:
    return statistics.fmean(values) if values else float("nan")


def _std(values: list[float]) -> float:
    return statistics.pstdev(values) if len(values) > 1 else 0.0


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(path: Path, summary: dict[str, Any]) -> None:
    title = summary.get("experiment_label") or f"{summary.get('method', 'model')} evaluation"
    rows = [
        ("Method", summary["method"]),
        ("Checkpoint step", summary["checkpoint_step"]),
        ("Held-out images", summary["num_images"]),
        ("PSNR (dB), mean ± std", f"{summary['psnr_mean']:.4f} ± {summary['psnr_std']:.4f}"),
        ("SSIM, mean ± std", f"{summary['ssim_mean']:.4f} ± {summary['ssim_std']:.4f}"),
        ("LPIPS, mean ± std", f"{summary['lpips_mean']:.4f} ± {summary['lpips_std']:.4f}"),
        ("Evaluation time (s)", f"{summary['evaluation_seconds']:.3f}"),
        ("Inference time (s)", f"{summary['inference_seconds']:.3f}"),
        ("Mean render time (ms/image)", f"{summary['mean_render_ms_per_image']:.3f}"),
        ("Images / second", f"{summary['images_per_second']:.4f}"),
        ("Rays / second", f"{summary['rays_per_second']:.2f}"),
        ("Rays evaluated", summary["total_rays"]),
        ("Field sample queries", summary["field_sample_queries_total"]),
        ("Field sample queries / ray", f"{summary['field_sample_queries_per_ray']:.4f}"),
        ("Peak GPU memory (MiB)", f"{summary['peak_gpu_memory_mib']:.2f}"),
        ("Model parameters", summary["num_parameters"]),
        ("Checkpoint size (MiB)", f"{summary['checkpoint_size_mib']:.2f}"),
    ]
    if summary.get("training_seconds") is not None:
        rows.insert(7, ("Training time (s)", f"{summary['training_seconds']:.3f}"))
    with path.open("w", encoding="utf-8") as handle:
        handle.write(f"# {title}\n\n")
        handle.write("| Metric | Value |\n|---|---:|\n")
        for name, value in rows:
            handle.write(f"| {name} | {value} |\n")
        handle.write(f"\n{summary['query_count_definition']}\n")


def _infer_static_samples_per_ray(model: Any) -> tuple[int, int, int] | None:
    """Return (total_per_ray, proposal_per_ray, nerf_per_ray) for proposal-based models like Nerfacto."""
    cfg = getattr(model, "config", None)
    if cfg is None:
        return None
    nerf_n = getattr(cfg, "num_nerf_samples_per_ray", None)
    prop_n = getattr(cfg, "num_proposal_samples_per_ray", None)
    if nerf_n is not None and prop_n is not None:
        prop_total = int(sum(prop_n))
        nerf_total = int(nerf_n)
        return (prop_total + nerf_total, prop_total, nerf_total)
    coarse_n = getattr(cfg, "num_coarse_samples", None)
    fine_n = getattr(cfg, "num_importance_samples", None)
    if coarse_n is not None and fine_n is not None:
        return (int(coarse_n) + int(fine_n), int(coarse_n), int(fine_n))
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True, help="Nerfstudio run's config.yml")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--training-seconds", type=float, default=None)
    parser.add_argument("--eval-rays-per-chunk", type=int, default=8192)
    parser.add_argument("--experiment-label", type=str, default=None)
    parser.add_argument("--save-comparisons", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    if not args.config.is_file():
        parser.error(f"Config not found: {args.config}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    comparison_dir = args.output_dir / "comparisons"
    if args.save_comparisons:
        comparison_dir.mkdir(parents=True, exist_ok=True)

    from nerfstudio.utils.eval_utils import eval_setup

    config, pipeline, checkpoint_path, checkpoint_step = eval_setup(
        args.config,
        eval_num_rays_per_chunk=args.eval_rays_per_chunk,
        test_mode="test",
    )
    pipeline.eval()
    model = pipeline.model
    datamanager = pipeline.datamanager
    eval_loader = datamanager.fixed_indices_eval_dataloader
    eval_dataset = datamanager.eval_dataset
    train_dataset = getattr(datamanager, "train_dataset", None)
    num_images = len(eval_dataset)
    if num_images == 0:
        raise RuntimeError("The COLMAP eval split is empty; cannot calculate image metrics.")

    if torch.cuda.is_available():
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()

    static_samples_info = _infer_static_samples_per_ray(model)
    num_parameters = int(sum(p.numel() for p in model.parameters()))
    checkpoint_size_mib = checkpoint_path.stat().st_size / (1024**2)

    per_image: list[dict[str, Any]] = []
    inference_seconds = 0.0
    total_rays = 0
    total_field_queries = 0
    used_dynamic_samples = False
    evaluation_started = time.perf_counter()

    with torch.inference_mode():
        for index, (camera, batch) in enumerate(eval_loader):
            height = int(camera.height.reshape(-1)[0].item())
            width = int(camera.width.reshape(-1)[0].item())
            num_rays = height * width

            if torch.cuda.is_available():
                torch.cuda.synchronize()
            render_started = time.perf_counter()
            outputs = model.get_outputs_for_camera(camera=camera)
            if torch.cuda.is_available():
                torch.cuda.synchronize()
            render_seconds = time.perf_counter() - render_started
            inference_seconds += render_seconds

            prediction = outputs.get("rgb")
            ground_truth = batch.get("image")
            if prediction is not None and ground_truth is not None:
                prediction_hw = tuple(prediction.shape[-3:-1])
                ground_truth_hw = tuple(ground_truth.shape[-3:-1])
                if prediction_hw != ground_truth_hw:
                    raise RuntimeError(
                        "Rendered image and ground truth have different dimensions: "
                        f"prediction={prediction_hw}, ground_truth={ground_truth_hw}. "
                        "Check the COLMAP intrinsics and image downscale factor in config.yml."
                    )

            if "num_samples_per_ray" in outputs:
                field_queries = int(outputs["num_samples_per_ray"].sum().item())
                used_dynamic_samples = True
            elif static_samples_info is not None:
                field_queries = int(num_rays * static_samples_info[0])
            else:
                raise RuntimeError(
                    "Model did not expose num_samples_per_ray or static sample counts; cannot report field queries."
                )
            total_rays += num_rays
            total_field_queries += field_queries

            image_metrics, image_outputs = model.get_image_metrics_and_images(outputs, batch)
            filename = getattr(eval_dataset, "image_filenames", [])[index]
            image_name = Path(filename).name if filename else f"eval_{index:04d}.png"
            record: dict[str, Any] = {
                "image_index": index,
                "image": image_name,
                "height": height,
                "width": width,
                "rays": num_rays,
                "field_sample_queries": field_queries,
                "field_sample_queries_per_ray": field_queries / num_rays,
                "render_seconds": render_seconds,
                "rays_per_second": num_rays / render_seconds if render_seconds > 0 else math.inf,
                **{key: float(value) for key, value in image_metrics.items()},
            }
            per_image.append(record)

            if args.save_comparisons:
                # The model returns a side-by-side [ground truth | prediction] image.
                comparison = image_outputs["img"].detach().permute(2, 0, 1).float().cpu().clamp(0, 1)
                output_name = f"{index:04d}_{Path(image_name).stem}.png"
                vutils.save_image(comparison, comparison_dir / output_name)

            print(
                f"[{index + 1}/{num_images}] {image_name}: "
                f"PSNR={record['psnr']:.3f}, SSIM={record['ssim']:.4f}, "
                f"LPIPS={record['lpips']:.4f}, field queries/ray={record['field_sample_queries_per_ray']:.2f}",
                flush=True,
            )

    if torch.cuda.is_available():
        torch.cuda.synchronize()
        peak_gpu_memory_mib = torch.cuda.max_memory_allocated() / (1024**2)
        gpu_name = torch.cuda.get_device_name(0)
    else:
        peak_gpu_memory_mib = 0.0
        gpu_name = "CPU"
    evaluation_seconds = time.perf_counter() - evaluation_started

    if used_dynamic_samples:
        query_def = (
            "sum(num_samples_per_ray): sampled 3D positions passed to the neural field during inference; "
            "not Internet requests and not FLOPs"
        )
    elif static_samples_info is not None:
        query_def = (
            f"proposal ({static_samples_info[1]}/ray) + main NeRF field ({static_samples_info[2]}/ray) = "
            f"{static_samples_info[0]} sampled 3D positions/ray during inference; not Internet requests and not FLOPs"
        )
    else:
        query_def = "sampled 3D positions passed to the neural field during inference"

    summary: dict[str, Any] = {
        "experiment_label": args.experiment_label,
        "config": str(args.config.resolve()),
        "checkpoint": str(checkpoint_path.resolve()),
        "checkpoint_step": int(checkpoint_step),
        "method": config.method_name,
        "eval_split": "COLMAP interval hold-out split",
        "num_train_images": len(train_dataset) if train_dataset is not None else None,
        "num_images": num_images,
        "total_rays": total_rays,
        "psnr_mean": _mean([row["psnr"] for row in per_image]),
        "psnr_std": _std([row["psnr"] for row in per_image]),
        "ssim_mean": _mean([row["ssim"] for row in per_image]),
        "ssim_std": _std([row["ssim"] for row in per_image]),
        "lpips_mean": _mean([row["lpips"] for row in per_image]),
        "lpips_std": _std([row["lpips"] for row in per_image]),
        "inference_seconds": inference_seconds,
        "evaluation_seconds": evaluation_seconds,
        "mean_render_ms_per_image": inference_seconds * 1000 / num_images,
        "images_per_second": num_images / inference_seconds if inference_seconds > 0 else 0.0,
        "rays_per_second": total_rays / inference_seconds if inference_seconds > 0 else 0.0,
        "field_sample_queries_total": total_field_queries,
        "field_sample_queries_per_ray": total_field_queries / total_rays if total_rays else 0.0,
        "proposal_samples_per_ray": static_samples_info[1] if (not used_dynamic_samples and static_samples_info) else None,
        "nerf_field_samples_per_ray": static_samples_info[2] if (not used_dynamic_samples and static_samples_info) else None,
        "peak_gpu_memory_mib": peak_gpu_memory_mib,
        "num_parameters": num_parameters,
        "checkpoint_size_mib": checkpoint_size_mib,
        "gpu": gpu_name,
        "training_seconds": args.training_seconds,
        "query_count_definition": query_def,
    }

    (args.output_dir / "metrics.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_csv(args.output_dir / "metrics.csv", [summary], list(summary))
    _write_csv(args.output_dir / "per-image-metrics.csv", per_image, list(per_image[0]))
    _write_markdown(args.output_dir / "metrics.md", summary)

    print(f"\nAggregate metrics: {args.output_dir / 'metrics.md'}", flush=True)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
