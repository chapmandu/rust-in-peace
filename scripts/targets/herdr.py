"""herdr theme config fragment.

Recolours herdr's tokyo-night base theme (tokyo-night-day for the light
flavor) to the album palette through the [theme.custom] override tokens —
herdr requires a base theme name. The primary accent is the cover's electric
tube blue, matching the Zellij tuning, and panel_bg takes VS Code's tab-strip
chrome, sitting sunken below content.

Design: one Token table maps herdr's vocabulary onto palette paths.
"""

from __future__ import annotations

from dataclasses import dataclass

from scripts.palette import resolve_palette_path
from scripts.roles import BLUE, GREEN, ORANGE, PURPLE, RED, TEAL, YELLOW, role_path
from scripts.variants import Flavor


@dataclass(frozen=True)
class Token:
    """A herdr override token mapped to a palette path."""

    name: str
    ref: str


# Order follows herdr's own struct.
TOKENS = [
    Token("accent", TEAL),
    Token("panel_bg", "bg.chrome"),
    Token("surface0", "bg.overlay"),
    Token("surface1", "ui.button"),
    Token("surface_dim", "bg.surface"),
    Token("overlay0", "fg.comment"),
    Token("overlay1", "fg.muted"),
    Token("text", "fg.base"),
    Token("subtext0", "fg.muted"),
    Token("mauve", PURPLE),
    Token("green", GREEN),
    Token("yellow", YELLOW),
    Token("red", RED),
    Token("blue", BLUE),
    Token("teal", role_path("builtin")),
    Token("peach", ORANGE),
]

HEADER = "# {slug} — generated; do not edit. Rebuild via `just build-ports`."


def generate(flavor: Flavor) -> str:
    """Generate the herdr theme config fragment for one flavor."""
    base = "tokyo-night-day" if flavor.appearance == "light" else "tokyo-night"
    width = max(len(token.name) for token in TOKENS)

    lines = [
        f'{token.name.ljust(width)} = "{resolve_palette_path(flavor.palette, token.ref)}"'
        for token in TOKENS
    ]

    return "\n".join(
        [
            HEADER.format(slug=flavor.slug),
            "",
            "[theme]",
            f'name = "{base}"',
            "",
            "[theme.custom]",
            *lines,
            "",
        ]
    )
