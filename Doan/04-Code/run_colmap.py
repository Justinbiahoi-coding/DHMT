"""Run COLMAP through nerfstudio and validate the generated pose model."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


def run(command: list[str]) -> None:
    print("$", " ".join(command))
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", type=Path, required=True, help="Raw image directory")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--camera-type", default="perspective")
    parser.add_argument("--quality-output", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    sparse = args.output_dir / "sparse" / "0"
    if sparse.is_dir() and not args.force:
        print(f"COLMAP model already exists: {sparse}")
    else:
        if args.force and args.output_dir.exists():
            shutil.rmtree(args.output_dir)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        run(
            [
                "ns-process-data",
                "images",
                "--data",
                str(args.images),
                "--output-dir",
                str(args.output_dir),
                "--camera-type",
                args.camera_type,
            ]
        )

    required = [sparse / name for name in ("cameras.bin", "images.bin", "points3D.bin")]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"COLMAP output is incomplete: {missing}")

    quality_output = args.quality_output or args.output_dir / "pose-quality.json"
    run(
        [
            "python",
            str(Path(__file__).with_name("check_pose_quality.py")),
            "--model",
            str(sparse),
            "--images",
            str(args.images),
            "--output",
            str(quality_output),
        ]
    )
    result = {"images": str(args.images), "output_dir": str(args.output_dir), "sparse_model": str(sparse)}
    report = args.output_dir / "colmap-run.json"
    report.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
