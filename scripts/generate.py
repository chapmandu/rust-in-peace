"""Resolve src/rust-in-peace.yml placeholders against a flavor palette.

Role names go through scripts/roles.py; dotted paths hit the palette.
`!alpha [colour, aa]` covers anchor-aliased cases. Null colours are stripped.
"""

from __future__ import annotations

import re
from typing import Any

import yaml

from scripts.palette import SRC_DIR, Palette, resolve_palette_path
from scripts.roles import ROLES
from scripts.variants import Flavor, flavors

type Theme = dict[str, Any]
"""A parsed VS Code colour theme (name, type, colors, tokenColors, ...)."""

_PLACEHOLDER_RE = re.compile(r"\{\{\s*([\w.]+)\s*\}\}")

# Keys that belong in a VS Code colour theme. Everything else in the YAML
# (anchors dump, $schema, leftover source metadata) is dropped before the
# JSON is written.
_THEME_KEYS = ("semanticHighlighting", "colors", "tokenColors")


class ThemeLoader(yaml.SafeLoader):
    """SafeLoader extended with the theme source's custom tags."""


def _alpha(loader: yaml.SafeLoader, node: yaml.SequenceNode) -> str:
    """`!alpha [hexRGB, alpha]`: concatenate a hex colour and a 2-hex alpha suffix."""
    hex_rgb, alpha = loader.construct_sequence(node)
    return f"{hex_rgb}{alpha}"


ThemeLoader.add_constructor("!alpha", _alpha)


def apply_palette(source: str, palette: Palette) -> str:
    """Substitute `{{group.key}}` / `{{role}}` placeholders with palette colours.

    Role names from scripts/roles.py win; anything else is a dotted palette
    path. Any trailing characters (e.g. a 2-hex alpha suffix) are preserved.
    """

    def replacer(match: re.Match[str]) -> str:
        key = match.group(1)
        role = ROLES.get(key)
        path = role.path if role is not None else key
        return resolve_palette_path(palette, path)

    return _PLACEHOLDER_RE.sub(replacer, source)


def build_theme(theme_yaml: str, palette: Palette) -> Theme:
    """Substitute a palette into the YAML source and parse it into a theme."""
    theme: Theme = yaml.load(
        apply_palette(theme_yaml, palette),
        Loader=ThemeLoader,  # noqa: S506 — ThemeLoader subclasses SafeLoader
    )
    # Colours mapped to null (or empty) fall through to VS Code's defaults.
    theme["colors"] = {key: value for key, value in theme["colors"].items() if value}
    return {key: theme[key] for key in _THEME_KEYS if key in theme}


def generate() -> list[tuple[Flavor, Theme]]:
    """Build every theme flavor by resolving the YAML mapping against its palette."""
    theme_yaml = (SRC_DIR / "rust-in-peace.yml").read_text(encoding="utf-8")

    themes: list[tuple[Flavor, Theme]] = []
    for flavor in flavors():
        theme: Theme = {
            "name": flavor.label,
            "type": flavor.appearance,
            **build_theme(theme_yaml, flavor.palette),
        }
        themes.append((flavor, theme))
    return themes
