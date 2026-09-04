"""Zed theme JSON.

Maps the palettes onto Zed's v0.2.0 theme schema, mirroring the VS Code
theme: chrome (tabs, panels, terminal) sits on the sunken band, the status
bar wears the deep skull-violet, green is the active UI accent, and the
token philosophy matches scope-for-scope. Zed themes are families, so one
file carries all four flavors.

Design: UI surfaces resolve once into named semantic aliases (bg, chrome,
elevated, active, ...) that the style map reuses, so each VS Code-equivalence
decision is made in exactly one place. Syntax and git-status colours come
from the shared role table (scripts/roles.py) so modified / info / builtin
/ variable.builtin cannot drift from VS Code or Helix.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from scripts.palette import Palette, resolve_palette_path
from scripts.roles import BLUE, COMMENT, CYAN, GREEN, ORANGE, PURPLE, RED, TEAL, YELLOW
from scripts.roles import ROLES as THEME_ROLES
from scripts.variants import Flavor


@dataclass(frozen=True)
class SyntaxGroup:
    """A syntax group: one palette colour applied to a set of Zed syntax scopes."""

    color: str
    scopes: list[str]
    font_style: str | None = None
    font_weight: int | None = None


# Syntax highlighting, grouped by palette role. Mirrors the VS Code theme's
# token philosophy: keywords/operators/tags = tube blue, functions = green,
# strings = gold, types/params = orange, constants/numbers = violet,
# builtins/links = cyan, comments = muted blue.
# Current Zed names (old keys no longer map): punctuation.markup, link,
# link.url, raw — not punctuation.list_marker / link_text / link_uri /
# text.literal.
SYNTAX = [
    SyntaxGroup(
        color=TEAL,
        scopes=[
            "keyword",
            "keyword.conditional",
            "keyword.conditional.ternary",
            "keyword.coroutine",
            "keyword.directive",
            "keyword.directive.define",
            "keyword.exception",
            "keyword.export",
            "keyword.function",
            "keyword.import",
            "keyword.modifier",
            "keyword.operator",
            "keyword.repeat",
            "keyword.return",
            "keyword.type",
            "operator",
            "tag",
            "tag.delimiter",
            "string.escape",
            "constant.macro",
            "concept",
            "character.special",
        ],
    ),
    SyntaxGroup(
        color=GREEN,
        scopes=[
            "function",
            "function.call",
            "function.decorator",
            "function.macro",
            "function.method",
            "function.method.call",
            "attribute",
            "tag.attribute",
            "diff.plus",
        ],
    ),
    SyntaxGroup(
        color=THEME_ROLES["function.builtin"].path,
        scopes=["function.builtin"],
    ),
    SyntaxGroup(
        color=YELLOW,
        scopes=[
            "string",
            "string.regex",
            "string.regexp",
            "string.special",
            "string.special.symbol",
            "string.special.path",
            "string.doc",
            "string.documentation",
            "raw",
            "character",
        ],
    ),
    SyntaxGroup(
        color=ORANGE,
        scopes=[
            "type",
            "type.builtin",
            "type.class.definition",
            "type.definition",
            "type.interface",
            "type.super",
            "enum",
            "constructor",
            "comment.todo",
            "comment.warning",
        ],
    ),
    SyntaxGroup(
        color=ORANGE,
        font_style="italic",
        scopes=["parameter", "variable.parameter"],
    ),
    SyntaxGroup(
        color=PURPLE,
        scopes=["constant", "constant.builtin", "boolean", "number", "number.float", "float"],
    ),
    SyntaxGroup(
        color=CYAN,
        scopes=["preproc", "link", "link.url", "string.special.url"],
    ),
    SyntaxGroup(
        color=BLUE,
        scopes=["comment.note", "comment.hint"],
    ),
    SyntaxGroup(
        color=RED,
        scopes=[
            "diff.minus",
            "comment.error",
            "variable.special",
            "keyword.debug",
        ],
    ),
    SyntaxGroup(
        color=THEME_ROLES["variable.builtin"].path,
        font_style="italic" if THEME_ROLES["variable.builtin"].italic else None,
        scopes=["variable.builtin"],
    ),
    SyntaxGroup(
        color=COMMENT,
        scopes=["comment", "comment.doc", "comment.documentation", "predoc", "tag.doctype"],
    ),
    SyntaxGroup(
        color="fg.base",
        scopes=[
            "label",
            "punctuation",
            "punctuation.bracket",
            "punctuation.delimiter",
            "punctuation.markup",
            "punctuation.special",
            "module",
            "namespace",
            "parent",
            "primary",
            "property",
            "symbol",
            "variable",
            "variable.member",
            "variant",
            "field",
            "embedded",
        ],
    ),
    SyntaxGroup(color=YELLOW, font_style="italic", scopes=["emphasis"]),
    SyntaxGroup(color=ORANGE, font_weight=700, scopes=["emphasis.strong"]),
    SyntaxGroup(color=PURPLE, font_weight=700, scopes=["title"]),
]

# The translucent editor accents, led by green — the VS Code active accent.
ACCENTS = [GREEN, ORANGE, YELLOW, CYAN, PURPLE, RED, BLUE]


def _style(palette: Palette) -> dict[str, Any]:
    """Build one flavor's style map from its palette."""

    def col(path: str, alpha: str = "") -> str:
        """Resolve a palette path to hex, with an optional 2-hex alpha suffix."""
        return resolve_palette_path(palette, path) + alpha

    # Semantic aliases for the UI surfaces.
    bg = col("bg.base")  #             editor & primary background
    chrome = col("bg.sunken")  #       panels, tabs, status/title bars, terminal
    elevated = col("bg.border")  #     elevated surfaces / overlays (darkest)
    border = col("bg.selection")  #    visible structural seams (as VS Code's editorGroup.border)
    border_subtle = col("bg.border")  # recessed lines: wrap guides, scrollbar track
    active = col("bg.overlay")  #      active line, active element, drop target
    selection = col("bg.selection")  # solid list selection (VS Code list.activeSelectionBackground)
    hover = col("bg.selection", "80")  # subtle dark list hover (VS Code list.hoverBackground)
    muted = col("fg.comment")  #       dim text/icons, scrollbar hover
    fg = col("fg.base")
    subtext = col("fg.muted")
    accent = col(GREEN)  # active UI accent — green, as in VS Code
    link = col(CYAN)  #    links & highlights — cyan, as in VS Code
    git_border = active  #             border around git-status callouts

    def highlight(group: SyntaxGroup) -> dict[str, Any]:
        """Colour plus any non-default font fields (schema defaults are null)."""
        style: dict[str, Any] = {"color": col(group.color)}
        if group.font_style is not None:
            style["font_style"] = group.font_style
        if group.font_weight is not None:
            style["font_weight"] = group.font_weight
        return style

    syntax = {scope: highlight(group) for group in SYNTAX for scope in group.scopes}

    def status_entries(name: str, path: str) -> dict[str, str]:
        """Expand `<name>` to fg/background/border entries — coloured fg on the editor bg."""
        return {name: col(path), f"{name}.background": bg, f"{name}.border": git_border}

    style: dict[str, Any] = {
        "accents": [col(path, "66") for path in ACCENTS],
        "background.appearance": "opaque",
        "border": border,
        "border.variant": border_subtle,
        "border.focused": col("fg.comment", "33"),
        "border.selected": border,
        "border.transparent": border_subtle,
        "border.disabled": border_subtle,
        "elevated_surface.background": elevated,
        "surface.background": chrome,
        "background": bg,
        "element.background": bg,
        "element.hover": hover,
        "element.active": active,
        "element.selected": selection,
        "element.disabled": active,
        "drop_target.background": selection,
        # Transparent, so status-bar buttons show the bar behind them.
        "ghost_element.background": col("bg.base", "00"),
        "ghost_element.hover": hover,
        "ghost_element.active": active,
        "ghost_element.selected": selection,
        "ghost_element.disabled": active,
        "text": fg,
        "text.muted": subtext,
        "text.placeholder": muted,
        "text.disabled": muted,
        "text.accent": accent,
        "icon": subtext,
        "icon.muted": muted,
        "icon.disabled": muted,
        "icon.placeholder": muted,
        "icon.accent": accent,
        "status_bar.background": col("ui.statusBar"),  # deep skull-violet, matching VS Code
        "title_bar.background": chrome,
        "title_bar.inactive_background": chrome,
        # Breadcrumb strip below the tabs — continues the active tab's editor
        # surface; its path text renders in text.muted.
        "toolbar.background": bg,
        "tab_bar.background": chrome,
        "tab.inactive_background": chrome,
        "tab.active_background": bg,
        "search.match_background": active,
        "panel.background": chrome,
        "panel.indent_guide": active,
        "panel.indent_guide_active": muted,
        "panel.indent_guide_hover": muted,
        "panel.overlay_background": elevated,
        "pane_group.border": border,
        "scrollbar.thumb.background": col("bg.overlay"),
        "scrollbar.thumb.hover_background": muted,
        "scrollbar.thumb.border": col("bg.overlay"),
        "scrollbar.track.background": col("bg.base", "80"),
        "scrollbar.track.border": border_subtle,
        "editor.foreground": fg,
        "editor.background": bg,
        "editor.gutter.background": bg,
        "editor.subheader.background": bg,
        # Soft solid bar just above the editor surface, as VS Code's
        # editor.lineHighlightBackground.
        "editor.active_line.background": col("bg.selection", "80"),
        "editor.highlighted_line.background": active,
        "editor.line_number": muted,
        "editor.active_line_number": fg,
        "editor.wrap_guide": border_subtle,
        "editor.active_wrap_guide": border_subtle,
        "editor.document_highlight.read_background": active,
        "editor.document_highlight.write_background": active,
        "editor.document_highlight.bracket_background": selection,
        "editor.indent_guide": active,
        "editor.indent_guide_active": muted,
        # Omit terminal.foreground / bright_foreground / dim_foreground and
        # every terminal.ansi.dim_* — schema default is null, and omit ≡ JSON
        # null. Zed does not derive dim ANSI from the bright slots; missing
        # dim keys fall through to ThemeColors::{dark,light} built-ins.
        "terminal.background": chrome,
        "terminal.ansi.background": chrome,
        "terminal.ansi.black": col("ansi.black"),
        "terminal.ansi.bright_black": col("ansi.brightBlack"),
        "terminal.ansi.red": col("ansi.red"),
        "terminal.ansi.bright_red": col("ansi.brightRed"),
        "terminal.ansi.green": col("ansi.green"),
        "terminal.ansi.bright_green": col("ansi.brightGreen"),
        "terminal.ansi.yellow": col("ansi.yellow"),
        "terminal.ansi.bright_yellow": col("ansi.brightYellow"),
        "terminal.ansi.blue": col("ansi.blue"),
        "terminal.ansi.bright_blue": col("ansi.brightBlue"),
        "terminal.ansi.magenta": col("ansi.magenta"),
        "terminal.ansi.bright_magenta": col("ansi.brightMagenta"),
        "terminal.ansi.cyan": col("ansi.cyan"),
        "terminal.ansi.bright_cyan": col("ansi.brightCyan"),
        "terminal.ansi.white": col("ansi.white"),
        "terminal.ansi.bright_white": col("ansi.brightWhite"),
        "link_text.hover": link,
        **status_entries("conflict", PURPLE),
        **status_entries("created", GREEN),
        **status_entries("deleted", RED),
        **status_entries("error", RED),
        **status_entries("hidden", "fg.muted"),
        **status_entries("hint", COMMENT),
        **status_entries("ignored", COMMENT),
        **status_entries("info", THEME_ROLES["info"].path),
        **status_entries("modified", THEME_ROLES["modified"].path),
        **status_entries("predictive", COMMENT),
        **status_entries("renamed", GREEN),
        **status_entries("success", GREEN),
        **status_entries("unreachable", RED),
        **status_entries("warning", ORANGE),
        "version_control.added": col(GREEN),
        "version_control.added_background": bg,
        "version_control.conflict": col(PURPLE),
        "version_control.conflict_background": bg,
        "version_control.deleted": col(RED),
        "version_control.deleted_background": bg,
        "version_control.ignored": col(COMMENT),
        "version_control.modified": col(THEME_ROLES["modified"].path),
        "version_control.modified_background": bg,
        "version_control.renamed": col(BLUE),
        "players": [
            {
                "cursor": accent,
                "background": accent,
                # Teal wash, matching VS Code's selection.
                "selection": col(TEAL, "3d"),
            }
        ],
        "syntax": syntax,
    }

    return style


def generate(flavors: list[Flavor]) -> str:
    """Generate the Zed theme-family JSON carrying every flavor."""
    # JSON carries no comments, so the author field doubles as the
    # generated-from notice.
    theme = {
        "$schema": "https://zed.dev/schema/themes/v0.2.0.json",
        "name": "Rust in Peace",
        "author": "Adam Chapman — generated from the src/ palettes; do not edit by hand",
        "themes": [
            {"name": flavor.label, "appearance": flavor.appearance, "style": _style(flavor.palette)}
            for flavor in flavors
        ],
    }

    return json.dumps(theme, indent=2, ensure_ascii=False) + "\n"
