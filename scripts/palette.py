"""Load src/ palette JSON and resolve dotted colour paths."""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"

type Palette = dict[str, str | Palette]
"""Nested palette of semantic colour groups, e.g. palette["syntax"]["keyword"]."""

_HEX_RE = re.compile(r"#?([0-9a-fA-F]{6})")


def load_palette(file: str = "palette.json") -> Palette:
    """Load and parse a palette from src/ (the dark palette by default)."""
    palette: Palette = json.loads((SRC_DIR / file).read_text(encoding="utf-8"))
    return palette


def palette_paths(palette: Palette, prefix: str = "") -> list[str]:
    """Flatten a palette to its dotted colour paths, e.g. `syntax.keyword`."""
    paths: list[str] = []
    for key, value in palette.items():
        if isinstance(value, str):
            paths.append(f"{prefix}{key}")
        else:
            paths.extend(palette_paths(value, f"{prefix}{key}."))
    return paths


def resolve_palette_path(palette: Palette, path: str) -> str:
    """Resolve a dotted path such as `syntax.keyword` to a colour in the palette."""
    node: str | Palette | None = palette
    for key in path.split("."):
        node = node.get(key) if isinstance(node, dict) else None
    if not isinstance(node, str):
        raise ValueError(f'palette has no colour at path "{path}"')
    return node


def hex_to_rgb(hex_colour: str) -> tuple[int, int, int]:
    """Convert a `#rrggbb` hex colour to an (r, g, b) triple of 0–255 integers."""
    match = _HEX_RE.fullmatch(hex_colour)
    if not match:
        raise ValueError(f'not a 6-digit hex colour: "{hex_colour}"')
    value = int(match.group(1), 16)
    return (value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF
