"""Shared semantic role table.

Extracted from the VS Code YAML anchors in ``src/rust-in-peace.yml``. Every
generator — ``scripts/generate.py`` and ``scripts/targets/*`` — resolves
editor-facing roles through this table so a palette edit cannot make Helix,
Zed, and VS Code drift on what "modified", "info", "builtin", or
"variable.builtin" mean.

Design: colour names (``CYAN``, ``YELLOW``, ``BLUE``, …) are the YAML
anchors. Roles record how those anchors are used in the YAML —
``gitDecoration.modified`` and ``editorInfo`` both use ``CYAN``, this/self
uses ``YELLOW`` italic — and ``resolve_role`` turns a role name into a hex
against a flavor's palette. ``apply_palette`` in generate.py also accepts
role names as placeholders (``{{builtin}}``), so the VS Code mapping itself
goes through this table.

The diagnostic ``info`` role is ``CYAN`` (``syntax.builtin``), not ``BLUE``
(``syntax.info``). That matches ``editorInfo.foreground`` in the YAML.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from scripts.palette import Palette, resolve_palette_path

# YAML colour anchors (src/rust-in-peace.yml rustInPeace.base).
COMMENT: Final = "fg.comment"
CYAN: Final = "syntax.builtin"
BLUE: Final = "syntax.info"
TEAL: Final = "syntax.keyword"
GREEN: Final = "syntax.function"
YELLOW: Final = "syntax.string"
ORANGE: Final = "syntax.type"
RED: Final = "syntax.error"
PURPLE: Final = "syntax.constant"

# The 16 ANSI slots, in Color0..Color15 / COLOR0..COLOR15 order.
ANSI_SLOTS: Final[tuple[str, ...]] = (
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white",
    "brightBlack",
    "brightRed",
    "brightGreen",
    "brightYellow",
    "brightBlue",
    "brightMagenta",
    "brightCyan",
    "brightWhite",
)


@dataclass(frozen=True)
class Role:
    """An editor-facing semantic role: a palette path and optional italic."""

    path: str
    italic: bool = False


ROLES: Final[dict[str, Role]] = {
    "keyword": Role(TEAL),
    "builtin": Role(CYAN, italic=True),  # Language Built-ins (`support`)
    "function": Role(GREEN),
    "string": Role(YELLOW),
    "type": Role(ORANGE),
    "error": Role(RED),
    "constant": Role(PURPLE),
    # gitDecoration.modifiedResourceForeground / editorGutter.modified
    "modified": Role(CYAN),
    # editorInfo.foreground — not BLUE / syntax.info
    "info": Role(CYAN),
    # support.function keeps CYAN, drops italic
    "function.builtin": Role(CYAN),
    # this, super, self (`variable.language`)
    "variable.builtin": Role(YELLOW, italic=True),
    **{f"ansi.{slot}": Role(f"ansi.{slot}") for slot in ANSI_SLOTS},
}


def role_path(name: str) -> str:
    """Return the palette path a role resolves through."""
    try:
        return ROLES[name].path
    except KeyError:
        raise ValueError(f'unknown role "{name}"') from None


def resolve_role(palette: Palette, name: str) -> str:
    """Resolve a role name to a hex colour in the given palette."""
    return resolve_palette_path(palette, role_path(name))
