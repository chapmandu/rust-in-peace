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
"keyword.control" = { fg = "aqua" }
"keyword.control.import" = { fg = "aqua" }
"keyword.control.return" = { fg = "aqua" }
"keyword.function" = { fg = "aqua" }
"keyword.operator" = { fg = "aqua" }
"keyword.directive" = { fg = "aqua" }
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
"function.macro" = { fg = "light-green" }
"function.special" = { fg = "cyan" }
attribute = { fg = "light-green", modifiers = ["italic"] }

string = { fg = "yellow" }
"string.regexp" = { fg = "yellow" }
"string.special" = { fg = "aqua" }
"constant.character" = { fg = "yellow" }

type = { fg = "orange", modifiers = ["italic"] }
"type.builtin" = { fg = "orange", modifiers = ["italic"] }
"type.enum.variant" = { fg = "orange" }
constructor = { fg = "orange" }
"variable.parameter" = { fg = "orange", modifiers = ["italic"] }

constant = { fg = "purple" }
"constant.builtin" = { fg = "purple" }
variable = { fg = "fg" }
"""
    + _VAR_BUILTIN
    + """
"variable.other.member" = { fg = "fg" }
label = { fg = "blue" }
namespace = { fg = "fg" }

comment = { fg = "comment", modifiers = ["italic"] }
"comment.block.documentation" = { fg = "comment", modifiers = ["italic"] }
"comment.line.documentation" = { fg = "comment", modifiers = ["italic"] }

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
    """A [palette] entry.

    A named colour resolved from a palette path, or derived from palette
    anchors via a ColorFn (scripts/color.py) for Helix-specific shades the
    core palette doesn't carry directly.
    """

    name: str
    ref: str | ColorFn
    comment: str | None = None


BLANK = None  # a blank line, preserving the grouping in the output

# Diagnostic hints and the teal slot share one slate blue: BLUE sunk toward
# the selection surface (palette syntax.info, not the diagnostic info role).
SLATE = mixed("bg.selection", BLUE, 0.70)

# Helix's named colours, grouped as in the output (BLANK = blank line).
# Slots with a VS Code UI equivalent take that element's colour; the rest
# derive from the semantically-nearest palette anchors.
PALETTE: list[Entry | None] = [
    Entry("orange", ORANGE, "logo orange — types, parameters"),
    Entry("yellow", YELLOW, "logo gold — strings"),
    Entry("light-green", GREEN, "glowing hand green — functions"),
    Entry("aqua", TEAL, "electric tube blue — keywords, operators"),
    Entry("teal", SLATE, "slate blue — markup, hints"),
    Entry("cyan", role_path("builtin"), "sky cyan — builtins"),
    Entry("blue", BLUE, "bright tube blue — UI accents, labels"),
    Entry("purple", PURPLE, "softened violet — constants, headings"),
    Entry("magenta", "ansi.magenta", "sarcophagus pink — select mode"),
    Entry("comment", "fg.comment", "muted blue shading"),
    Entry("black", "bg.surface", "raised surface blue"),
    Entry(
        "variable-builtin",
        role_path("variable.builtin"),
        "this/self — as VS Code variable.language",
    ),
    BLANK,
    Entry("add", GREEN, "as VS Code gitDecoration.added"),
    Entry("change", role_path("modified"), "as VS Code gitDecoration.modified"),
    Entry("delete", RED, "as VS Code gitDecoration.deleted"),
    BLANK,
    Entry("error", RED, "as VS Code editorError"),
    Entry("info", role_path("info"), "as VS Code editorInfo"),
    Entry("hint", SLATE),
    BLANK,
    Entry("fg", "fg.base", "pale blue highlight white"),
    Entry("fg-dark", "fg.muted"),
    Entry(
        "fg-gutter",
        mixed("bg.base", "fg.ink", 0.10),
        "whitespace marks — flattened editorWhitespace",
    ),
    Entry("fg-linenr", "fg.comment", "as VS Code editorLineNumber"),
    Entry("fg-selected", "bg.selection", "menu selection bg — as VS Code list selection"),
    Entry("border", "bg.border"),
    Entry("border-highlight", "syntax.keyword"),
    Entry("bg", "bg.base", "hangar deep blue"),
    Entry("bg-inlay", mixed("bg.base", "bg.selection", 0.50), "flattened list.focusBackground"),
    Entry(
        "bg-selection",
        mixed("bg.selection", "syntax.keyword", 0.20),
        "selection lifted toward tube blue for visibility",
    ),
    Entry("bg-menu", "bg.sunken", "statusline, popups"),
    Entry("bg-focus", "bg.overlay"),
]

HEADER = """\
# {slug} — a Helix theme from the Megadeth "Rust in Peace" cover palette.
# Generated from the src/ palettes by scripts/targets/helix.py (just build-ports).
# Do not edit by hand: edit the palette and rebuild.

# Syntax roles mirror the rust-in-peace VSCode theme (original structure):
#   keywords / operators / delimiters / tags = electric tube blue
#   functions / decorators = glow green      strings  = logo gold
#   types / parameters     = logo orange     constants = violet
#   builtins / function.builtin = sky cyan   comments = muted blue
#   this/self (variable.builtin) = logo gold italic
# The theme is standalone — markup, diagnostics, and the full UI layer are
# defined below. Every colour in [palette] derives from the shared role
# table (scripts/roles.py); diffs and diagnostics follow the VS Code
# theme's UI elements. Helix-only shades use declared mix formulas."""


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
        line = f'{entry.name.ljust(width)} = "{hex_colour}"'
        palette_lines.append(f"{line} # {entry.comment}" if entry.comment else line)

    header = HEADER.format(slug=flavor.slug)
    return "\n".join([header, "", ROLES, "", "[palette]", *palette_lines, ""])
