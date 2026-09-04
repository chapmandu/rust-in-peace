"""Helix TOML theme.

A standalone theme (no `inherits`): syntax, markup, diagnostics, and the
full UI layer are all defined here, recoloured to the album palette and
mirroring the VS Code theme's token philosophy.

Design: the output has two layers. The ROLES block is static text — theme
roles reference palette *names* ("aqua", "orange"), so it never changes with
the source palette. The [palette] block beneath it defines those names, and
every one derives from the shared role table (scripts/roles.py) or a mix
formula over palette anchors (scripts/color.py). Diff and diagnostic slots
take the VS Code theme's colour for the equivalent UI element.
"""

from __future__ import annotations

from dataclasses import dataclass

from scripts.color import ColorFn, mixed
from scripts.palette import resolve_palette_path
from scripts.roles import BLUE, GREEN, ORANGE, PURPLE, RED, TEAL, YELLOW, Role, role_path
from scripts.roles import ROLES as THEME_ROLES
from scripts.variants import Flavor


def _scope_style(palette_name: str, role: Role) -> str:
    """Render a Helix `{ fg = "name", ... }` style from a shared role."""
    parts = [f'fg = "{palette_name}"']
    if role.italic:
        parts.append('modifiers = ["italic"]')
    return "{ " + ", ".join(parts) + " }"


# function.builtin / variable.builtin are driven by the shared role table so
# italic and colour stay aligned with VS Code (support.function / this/self).
_FN_BUILTIN = f'"function.builtin" = {_scope_style("cyan", THEME_ROLES["function.builtin"])}'
_VAR_BUILTIN = (
    f'"variable.builtin" = {_scope_style("variable-builtin", THEME_ROLES["variable.builtin"])}'
)

# Static: roles reference the palette names defined in the [palette] block below.
ROLES = (
    """\
keyword = { fg = "aqua" }
operator = { fg = "aqua" }
punctuation = { fg = "fg" }
"punctuation.delimiter" = { fg = "aqua" }
tag = { fg = "aqua" }
special = { fg = "aqua" }
"constant.character.escape" = { fg = "aqua" }

function = { fg = "light-green" }
"""
    + _FN_BUILTIN
    + """
"function.special" = { fg = "cyan" }
attribute = { fg = "light-green", modifiers = ["italic"] }

string = { fg = "yellow" }
"string.special" = { fg = "aqua" }
"constant.character" = { fg = "yellow" }

type = { fg = "orange", modifiers = ["italic"] }
"type.enum.variant" = { fg = "orange" }
constructor = { fg = "orange" }
"variable.parameter" = { fg = "orange", modifiers = ["italic"] }

constant = { fg = "purple" }
variable = { fg = "fg" }
"""
    + _VAR_BUILTIN
    + """
label = { fg = "blue" }
namespace = { fg = "fg" }

comment = { fg = "comment", modifiers = ["italic"] }

"markup.bold" = { modifiers = ["bold"] }
"markup.italic" = { modifiers = ["italic"] }
"markup.strikethrough" = { modifiers = ["crossed_out"] }
"markup.heading" = { fg = "purple", modifiers = ["bold"] }
"markup.heading.completion" = { bg = "bg-menu", fg = "fg" }
"markup.heading.hover" = { bg = "fg-selected" }
"markup.link" = { fg = "cyan", underline = { style = "line" } }
"markup.link.label" = { fg = "teal" }
"markup.link.text" = { fg = "teal" }
"markup.link.url" = { underline = { style = "line" } }
"markup.list" = { fg = "cyan" }
"markup.normal.completion" = { fg = "comment" }
"markup.normal.hover" = { fg = "fg-dark" }
"markup.raw" = { fg = "light-green" }
"markup.raw.inline" = { bg = "black", fg = "blue" }
"markup.quote" = { fg = "yellow", modifiers = ["italic"] }

"diff.plus" = { fg = "add" }
"diff.minus" = { fg = "delete" }
"diff.delta" = { fg = "change" }
"diff.delta.moved" = { fg = "blue" }

error = { fg = "error" }
warning = { fg = "orange" }
info = { fg = "info" }
hint = { fg = "hint" }
"diagnostic.error" = { underline = { style = "curl", color = "error" } }
"diagnostic.warning" = { underline = { style = "curl", color = "orange" } }
"diagnostic.info" = { underline = { style = "curl", color = "info" } }
"diagnostic.hint" = { underline = { style = "curl", color = "hint" } }
"diagnostic.unnecessary" = { modifiers = ["dim"] }
"diagnostic.deprecated" = { modifiers = ["crossed_out"] }

"ui.background" = { bg = "bg", fg = "fg" }
"ui.cursor" = { fg = "bg", bg = "fg-linenr" }
"ui.cursor.primary" = { fg = "bg", bg = "fg" }
"ui.cursor.primary.normal" = { fg = "bg", bg = "blue" }
"ui.cursor.primary.insert" = { fg = "bg", bg = "light-green" }
"ui.cursor.primary.select" = { fg = "bg", bg = "magenta" }
"ui.cursor.match" = { fg = "orange", modifiers = ["bold"] }
"ui.cursorline.primary" = { bg = "bg-inlay" }
"ui.help" = { bg = "bg-menu", fg = "fg" }
"ui.linenr" = { fg = "fg-linenr" }
"ui.linenr.selected" = { fg = "fg-dark" }
"ui.menu" = { bg = "bg-menu", fg = "fg" }
"ui.menu.selected" = { bg = "fg-selected" }
"ui.popup" = { bg = "bg-menu", fg = "border-highlight" }
"ui.selection" = { bg = "bg-selection" }
"ui.selection.primary" = { bg = "bg-selection" }
"ui.statusline" = { bg = "bg-menu", fg = "fg-dark" }
"ui.statusline.inactive" = { bg = "bg-menu", fg = "comment" }
"ui.statusline.normal" = { bg = "blue", fg = "bg", modifiers = ["bold"] }
"ui.statusline.insert" = { bg = "light-green", fg = "bg", modifiers = ["bold"] }
"ui.statusline.select" = { bg = "magenta", fg = "bg", modifiers = ["bold"] }
"ui.text" = { fg = "fg" }
"ui.text.focus" = { bg = "bg-focus" }
"ui.text.inactive" = { fg = "comment", modifiers = ["italic"] }
"ui.text.info" = { bg = "bg-menu", fg = "fg" }
"ui.text.directory" = { fg = "cyan" }
"ui.virtual.ruler" = { bg = "fg-gutter" }
"ui.virtual.whitespace" = { fg = "fg-gutter" }
"ui.virtual.indent-guide" = { fg = "fg-gutter" }
"ui.virtual.inlay-hint" = { bg = "bg-inlay", fg = "teal" }
"ui.virtual.jump-label" = { fg = "orange", modifiers = ["bold"] }
"ui.window" = { fg = "border", modifiers = ["bold"] }

"ui.bufferline.background" = { bg = "bg-menu" }
"ui.bufferline" = { fg = "comment", bg = "bg-menu" }
"""
    + (  # the active-tab underline key alone would overrun the line limit
        '"ui.bufferline.active" = '
        '{ fg = "fg", bg = "bg", underline = { color = "light-green", style = "line" } }'
    )
)


@dataclass(frozen=True)
class Entry:
    """A [palette] entry: a named colour from a path or a ColorFn mix."""

    name: str
    ref: str | ColorFn


BLANK = None  # a blank line, preserving the grouping in the output

# Diagnostic hints and the teal slot share one slate blue: BLUE sunk toward
# the selection surface (palette syntax.info, not the diagnostic info role).
SLATE = mixed("bg.selection", BLUE, 0.70)

# Helix's named colours, grouped as in the output (BLANK = blank line).
# Slots with a VS Code UI equivalent take that element's colour; the rest
# derive from the semantically-nearest palette anchors.
PALETTE: list[Entry | None] = [
    Entry("orange", ORANGE),
    Entry("yellow", YELLOW),
    Entry("light-green", GREEN),
    Entry("aqua", TEAL),
    Entry("teal", SLATE),
    Entry("cyan", role_path("builtin")),
    Entry("blue", BLUE),
    Entry("purple", PURPLE),
    Entry("magenta", "ansi.magenta"),
    Entry("comment", "fg.comment"),
    Entry("black", "bg.surface"),
    Entry("variable-builtin", role_path("variable.builtin")),
    BLANK,
    Entry("add", GREEN),
    Entry("change", role_path("modified")),
    Entry("delete", RED),
    BLANK,
    Entry("error", RED),
    Entry("info", role_path("info")),
    Entry("hint", SLATE),
    BLANK,
    Entry("fg", "fg.base"),
    Entry("fg-dark", "fg.muted"),
    Entry("fg-gutter", mixed("bg.base", "fg.ink", 0.10)),
    Entry("fg-linenr", "fg.comment"),
    Entry("fg-selected", "bg.selection"),
    Entry("border", "bg.border"),
    Entry("border-highlight", "syntax.keyword"),
    Entry("bg", "bg.base"),
    Entry("bg-inlay", mixed("bg.base", "bg.selection", 0.50)),
    Entry("bg-selection", mixed("bg.selection", "syntax.keyword", 0.20)),
    Entry("bg-menu", "bg.sunken"),
    Entry("bg-focus", "bg.overlay"),
]

HEADER = "# {slug} — generated; do not edit. Rebuild via `just build-ports`."


def generate(flavor: Flavor) -> str:
    """Generate the Helix TOML theme for one flavor."""
    palette = flavor.palette
    width = max(len(entry.name) for entry in PALETTE if entry is not None)

    palette_lines: list[str] = []
    for entry in PALETTE:
        if entry is None:
            palette_lines.append("")
            continue
        ref = entry.ref
        hex_colour = resolve_palette_path(palette, ref) if isinstance(ref, str) else ref(palette)
        palette_lines.append(f'{entry.name.ljust(width)} = "{hex_colour}"')

    header = HEADER.format(slug=flavor.slug)
    return "\n".join([header, "", ROLES, "", "[palette]", *palette_lines, ""])
