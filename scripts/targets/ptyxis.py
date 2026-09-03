"""Ptyxis `.palette` file.

The 16 ANSI slots plus background/foreground/cursor and the titlebar pair in
Ptyxis's palette INI format. Ptyxis expects both [Light] and [Dark] sections,
so the same colour block is emitted twice — each flavor keeps its own
appearance under either.
"""

from __future__ import annotations

from scripts.palette import Palette, resolve_palette_path
from scripts.roles import ANSI_SLOTS, resolve_role
from scripts.variants import Flavor


def _scheme(palette: Palette) -> list[str]:
    """Build the shared `[Light]`/`[Dark]` colour block (Ptyxis wants both)."""
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


HEADER = """\
# {slug} — a Ptyxis palette from the Megadeth "Rust in Peace" cover palette.
# Generated from the src/ palettes by scripts/targets/ptyxis.py (just build-ports).
# Do not edit by hand: edit the palette and rebuild.
#
# The 16 ANSI slots plus background/foreground/cursor and the titlebar
# pair. [Light] and [Dark] share one block — this is a {appearance} theme
# under either appearance."""


def generate(flavor: Flavor) -> str:
    """Generate the Ptyxis `.palette` file for one flavor."""
    block = _scheme(flavor.palette)
    header = HEADER.format(slug=flavor.slug, appearance=flavor.appearance)
    return "\n".join(
        [
            header,
            "[Palette]",
            f"Name={flavor.label}",
            "",
            "[Light]",
            *block,
            "",
            "[Dark]",
            *block,
            "",
        ]
    )
