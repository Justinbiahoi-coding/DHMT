"""Render a spiral video from camera poses synthesized around the held-out scene."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True, help="Nerfstudio run's config.yml")
    parser.add_argument("--output", type=Path, required=True, help="Output MP4 path")
    parser.add_argument("--seconds", type=float, default=8.0)
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--radius", type=float, default=0.1)
    parser.add_argument("--downscale-factor", type=float, default=2.0)
    args = parser.parse_args()

    if not args.config.is_file():
        parser.error(f"Config not found: {args.config}")
    if args.seconds <= 0 or args.fps <= 0 or args.radius <= 0 or args.downscale_factor < 1:
        parser.error("seconds, fps, radius must be positive and downscale-factor must be >= 1")
    args.output.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "ns-render",
        "spiral",
        "--load-config",
        str(args.config.resolve()),
        "--output-path",
        str(args.output.resolve()),
        "--seconds",
        str(args.seconds),
        "--frame-rate",
        str(args.fps),
        "--radius",
        str(args.radius),
        "--downscale-factor",
        str(args.downscale_factor),
        "--output-format",
        "video",
        "--rendered-output-names",
        "rgb",
    ]
    log_path = args.output.with_suffix(".log")
    started = time.perf_counter()
    print("Rendering synthetic camera trajectory:", " ".join(command), flush=True)
    with log_path.open("w", encoding="utf-8") as log_file:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="", flush=True)
            log_file.write(line)
            log_file.flush()
        return_code = process.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, command)
    if not args.output.is_file() or args.output.stat().st_size == 0:
        raise RuntimeError(f"Renderer exited without creating a video: {args.output}")

    still_path = args.output.with_name(f"{args.output.stem}_frame.png")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            str(args.seconds / 4),
            "-i",
            str(args.output.resolve()),
            "-frames:v",
            "1",
            str(still_path.resolve()),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    if not still_path.is_file() or still_path.stat().st_size == 0:
        raise RuntimeError(f"ffmpeg did not create the example frame: {still_path}")

    manifest = {
        "video": str(args.output.resolve()),
        "example_novel_view_image": str(still_path.resolve()),
        "config": str(args.config.resolve()),
        "trajectory": "Nerfstudio spiral path synthesized from a held-out camera pose",
        "seconds": args.seconds,
        "fps": args.fps,
        "frames": int(args.seconds * args.fps),
        "radius": args.radius,
        "downscale_factor": args.downscale_factor,
        "render_seconds": time.perf_counter() - started,
        "size_bytes": args.output.stat().st_size,
        "command": command,
    }
    args.output.with_suffix(".json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("Video written:", args.output, flush=True)


if __name__ == "__main__":
    main()
