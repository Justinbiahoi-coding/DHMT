"""Build synchronized Kaggle notebooks from the local experiment scripts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
CODE = ROOT / "04-Code"
KERNEL = CODE / "kaggle-kernel"
NERFSTUDIO_COMMIT = "50e0e3c70c775e89333256213363badbf074f29d"
SEED = 42
ITERATIONS = 30_000


def _cell(cell_type: str, source: str) -> dict[str, Any]:
    cell: dict[str, Any] = {"cell_type": cell_type, "metadata": {}, "source": source.splitlines(keepends=True)}
    if cell_type == "code":
        cell.update({"execution_count": None, "outputs": []})
    return cell


def _build_cells(title: str, description: str) -> list[dict[str, Any]]:
    evaluator_source = (CODE / "evaluate_experiment.py").read_text(encoding="utf-8")
    renderer_source = (CODE / "render_novel_view.py").read_text(encoding="utf-8")

    setup = f'''import hashlib
import importlib.metadata as metadata
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import torch

SEED = {SEED}
NERFSTUDIO_COMMIT = "{NERFSTUDIO_COMMIT}"
repo = Path("/kaggle/working/nerfstudio")
print("Python:", sys.version)
print("PyTorch:", torch.__version__)
print("PyTorch CUDA:", torch.version.cuda)
print("CUDA available:", torch.cuda.is_available())
assert torch.cuda.is_available(), "Enable a Kaggle GPU in Notebook Settings."
print("GPU:", torch.cuda.get_device_name(0))

nvcc = shutil.which("nvcc")
if nvcc is None:
    raise RuntimeError("nvcc is unavailable; tiny-cuda-nn needs the CUDA Toolkit to compile.")
nvcc_info = subprocess.run([nvcc, "--version"], text=True, capture_output=True, check=True).stdout
print(nvcc_info)
toolkit_match = re.search(r"release (\\d+\\.\\d+)", nvcc_info)
if toolkit_match and torch.version.cuda and toolkit_match.group(1) != torch.version.cuda:
    print("CUDA toolkit and PyTorch CUDA versions differ; continuing with the Kaggle-provided runtime.")

if not repo.exists():
    subprocess.run([
        "git", "clone", "--filter=blob:none", "--no-checkout",
        "https://github.com/nerfstudio-project/nerfstudio.git", str(repo)
    ], check=True)
subprocess.run(["git", "-C", str(repo), "fetch", "--depth", "1", "origin", NERFSTUDIO_COMMIT], check=True)
subprocess.run(["git", "-C", str(repo), "checkout", "--detach", NERFSTUDIO_COMMIT], check=True)
nerfstudio_commit = subprocess.run(
    ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True, capture_output=True, check=True
).stdout.strip()
assert nerfstudio_commit == NERFSTUDIO_COMMIT
print("Pinned Nerfstudio commit:", nerfstudio_commit)
'''

    install = '''# Keep Kaggle's preinstalled PyTorch/CUDA. Pin Pillow below 12 for Nerfstudio 1.1.5.
subprocess.run([sys.executable, "-m", "pip", "install", "ninja", "packaging", "Pillow<12"], check=True)
subprocess.run([sys.executable, "-m", "pip", "install", "-e", str(repo)], check=True)
subprocess.run([sys.executable, "-m", "pip", "install", "Pillow<12"], check=True)

# NerfAcc 0.5.2 uses cub::Equality(), removed from the CUDA 13 CUB headers.
# Patch its installed source idempotently before its CUDA extension is compiled.
nerfacc_spec = importlib.util.find_spec("nerfacc")
if nerfacc_spec is None or nerfacc_spec.origin is None:
    raise RuntimeError("nerfacc was not installed with Nerfstudio.")
nerfacc_root = Path(nerfacc_spec.origin).parent
scan_file = nerfacc_root / "cuda" / "csrc" / "scan.cu"
scan_text = scan_file.read_text(encoding="utf-8")
if "#include <thrust/functional.h>" not in scan_text:
    scan_text = "#include <thrust/functional.h>\\n" + scan_text
if "cub::Equality()" in scan_text:
    scan_text = scan_text.replace("cub::Equality()", "thrust::equal_to<int64_t>()")
elif "thrust::equal_to<int64_t>()" not in scan_text:
    raise RuntimeError(f"Unexpected NerfAcc scan.cu source; inspect before patching: {scan_file}")
scan_file.write_text(scan_text, encoding="utf-8")
print("CUDA 13 compatible NerfAcc scan:", scan_file)

# PyTorch 2.6+ defaults torch.load to weights_only=True. Nerfstudio checkpoints
# contain trusted NumPy metadata and are produced by this notebook's own trainer.
eval_utils_file = repo / "nerfstudio" / "utils" / "eval_utils.py"
eval_utils_text = eval_utils_file.read_text(encoding="utf-8")
old_load = 'torch.load(load_path, map_location="cpu")'
compatible_load = 'torch.load(load_path, map_location="cpu", weights_only=False)'
if old_load in eval_utils_text:
    eval_utils_text = eval_utils_text.replace(old_load, compatible_load)
elif compatible_load not in eval_utils_text:
    raise RuntimeError(f"Could not apply PyTorch checkpoint compatibility patch: {eval_utils_file}")
eval_utils_file.write_text(eval_utils_text, encoding="utf-8")
print("Nerfstudio checkpoint load compatibility:", eval_utils_file)

# Build NVlabs tiny-cuda-nn for the active Kaggle GPU's compute capability.
env = os.environ.copy()
major, minor = torch.cuda.get_device_capability(0)
env["TCNN_CUDA_ARCHITECTURES"] = f"{major}{minor}"
print("tiny-cuda-nn CUDA architecture:", env["TCNN_CUDA_ARCHITECTURES"])
ldconfig = subprocess.run(["ldconfig", "-p"], text=True, capture_output=True, check=False).stdout
driver_candidates = re.findall(r"\\s+(\\/\\S*libcuda\\.so\\.1)\\s*$", ldconfig, flags=re.MULTILINE)
driver_candidates += [
    "/usr/lib/x86_64-linux-gnu/libcuda.so.1",
    "/usr/lib64/libcuda.so.1",
    "/usr/local/nvidia/lib64/libcuda.so.1",
]
driver_lib = next((Path(path) for path in driver_candidates if Path(path).is_file()), None)
if driver_lib is None:
    raise RuntimeError("Could not locate the CUDA driver library libcuda.so.1.")
link_dir = Path("/kaggle/working/cuda-link")
link_dir.mkdir(parents=True, exist_ok=True)
cuda_link = link_dir / "libcuda.so"
if cuda_link.exists() or cuda_link.is_symlink():
    cuda_link.unlink()
cuda_link.symlink_to(driver_lib)
env["LIBRARY_PATH"] = str(link_dir) + os.pathsep + env.get("LIBRARY_PATH", "")

tcnn_repo = Path("/kaggle/working/tiny-cuda-nn")
if tcnn_repo.exists():
    current_tcnn_tag = subprocess.run(
        ["git", "-C", str(tcnn_repo), "describe", "--tags", "--exact-match"],
        text=True,
        capture_output=True,
        check=False,
    )
    if current_tcnn_tag.returncode or current_tcnn_tag.stdout.strip() != "v2.0":
        shutil.rmtree(tcnn_repo)
if not tcnn_repo.exists():
    subprocess.run([
        "git", "clone", "--recursive", "--depth", "1", "--branch", "v2.0",
        "https://github.com/NVlabs/tiny-cuda-nn.git", str(tcnn_repo)
    ], check=True)
assert subprocess.run(
    ["git", "-C", str(tcnn_repo), "describe", "--tags", "--exact-match"],
    text=True,
    capture_output=True,
    check=True,
).stdout.strip() == "v2.0"
tcnn_commit = subprocess.run(
    ["git", "-C", str(tcnn_repo), "rev-parse", "HEAD"], text=True, capture_output=True, check=True
).stdout.strip()
subprocess.run([
    sys.executable, "-m", "pip", "install", "-v", "--no-build-isolation",
    str(tcnn_repo / "bindings" / "torch")
], check=True, env=env)

import tinycudann as tcnn
encoding = tcnn.Encoding(3, {
    "otype": "HashGrid", "n_levels": 2, "n_features_per_level": 2,
    "log2_hashmap_size": 4, "base_resolution": 4, "per_level_scale": 2.0,
}).cuda()
with torch.no_grad():
    encoded = encoding(torch.rand((8, 3), device="cuda"))
assert encoded.shape == (8, 4)
print("tiny-cuda-nn commit:", tcnn_commit)
print("tiny-cuda-nn CUDA smoke check:", tuple(encoded.shape))
'''

    dataset = '''input_dir = Path("/kaggle/input/mipnerf360-garden-images8")
if not input_dir.exists():
    try:
        import kagglehub
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "kagglehub"], check=True)
        import kagglehub
    input_dir = Path(kagglehub.dataset_download("nminhkhoa24120073/mipnerf360-garden-images8/versions/1"))

def is_scene_root(path: Path) -> bool:
    return (path / "images_8").is_dir() and all(
        (path / "sparse" / "0" / filename).is_file()
        for filename in ("cameras.bin", "images.bin", "points3D.bin")
    )

if not is_scene_root(input_dir):
    possible_roots = [path.parent for path in input_dir.rglob("images_8") if is_scene_root(path.parent)]
    if len(possible_roots) != 1:
        raise RuntimeError(f"Expected one Garden dataset root with images_8 and sparse/0; found {possible_roots}")
    input_dir = possible_roots[0]

scene = Path("/kaggle/working/mipnerf360-garden")
if not scene.exists():
    shutil.copytree(input_dir, scene)
images_8_dir = scene / "images_8"
images = sorted(path for path in images_8_dir.iterdir() if path.is_file())
if len(images) != 185:
    raise RuntimeError(f"Expected 185 images in images_8, found {len(images)}")
assert is_scene_root(scene)

# COLMAP intrinsics describe the original images. Nerfstudio needs the logical
# `images` directory to discover filenames, then applies factor 8 and loads the
# already-downscaled files from `images_8`. If original images are present, keep
# them; otherwise use the available image_8 files as filename placeholders.
images_dir = scene / "images"
if not images_dir.exists():
    shutil.copytree(images_8_dir, images_dir)
image_names = {path.name for path in images}
parser_image_names = {path.name for path in images_dir.iterdir() if path.is_file()}
if image_names != parser_image_names:
    raise RuntimeError("The images and images_8 directories must contain the same filenames.")

# Fail before training if the low-resolution images do not correspond to the
# COLMAP camera dimensions at the configured downscale factor.
from PIL import Image
from nerfstudio.data.utils.colmap_parsing_utils import read_cameras_binary, read_images_binary

colmap_dir = scene / "sparse" / "0"
cameras = read_cameras_binary(colmap_dir / "cameras.bin")
colmap_images = read_images_binary(colmap_dir / "images.bin")
colmap_image_names = {record.name for record in colmap_images.values()}
if colmap_image_names != image_names:
    missing = sorted(colmap_image_names - image_names)[:5]
    unregistered = sorted(image_names - colmap_image_names)[:5]
    raise RuntimeError(
        "COLMAP and images_8 filenames differ. "
        f"Missing image files: {missing}; not registered in COLMAP: {unregistered}"
    )

camera_image_sizes = {}
for record in colmap_images.values():
    camera = cameras[record.camera_id]
    image_path = images_8_dir / record.name
    with Image.open(image_path) as image:
        image_size = image.size
    expected_size = (camera.width // 8, camera.height // 8)
    if image_size != expected_size:
        raise RuntimeError(
            f"Image/COLMAP scale mismatch for {record.name}: image_8={image_size}, "
            f"COLMAP/8={expected_size} from camera {camera.id} ({camera.width}x{camera.height}). "
            "Fix the image preprocessing or downscale factor before training."
        )
    camera_image_sizes.setdefault(camera.id, set()).add(image_size)

if any(len(sizes) != 1 for sizes in camera_image_sizes.values()):
    raise RuntimeError(f"A COLMAP camera ID maps to multiple image sizes: {camera_image_sizes}")
print("Validated 185 images against COLMAP using downscale factor 8.")

digest = hashlib.sha256()
for path in [scene / "sparse" / "0" / "cameras.bin", scene / "sparse" / "0" / "images.bin", scene / "sparse" / "0" / "points3D.bin", *images]:
    digest.update(path.relative_to(scene).as_posix().encode("utf-8"))
    with path.open("rb") as content:
        for chunk in iter(lambda: content.read(1024 * 1024), b""):
            digest.update(chunk)
dataset_fingerprint = digest.hexdigest()
print("Dataset:", scene, "| images:", len(images), "| fingerprint:", dataset_fingerprint)
'''

    train = '''# Official full run: Nerfstudio Instant-NGP default 30,000 steps, fixed seed, COLMAP interval hold-out.
os.chdir(repo)
run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
output_root = Path("/kaggle/working/outputs") / f"run-{run_id}"
train_command = [
    "ns-train", "instant-ngp",
    "--machine.num-devices", "1",
    "--machine.seed", str(SEED),
    "--max-num-iterations", "30000",
    "--steps-per-save", "2000",
    "--steps-per-eval-all-images", "30000",
    "--viewer.quit-on-train-completion", "True",
    "--output-dir", str(output_root),
    "--data", str(scene),
    "colmap", "--images-path", "images", "--colmap-path", "sparse/0",
    "--downscale-factor", "8", "--downscale-rounding-mode", "floor",
    "--eval-mode", "interval", "--eval-interval", "8",
]
print("Running:", " ".join(train_command), flush=True)
train_started_utc = datetime.now(timezone.utc).isoformat()
train_started = time.perf_counter()
train_log_path = Path("/kaggle/working/training.log")
with train_log_path.open("w", encoding="utf-8") as log_file:
    process = subprocess.Popen(
        train_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1, env={**os.environ, "PYTHONUNBUFFERED": "1"}
    )
    assert process.stdout is not None
    for line in process.stdout:
        print(line, end="", flush=True)
        log_file.write(line)
        log_file.flush()
    train_return_code = process.wait()
training_seconds = time.perf_counter() - train_started
if train_return_code:
    raise subprocess.CalledProcessError(train_return_code, train_command)

checkpoint_candidates = list(output_root.rglob("step-*.ckpt"))
if not checkpoint_candidates:
    raise RuntimeError(f"Training finished but no checkpoint was found under {output_root}")

def checkpoint_step(path: Path) -> int:
    match = re.fullmatch(r"step-(\\d+)\\.ckpt", path.name)
    if match is None:
        raise RuntimeError(f"Unexpected checkpoint filename: {path.name}")
    return int(match.group(1))

checkpoint_path = max(checkpoint_candidates, key=checkpoint_step)
saved_step = checkpoint_step(checkpoint_path)
if saved_step < 29999:
    raise RuntimeError(f"Expected the final 30,000-step checkpoint (step 29999), found step {saved_step}")
print("Final checkpoint step:", saved_step)
config_path = checkpoint_path.parents[1] / "config.yml"
assert config_path.is_file(), f"Training config not found beside checkpoint: {config_path}"
run_dir = config_path.parent
artifacts = Path("/kaggle/working/experiment-artifacts")
artifact_checkpoints = artifacts / "checkpoints"
artifact_checkpoints.mkdir(parents=True, exist_ok=True)
saved_checkpoint = artifact_checkpoints / checkpoint_path.name
shutil.copy2(checkpoint_path, saved_checkpoint)
shutil.copy2(config_path, artifacts / "config.yml")
shutil.copy2(train_log_path, artifacts / "training.log")
pip_freeze = subprocess.run(
    [sys.executable, "-m", "pip", "freeze"], text=True, capture_output=True, check=True
).stdout
(artifacts / "pip-freeze.txt").write_text(pip_freeze, encoding="utf-8")
gpu_details = subprocess.run(
    ["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv"],
    text=True,
    capture_output=True,
    check=False,
).stdout.strip()

def package_version(name: str) -> str | None:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None

run_metadata = {
    "run_id": run_id,
    "started_utc": train_started_utc,
    "training_seconds": training_seconds,
    "seed": SEED,
    "method": "instant-ngp",
    "iterations": 30000,
    "checkpoint_step": saved_step,
    "eval_mode": "interval",
    "eval_interval": 8,
    "images_path": "images",
    "downscale_factor": 8,
    "downscale_rounding_mode": "floor",
    "images": len(images),
    "dataset_fingerprint": dataset_fingerprint,
    "gpu": torch.cuda.get_device_name(0),
    "gpu_driver": gpu_details,
    "python": sys.version,
    "torch": torch.__version__,
    "torch_cuda": torch.version.cuda,
    "nerfstudio_commit": nerfstudio_commit,
    "tiny_cuda_nn_commit": tcnn_commit,
    "tiny_cuda_nn_release": "v2.0",
    "nerfacc_version": package_version("nerfacc"),
    "pillow_version": package_version("Pillow"),
    "command": train_command,
    "run_directory": str(run_dir),
    "config": str((artifacts / "config.yml").resolve()),
    "checkpoint": str(saved_checkpoint.resolve()),
}
(artifacts / "run-metadata.json").write_text(json.dumps(run_metadata, indent=2), encoding="utf-8")
print("Training finished in", round(training_seconds / 60, 2), "minutes")
print("Final checkpoint:", saved_checkpoint)
'''

    eval_run = '''from pathlib import Path

artifacts = Path("/kaggle/working/experiment-artifacts")
artifacts.mkdir(parents=True, exist_ok=True)
evaluation_dir = artifacts / "evaluation"
eval_command = [
    sys.executable, "/kaggle/working/evaluate_experiment.py",
    "--config", str(config_path),
    "--output-dir", str(evaluation_dir),
    "--training-seconds", str(training_seconds),
    "--eval-rays-per-chunk", "8192",
]
print("Running evaluation:", " ".join(eval_command), flush=True)
subprocess.run(eval_command, cwd=repo, check=True)
'''

    render_run = '''video_path = artifacts / "novel_view_spiral.mp4"
render_command = [
    sys.executable, "/kaggle/working/render_novel_view.py",
    "--config", str(config_path),
    "--output", str(video_path),
    "--seconds", "8",
    "--fps", "24",
    "--radius", "0.1",
    "--downscale-factor", "2",
]
print("Running novel-view render:", " ".join(render_command), flush=True)
subprocess.run(render_command, cwd=repo, check=True)
'''

    show = '''import json
import subprocess
from pathlib import Path

import pandas as pd
from IPython.display import Video, display
from PIL import Image

metrics = json.loads(
    (artifacts / "evaluation" / "metrics.json").read_text(encoding="utf-8")
)

scorecard = pd.DataFrame([
    {
        "Metric": "PSNR mean ± std (dB)",
        "Value": f"{metrics['psnr_mean']:.4f} ± {metrics['psnr_std']:.4f}",
    },
    {
        "Metric": "SSIM mean ± std",
        "Value": f"{metrics['ssim_mean']:.4f} ± {metrics['ssim_std']:.4f}",
    },
    {
        "Metric": "LPIPS mean ± std",
        "Value": f"{metrics['lpips_mean']:.4f} ± {metrics['lpips_std']:.4f}",
    },
    {
        "Metric": "Training time (s)",
        "Value": (
            f"{metrics['training_seconds']:.2f}"
            if metrics.get("training_seconds") is not None
            else "N/A"
        ),
    },
    {
        "Metric": "Evaluation time (s)",
        "Value": f"{metrics['evaluation_seconds']:.2f}",
    },
    {
        "Metric": "Field sample queries / ray",
        "Value": f"{metrics['field_sample_queries_per_ray']:.4f}",
    },
    {
        "Metric": "Peak GPU memory (MiB)",
        "Value": f"{metrics['peak_gpu_memory_mib']:.2f}",
    },
])

display(scorecard)
display(pd.read_csv(artifacts / "evaluation" / "per-image-metrics.csv"))

source_video = Path(video_path)
upright_video = source_video.with_name(
    f"{source_video.stem}_upright{source_video.suffix}"
)
upright_frame = upright_video.with_name(
    f"{upright_video.stem}_frame.png"
)

# Rotate every frame 180 degrees. This does not retrain the model.
subprocess.run(
    [
        "ffmpeg",
        "-y",
        "-i", str(source_video),
        "-vf", "hflip,vflip",
        "-an",
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        str(upright_video),
    ],
    check=True,
)

subprocess.run(
    [
        "ffmpeg",
        "-y",
        "-ss", "2",
        "-i", str(upright_video),
        "-frames:v", "1",
        str(upright_frame),
    ],
    check=True,
)

print("Per-image metrics:", artifacts / "evaluation" / "per-image-metrics.csv")
print("Saved checkpoint:", saved_checkpoint)
print("Original video:", source_video)
print("Upright video:", upright_video)

display(Image.open(upright_frame))
display(Video(str(upright_video), embed=True, width=640))'''

    return [
        _cell("markdown", f"# {title}\n\n{description}\n\n"
              "Run on Kaggle with Internet and one GPU enabled. This notebook trains the Nerfstudio `instant-ngp` method from scratch for 30,000 iterations on the Garden COLMAP scene. Local files are source copies; GPU work runs on Kaggle.\n\n"
              "Outputs include the final checkpoint and config, training log and environment manifest, per-image and aggregate PSNR/SSIM/LPIPS, measured inference time and GPU memory, the number of field sample queries, and a novel-view spiral video. The query count means sampled 3D positions evaluated by the neural field, not network traffic."),
        _cell("code", setup),
        _cell("code", install),
        _cell("code", dataset),
        _cell("code", train),
        _cell("markdown", "## Evaluation and reusable evaluation script\n\nThe script evaluates every image in the interval hold-out split. It records PSNR, SSIM, LPIPS, render time, GPU memory and the actual number of sampled 3D positions passed through the Instant-NGP field. It exports aggregate and per-image CSV files plus a Markdown results table and side-by-side ground-truth/prediction images."),
        _cell("code", "%%writefile /kaggle/working/evaluate_experiment.py\n" + evaluator_source),
        _cell("code", eval_run),
        _cell("markdown", "## Novel-view inference video\n\nThe renderer synthesizes a spiral camera path around a held-out camera pose, then asks the trained model to render RGB frames from those camera poses. These camera poses are generated for inference and are not among the COLMAP training images."),
        _cell("code", "%%writefile /kaggle/working/render_novel_view.py\n" + renderer_source),
        _cell("code", render_run),
        _cell("markdown", "## Reproduction outputs\n\nKaggle saves files under `/kaggle/working` when you save a notebook version with outputs. The checkpoint is also copied into `experiment-artifacts/checkpoints` so it can be downloaded with the metrics, config and video."),
        _cell("code", show),
    ]


def _write_notebook(path: Path, title: str, description: str) -> None:
    cells = _build_cells(title, description)
    for index, cell in enumerate(cells):
        cell["id"] = f"cell-{index:03d}"
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def main() -> None:
    main_notebook = KERNEL / "instant-ngp-dhmt.ipynb"
    _write_notebook(
        main_notebook,
        "Nerfstudio Instant-NGP: full training on Kaggle",
        "Canonical Kaggle kernel for training the Garden scene from scratch, then evaluating and rendering novel views.",
    )


if __name__ == "__main__":
    main()
