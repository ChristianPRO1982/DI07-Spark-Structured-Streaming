"""
Reset and seed the init folder from an immutable source dataset.
"""

from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class InitConfig:
    source_dir: Path
    init_dir: Path
    landing_dir: Path
    pattern: str


def parse_args() -> InitConfig:
    """Parse CLI arguments into an InitConfig."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--init-dir", required=True)
    parser.add_argument("--landing-dir", required=True)
    parser.add_argument("--pattern", default="*.json")
    args = parser.parse_args()

    return InitConfig(
        source_dir=Path(args.source_dir),
        init_dir=Path(args.init_dir),
        landing_dir=Path(args.landing_dir),
        pattern=args.pattern,
    )


def ensure_empty_dir(path: Path) -> None:
    """Ensure a directory exists and remove all files except .gitkeep."""
    path.mkdir(parents=True, exist_ok=True)

    for item in path.iterdir():
        if item.name == ".gitkeep":
            continue

        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)



def copy_dataset(cfg: InitConfig) -> int:
    """Copy dataset files from source to init."""
    files = sorted(cfg.source_dir.glob(cfg.pattern))
    if not files:
        raise SystemExit(f"No files found in {cfg.source_dir} with pattern {cfg.pattern}")

    for f in files:
        shutil.copy2(f, cfg.init_dir / f.name)

    return len(files)


def main() -> None:
    """Program entrypoint."""
    cfg = parse_args()

    if not cfg.source_dir.exists():
        raise SystemExit(f"Source directory does not exist: {cfg.source_dir}")

    ensure_empty_dir(cfg.init_dir)
    ensure_empty_dir(cfg.landing_dir)

    count = copy_dataset(cfg)
    print(f"Seeded init with {count} files from {cfg.source_dir}")


if __name__ == "__main__":
    main()
