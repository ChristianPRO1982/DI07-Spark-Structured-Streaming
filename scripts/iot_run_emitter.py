"""
Move JSON files from init to landing with random timing to simulate an IoT stream.
"""

from __future__ import annotations

import argparse
import logging
import random
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RunConfig:
    init_dir: Path
    landing_dir: Path
    min_delay_s: float
    max_delay_s: float
    batch_min: int
    batch_max: int
    shuffle: bool


def build_logger() -> logging.Logger:
    """Create a configured logger."""
    logger = logging.getLogger("iot_run_emitter")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def parse_args() -> RunConfig:
    """Parse CLI arguments into a RunConfig."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--init-dir", required=True)
    parser.add_argument("--landing-dir", required=True)
    parser.add_argument("--min-delay-s", type=float, default=0.1)
    parser.add_argument("--max-delay-s", type=float, default=30.0)
    parser.add_argument("--batch-min", type=int, default=1)
    parser.add_argument("--batch-max", type=int, default=10)
    parser.add_argument("--shuffle", action="store_true")
    args = parser.parse_args()

    if args.batch_min < 1 or args.batch_max < args.batch_min:
        raise SystemExit("Invalid batch range: batch-min must be >= 1 and batch-max >= batch-min")

    if args.min_delay_s < 0 or args.max_delay_s < args.min_delay_s:
        raise SystemExit("Invalid delay range: min-delay-s must be >= 0 and max-delay-s >= min-delay-s")

    return RunConfig(
        init_dir=Path(args.init_dir),
        landing_dir=Path(args.landing_dir),
        min_delay_s=args.min_delay_s,
        max_delay_s=args.max_delay_s,
        batch_min=args.batch_min,
        batch_max=args.batch_max,
        shuffle=args.shuffle,
    )


def list_init_files(init_dir: Path) -> list[Path]:
    """List JSON files currently available in init."""
    return sorted([p for p in init_dir.iterdir() if p.is_file() and p.suffix.lower() == ".json"])


def pick_batch(files: list[Path], cfg: RunConfig) -> list[Path]:
    """Pick the next batch of files to move."""
    if not files:
        return []

    batch_size = min(len(files), random.randint(cfg.batch_min, cfg.batch_max))

    if cfg.shuffle:
        random.shuffle(files)
        return files[:batch_size]

    return files[:batch_size]


def move_atomically(src: Path, dst: Path) -> None:
    """Move a file by renaming into landing (atomic if same filesystem)."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    src.replace(dst)


def main() -> None:
    """Program entrypoint."""
    cfg = parse_args()
    logger = build_logger()

    if not cfg.init_dir.exists():
        raise SystemExit(f"Init directory does not exist: {cfg.init_dir}")

    cfg.landing_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Starting emitter: %s -> %s", cfg.init_dir, cfg.landing_dir)

    while True:
        files = list_init_files(cfg.init_dir)
        if not files:
            logger.info("No more files in init. Done.")
            break

        batch = pick_batch(files, cfg)
        delay = random.uniform(cfg.min_delay_s, cfg.max_delay_s)
        time.sleep(delay)

        timestamp_ms = int(time.time() * 1000)
        for src in batch:
            dst_name = f"{src.stem}__{timestamp_ms}{src.suffix}"
            move_atomically(src, cfg.landing_dir / dst_name)

        logger.info(
            "Moved %d file(s) after %.2fs | remaining in init: %d",
            len(batch),
            delay,
            len(files) - len(batch),
        )


if __name__ == "__main__":
    main()
