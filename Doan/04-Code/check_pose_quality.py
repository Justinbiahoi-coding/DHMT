"""Export a COLMAP model to text and report registration and reprojection quality."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import subprocess
import tempfile
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, required=True, help="COLMAP sparse/0 directory")
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("pose-quality.json"))
    args = parser.parse_args()

    for name in ("cameras.bin", "images.bin", "points3D.bin"):
        if not (args.model / name).is_file():
            raise FileNotFoundError(f"Missing COLMAP file: {args.model / name}")

    with tempfile.TemporaryDirectory(prefix="colmap-text-") as directory:
        text_model = Path(directory)
        subprocess.run(
            [
                "colmap",
                "model_converter",
                "--input_path",
                str(args.model),
                "--output_path",
                str(text_model),
                "--output_type",
                "TXT",
            ],
            check=True,
        )
        image_lines = (text_model / "images.txt").read_text(encoding="utf-8").splitlines()
        point_lines = (text_model / "points3D.txt").read_text(encoding="utf-8").splitlines()

    registered = [
        line for line in image_lines if line and not line.startswith("#") and len(line.split()) >= 10
    ][::2]
    errors = []
    for line in point_lines:
        if line and not line.startswith("#"):
            fields = line.split()
            if len(fields) >= 8:
                error = float(fields[7])
                if math.isfinite(error):
                    errors.append(error)

    image_count = sum(1 for path in args.images.iterdir() if path.is_file())
    report = {
        "image_count": image_count,
        "registered_image_count": len(registered),
        "registration_ratio": len(registered) / image_count if image_count else 0.0,
        "point_count": len(errors),
        "reprojection_error_mean_px": statistics.fmean(errors) if errors else None,
        "reprojection_error_median_px": statistics.median(errors) if errors else None,
    }
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
