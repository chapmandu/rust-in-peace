"""Ptyxis `.palette` file.

The 16 ANSI slots plus background/foreground/cursor and the titlebar pair in
Ptyxis's palette INI format. Each flavor is one appearance, so the file is a
single-scheme palette: colours live under `[Palette]` and `[Light]`/`[Dark]`
are omitted.
"""

from __future__ import annotations

from scripts.palette import Palette, resolve_palette_path
from scripts.roles import ANSI_SLOTS, resolve_role
from scripts.variants import Flavor


def _scheme(palette: Palette) -> list[str]:
    """Build the single-scheme colour block under `[Palette]`."""
    return [
        f"Background={resolve_palette_path(palette, 'bg.base')}",
        f"Foreground={resolve_palette_path(palette, 'fg.base')}",
        f"Cursor={resolve_palette_path(palette, 'fg.base')}",
        # Without these Ptyxis derives its own headerbar shade from the
        # background; pin the tab strip to the shared chrome band instead.
        f"TitlebarBackground={resolve_palette_path(palette, 'bg.chrome')}",
        f"TitlebarForeground={resolve_palette_path(palette, 'fg.base')}",
        *(f"Color{i}={resolve_role(palette, f'ansi.{slot}')}" for i, slot in enumerate(ANSI_SLOTS)),
    ]


HEADER = "# {slug} — generated; do not edit. Rebuild via `just build-ports`."


def generate(flavor: Flavor) -> str:
    """Generate the Ptyxis `.palette` file for one flavor."""
    return "\n".join(
        [
            HEADER.format(slug=flavor.slug),
            "[Palette]",
            f"Name={flavor.label}",
            *_scheme(flavor.palette),
            "",
        ]
    )
