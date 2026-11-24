# Instant-NGP experiment files

## Kaggle execution

`kaggle-kernel/instant-ngp-dhmt.ipynb` is the single canonical Kaggle notebook for `nminhkhoa24120073/instant-ngp-dhmt`. It trains Nerfstudio `instant-ngp` from scratch for 30,000 iterations with seed 42 on the Garden COLMAP dataset, then evaluates the saved model and renders novel views. It pins Nerfstudio to commit `50e0e3c70c775e89333256213363badbf074f29d` and tiny-cuda-nn to `v2.0`. The dataset cell validates that `images_8` has the same filenames and 1/8 dimensions as the COLMAP model; training configures Nerfstudio to scale camera intrinsics by 8. Enable Internet and one GPU, then run the cells in order.

The notebook creates `/kaggle/working/experiment-artifacts/` containing:

- `checkpoints/step-000029999.ckpt` and `config.yml` - trained model weights and load configuration. Nerfstudio numbers the 30,000 iterations from step 0, so the last saved step is 29,999.
- `run-metadata.json`, `pip-freeze.txt`, and `training.log` - training time, command, dependency commits, dataset fingerprint, GPU/driver, and runtime details.
- `evaluation/metrics.json`, `metrics.csv`, `metrics.md`, and `per-image-metrics.csv` - PSNR, SSIM, LPIPS, inference time, throughput, GPU memory, and sampled neural-field queries.
- `evaluation/comparisons/` - held-out ground-truth and rendered image pairs.
- `novel_view_spiral.mp4`, `novel_view_spiral_frame.png`, `novel_view_spiral_upright.mp4`, `novel_view_spiral_upright_frame.png`, and JSON/log sidecars - rendered inference frames from a synthesized camera path, the 180-degree upright-rotated version, and extracted novel-view images.

`field_sample_queries_total` counts the sampled 3D positions passed through the Instant-NGP neural field at inference time. It is an algorithmic query count, not Internet traffic or a FLOP count.

## Scripts and notebook sync

- `build_experiment_notebooks.py` regenerates `kaggle-kernel/instant-ngp-dhmt.ipynb` by embedding `evaluate_experiment.py` and `render_novel_view.py` via `%%writefile`.
- `evaluate_experiment.py` evaluates every image in the held-out COLMAP interval split and exports aggregate and per-image tables.
- `render_novel_view.py` invokes Nerfstudio's spiral renderer and writes an MP4 plus a run manifest.
- `run_colmap.py` and `check_pose_quality.py` run COLMAP via Nerfstudio and report registration/reprojection quality on local datasets.

Both evaluation and render scripts run inside the Kaggle Nerfstudio environment; they are not intended to train on the local machine. Create a new Kaggle version without starting a GPU run from the repository root with:

```powershell
$env:PYTHONPATH = (Resolve-Path '.kaggle-cli').Path
$env:KAGGLE_CONFIG_DIR = 'C:\Users\Administrator\.kaggle'
.\.venv-kaggle\Scripts\python.exe -m kaggle kernels push -p 04-Code/kaggle-kernel --no-run
```

The `--no-run` option only saves the new version; start it manually from Kaggle when ready. Note that `build_experiment_notebooks.py` regenerates a clean source-only notebook (`outputs: []`). To pull the executed notebook **with cell outputs** (`__notebook__.ipynb`) from Kaggle version `<N>`, use `ApiDownloadKernelOutputRequest(owner_slug="nminhkhoa24120073", kernel_slug="instant-ngp-dhmt", version_number=<N>, file_path="__notebook__.ipynb")` via `.kaggle-cli` / `kagglesdk`.
