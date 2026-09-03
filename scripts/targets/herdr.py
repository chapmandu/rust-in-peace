"""herdr theme config fragment.

Recolours herdr's tokyo-night base theme (tokyo-night-day for the light
flavor) to the album palette through the [theme.custom] override tokens —
herdr requires a base theme name, and every token it exposes is overridden
here; any it later adds falls through to the base. The primary accent is the
cover's electric tube blue, matching the Zellij tuning, and panel_bg takes
VS Code's tab-strip chrome, sitting sunken below content.

Design: one Token table maps herdr's vocabulary onto palette paths, each with
an inline note that lands in the generated file as a comment.
"""

from __future__ import annotations

from dataclasses import dataclass

from scripts.palette import resolve_palette_path
from scripts.roles import BLUE, GREEN, ORANGE, PURPLE, RED, TEAL, YELLOW, role_path
from scripts.variants import Flavor


@dataclass(frozen=True)
class Token:
    """A herdr override token mapped to a palette path, with an optional note."""

    name: str
    ref: str
    comment: str | None = None


# Order follows herdr's own struct.
TOKENS = [
    Token("accent", TEAL, "primary accent — tube blue, the theme signature"),
    Token("panel_bg", "bg.chrome", "tab + status bar band — VS Code's tab-strip chrome"),
    Token("surface0", "bg.overlay", "raised surface — selected rows, inactive tab chips"),
    Token("surface1", "ui.button", "highest surface — VS Code button blue"),
    Token("surface_dim", "bg.surface", "base surface — active row, dividers, seams"),
    Token("overlay0", "fg.comment", "muted UI lines, borders"),
    Token("overlay1", "fg.muted", "brighter UI lines"),
    Token("text", "fg.base", "primary text"),
    Token("subtext0", "fg.muted", "secondary text"),
    Token("mauve", PURPLE, "softened violet — constants"),
    Token("green", GREEN, "glowing hand green"),
    Token("yellow", YELLOW, "logo gold"),
    Token("red", RED, "rust / logo-edge red"),
    Token("blue", BLUE, "bright tube blue"),
    Token("teal", role_path("builtin"), "sky cyan"),
    Token("peach", ORANGE, "logo orange"),
]

HEADER = """\
# {slug} — a herdr theme from the Megadeth "Rust in Peace" cover palette.
# Generated from the src/ palettes by scripts/targets/herdr.py (just build-ports).
# Do not edit by hand: edit the palette and rebuild.
# Merge this into your herdr config: https://herdr.dev/docs/configuration/#theme
#
# Recolours the {base} base theme via [theme.custom] overrides; any token
# not set here falls through to {base}. The accent is the cover's electric
# tube blue (the theme signature); panel_bg takes VS Code's tab-strip
# chrome, sitting sunken below content.
# Tip: set panel_bg = "reset" to let panels follow your terminal background.
# Note: [theme.custom] is a single global block, so herdr's appearance
# auto-switch ([theme] dark_name/light_name) can't pair two flavors — merge
# the overrides of just one."""


def generate(flavor: Flavor) -> str:
    """Generate the herdr theme config fragment for one flavor."""
    base = "tokyo-night-day" if flavor.appearance == "light" else "tokyo-night"
    width = max(len(token.name) for token in TOKENS)

    lines = []
    for token in TOKENS:
        hex_colour = resolve_palette_path(flavor.palette, token.ref)
        line = f'{token.name.ljust(width)} = "{hex_colour}"'
        lines.append(f"{line} # {token.comment}" if token.comment else line)

    return "\n".join(
        [
            HEADER.format(slug=flavor.slug, base=base),
            "",
            "[theme]",
            f'name = "{base}"',
            "",
            "[theme.custom]",
            *lines,
            "",
        ]
    )
