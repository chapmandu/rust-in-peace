"""Zellij KDL theme.

Emits the six-slot style block Zellij expects for every UI component, in its
`r g b` colour notation (0 = unset, inherit the terminal default). Chrome
follows VS Code's tab strip: inactive tabs sit flat on the sunken band with
muted comment-blue labels, the active one pops as a glow-green pill (the
green active-tab border), and the focused frame is the keyword tube blue.
Ribbons double as the status bar's mode and key-hint pills, so those wear
the same treatment.

Design: components are pure data — a dict of styles whose slots reference
palette paths — rendered by one small `_render`. TEXT/SELECTED are shared
bases for every plain-text, table, and list component. Ribbon slot semantics
come from zellij's tab-bar/status-bar plugin source: ribbon background/base
are the pill, unselected emphasis_1 is the hover/alternate-tab *background*,
emphasis_0 the shortcut character, emphasis_3 the bell-flash foreground.
"""

from __future__ import annotations

from scripts.palette import Palette, hex_to_rgb, resolve_palette_path
from scripts.roles import BLUE, GREEN, ORANGE, PURPLE, RED, TEAL, YELLOW
from scripts.variants import Flavor

# A Zellij colour value: a palette path (`syntax.info`), or 0 — Zellij's
# sentinel for "unset / inherit the terminal default".
type Ref = str | int

# The six-slot style block Zellij expects for every UI component.
type Style = dict[str, Ref]

# Primary foreground on the sunken bar chrome (as VS Code's tab strip), with
# the four emphasis accents in type / info / function / constant order.
TEXT: Style = {
    "base": "fg.base",
    "background": "bg.sunken",
    "emphasis_0": ORANGE,
    "emphasis_1": BLUE,
    "emphasis_2": GREEN,
    "emphasis_3": PURPLE,
}

# Selected rows: TEXT lifted onto the VS Code list-selection surface.
SELECTED: Style = {**TEXT, "background": "bg.selection"}

# UI-component styles, in file order.
COMPONENTS: dict[str, Style] = {
    "text_unselected": TEXT,
    "text_selected": SELECTED,
    # Active tab / active mode pill: VS Code's green active-tab accent.
    "ribbon_selected": {
        "base": "bg.base",  # navy text on the green pill
        "background": GREEN,  # glow green — as VS Code tab.activeBorderTop
        "emphasis_0": "ui.statusBar",  # shortcut char in the selected pill
        "emphasis_1": "bg.base",
        "emphasis_2": "bg.base",
        "emphasis_3": "ui.statusBar",  # bell-flash fg — must read on green
    },
    # Inactive tabs / key-hint pills: flat on the bar band, as VS Code's tab strip.
    "ribbon_unselected": {
        "base": "fg.comment",  # muted comment blue — quiet inactive labels
        "background": "bg.panel",  # as VS Code tab.inactiveBackground
        "emphasis_0": YELLOW,  # gold shortcut chars
        "emphasis_1": "bg.surface",  # hover / alternate-tab background — a subtle lift
        "emphasis_2": "fg.muted",
        "emphasis_3": RED,  # bell-flash fg
    },
    "table_title": {
        "base": BLUE,
        "background": 0,
        "emphasis_0": ORANGE,
        "emphasis_1": BLUE,
        "emphasis_2": GREEN,
        "emphasis_3": PURPLE,
    },
    "table_cell_selected": SELECTED,
    "table_cell_unselected": TEXT,
    "list_selected": SELECTED,
    "list_unselected": TEXT,
    "frame_selected": {
        "base": TEAL,
        "background": 0,
        "emphasis_0": ORANGE,
        "emphasis_1": BLUE,
        "emphasis_2": PURPLE,
        "emphasis_3": 0,
    },
    "frame_unselected": {
        "base": "fg.comment",  # muted UI-line blue, as VS Code's focusBorder family
        "background": 0,
        "emphasis_0": ORANGE,
        "emphasis_1": BLUE,
        "emphasis_2": PURPLE,
        "emphasis_3": PURPLE,
    },
    "frame_highlight": {
        "base": ORANGE,
        "background": 0,
        "emphasis_0": PURPLE,
        "emphasis_1": ORANGE,
        "emphasis_2": ORANGE,
        "emphasis_3": ORANGE,
    },
    "exit_code_success": {
        "base": GREEN,
        "background": 0,
        "emphasis_0": BLUE,
        "emphasis_1": "bg.surface",
        "emphasis_2": PURPLE,
        "emphasis_3": "fg.comment",
    },
    "exit_code_error": {
        "base": RED,
        "background": 0,
        "emphasis_0": YELLOW,
        "emphasis_1": 0,
        "emphasis_2": 0,
        "emphasis_3": 0,
    },
}

# The ten multiplayer cursor colours, in slot order (0 = no colour).
MULTIPLAYER: list[Ref] = [
    PURPLE,  # player_1
    BLUE,  # player_2
    0,  # player_3
    YELLOW,  # player_4
    GREEN,  # player_5
    0,  # player_6
    RED,  # player_7
    0,  # player_8
    0,  # player_9
    0,  # player_10
]

HEADER = """\
// {slug} — a Zellij theme from the Megadeth "Rust in Peace" cover palette.
// Generated from the src/ palettes by scripts/targets/zellij.py (just build-ports).
// Do not edit by hand: edit the palette and rebuild.
//
// Chrome follows VS Code's tab strip: inactive tabs sit flat on the sunken
// band with muted comment-blue labels, the active tab (and the status bar's
// mode pill) pops as a glow-green pill — VS Code's green active-tab border —
// and the focused frame is the keyword tube blue. Colours are `r g b`; 0
// means unset, inheriting the terminal default. Every colour tracks the
// shared palette; the unfocused frame wears VS Code's muted UI-line comment
// blue."""


def _render(palette: Palette, ref: Ref) -> str:
    """Render a Ref to a Zellij colour token: `r g b`, or `0` for the sentinel."""
    if ref == 0:
        return "0"
    assert isinstance(ref, str)  # noqa: S101 — narrows the Ref union for mypy
    return " ".join(str(channel) for channel in hex_to_rgb(resolve_palette_path(palette, ref)))


def generate(flavor: Flavor) -> str:
    """Generate the Zellij KDL theme for one flavor."""
    palette = flavor.palette
    indent = "    "

    component_lines = []
    for name, style in COMPONENTS.items():
        component_lines.append(f"{indent * 2}{name} {{")
        component_lines += [
            f"{indent * 3}{slot} {_render(palette, ref)}" for slot, ref in style.items()
        ]
        component_lines.append(f"{indent * 2}}}")

    multiplayer_lines = [
        f"{indent * 2}multiplayer_user_colors {{",
        *(
            f"{indent * 3}player_{i + 1} {_render(palette, ref)}"
            for i, ref in enumerate(MULTIPLAYER)
        ),
        f"{indent * 2}}}",
    ]

    return "\n".join(
        [
            HEADER.format(slug=flavor.slug),
            "themes {",
            f"{indent}{flavor.slug} {{",
            *component_lines,
            *multiplayer_lines,
            f"{indent}}}",
            "}",
            "",
        ]
    )
