"""Write dist/*.json for every flavor, then refresh the README art."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from scripts.generate import Theme, generate
from scripts.palette import REPO_ROOT
from scripts.readme import build_readme

DIST_DIR = REPO_ROOT / "dist"


def write_theme(path: Path, theme: Theme) -> None:
    """Write a theme as pretty-printed JSON."""
    path.write_text(json.dumps(theme, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    """Build the VS Code theme JSONs, then refresh the README's art and sections."""
    shutil.rmtree(DIST_DIR, ignore_errors=True)
    DIST_DIR.mkdir()

    for flavor, theme in generate():
        write_theme(DIST_DIR / f"{flavor.slug}.json", theme)

    build_readme()


if __name__ == "__main__":
    main()
