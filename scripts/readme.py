"""Regenerate the README's swatch art and generated sections.

Each theme is rendered as a miniature editor window — a deterministic SVG
assembled from f-string fragments — and rasterized to PNG at 2× via resvg,
because the Marketplace rejects SVG images in READMEs. The hero and palette
blocks are spliced between `<!-- GENERATED ... -->` markers in README.md, so
the surrounding prose stays hand-edited.

Design: layout is pure arithmetic on a 640x400 viewBox. Text runs are pinned
with textLength so the maths, not the renderer's font metrics, decides where
code sits; JetBrains Mono's exact 0.6em advance keeps that pinning from
stretching glyphs. Coordinates go through fmt() so the SVG is byte-stable.
The banner at assets/banner.png is hand-made and never touched by the build.
"""

from __future__ import annotations

import shutil
from typing import NamedTuple

import resvg_py

from scripts.palette import REPO_ROOT, Palette, resolve_palette_path
from scripts.roles import ROLES
from scripts.variants import Flavor, flavors

REPO = "https://github.com/chapmandu/rust-in-peace"
REPO_RAW = f"{REPO}/raw/main"
MARKETPLACE_URL = "https://marketplace.visualstudio.com/items?itemName=chapmandu.rust-in-peace"


class Run(NamedTuple):
    """One run of same-coloured text; `squiggle` marks the error underline."""

    text: str
    role: str
    squiggle: bool = False


def snippet_style(palette: Palette, name: str) -> tuple[str, bool]:
    """Resolve a snippet token to ``(hex, italic)``.

    Names in the shared role table (``scripts.roles.ROLES``) take colour and
    italic from that table. Anything else is a dotted palette path with italic
    off — the same fall-through ``apply_palette`` uses.
    """
    role = ROLES.get(name)
    if role is not None:
        return resolve_palette_path(palette, role.path), role.italic
    return resolve_palette_path(palette, name), False


# The demo snippet, as token runs so the same code renders in every variant's
# colours. Each line exists to exercise a palette role; the squiggle sits under
# "intelligence" (two words combined that can't make sense — Hangar 18).
# Token names are shared role names or dotted palette paths — not a private map.
SNIPPET: list[list[Run]] = [
    [Run("//! Megadeth — Rust in Peace (1990)", "fg.comment")],
    [
        Run("use ", "keyword"),
        Run("hangar", "builtin"),
        Run("::", "fg.base"),
        Run("warhead", "builtin"),
        Run("::", "fg.base"),
        Run("Polaris", "type"),
        Run(";", "fg.base"),
    ],
    [
        Run("#[military(", "syntax.info"),
        Run("intelligence", "syntax.info", squiggle=True),
        Run(" = ", "fg.base"),
        Run("false", "constant"),
        Run(")]", "syntax.info"),
    ],
    [
        Run("pub struct ", "keyword"),
        Run("Rattlehead", "type"),
        Run(" { rust_eaten: ", "fg.base"),
        Run("bool", "builtin"),
        Run(" }", "fg.base"),
    ],
    [
        Run("impl ", "keyword"),
        Run("Rattlehead", "type"),
        Run(" {", "fg.base"),
    ],
    [
        Run("    ", "fg.base"),
        Run("pub fn ", "keyword"),
        Run("holy_wars", "function"),
        Run("(&", "fg.base"),
        Run("self", "variable.builtin"),
        Run(") -> ", "fg.base"),
        Run("Punishment", "type"),
        Run(" {", "fg.base"),
    ],
    [
        Run("        ", "fg.base"),
        Run("let ", "keyword"),
        Run("dues = ", "fg.base"),
        Run("Verse", "type"),
        Run("::", "fg.base"),
        Run("from", "function"),
        Run("(", "fg.base"),
        Run('"the punishment due"', "string"),
        Run(");", "fg.base"),
    ],
    [
        Run("        dues.", "fg.base"),
        Run("punish", "function"),
        Run("(", "fg.base"),
        Run("NUCLEAR_DAWN", "constant"),
        Run(" * ", "fg.base"),
        Run("1990", "constant"),
        Run(")", "fg.base"),
    ],
    [Run("    }", "fg.base")],
    [Run("}", "fg.base")],
]

# Zero-based line index that gets the current-line highlight.
CURRENT_LINE = 6

# Rail labels for the syntax colours, drawn from the album's world.
RAIL_NAMES = {
    "keyword": "warhead",  # Polaris missile steel — the cobalt of the cover art
    "builtin": "cryogenic",  # "suspended state of cryogenics" — Hangar 18
    "info": "radar",  # the airbase radar glow
    "function": "geiger",  # radioactive green, counted in clicks
    "string": "trefoil",  # the yellow radiation symbol on the hangar door
    "type": "oxide",  # rust, resting in peace
    "constant": "lucretia",  # the album's ghost track — ethereal violet
    "error": "punishment",  # "The Punishment Due" — every error gets theirs
}

# Window geometry (viewBox units; display size is set by the README <img>).
W = 640
H = 400
TAB_H = 36
RAIL_Y = 312
STATUS_Y = 368
CODE_X = 64
FIRST_BASELINE = 62
LINE_H = 24
FONT = 13
CH = FONT * 0.6  # monospace advance; tspans are pinned with textLength

# JetBrains Mono's advance is exactly 0.6em, matching the layout math below,
# so textLength pinning never stretches glyphs.
MONO = "'JetBrains Mono', ui-monospace, 'Cascadia Code', Menlo, Consolas, monospace"


def escape_xml(text: str) -> str:
    """Escape text for embedding in SVG attributes and content."""
    return (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )


def fmt(value: float) -> str:
    """Format a coordinate without float noise, for byte-stable output."""
    return f"{round(value, 1):g}"


def squiggle_path(x: float, y: float, width: float) -> str:
    """Wavy error underline starting at x, of the given width."""
    step = 6
    segments = max(1, round(width / step))
    tail = " t 6 0" * (segments - 1)
    return f"M {fmt(x)} {fmt(y)} q 3 3 6 0{tail}"


def render_window(palette: Palette, label: str) -> str:
    """Render one theme as a miniature editor window (deterministic SVG)."""

    def colour(path: str) -> str:
        return resolve_palette_path(palette, path)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape_xml(label)} palette preview">',
        f'<defs><clipPath id="window"><rect width="{W}" height="{H}" rx="12"/></clipPath></defs>',
        f'<g clip-path="url(#window)" font-family="{MONO}">',
        # Window bands: tab strip, editor, hex rail, status bar.
        f'<rect width="{W}" height="{H}" fill="{colour("bg.sunken")}"/>',
        f'<rect y="{TAB_H}" width="{W}" height="{RAIL_Y - TAB_H}" fill="{colour("bg.base")}"/>',
        f'<rect y="{STATUS_Y}" width="{W}" height="{H - STATUS_Y}" fill="{colour("ui.statusBar")}"/>',
    ]

    # Window dots, in palette colours.
    dots = [
        (20, colour("syntax.error")),
        (38, colour("syntax.string")),
        (56, colour("syntax.function")),
    ]
    for cx, fill in dots:
        parts.append(f'<circle cx="{cx}" cy="18" r="5" fill="{fill}" opacity="0.75"/>')

    # Active tab with VS Code's top accent border.
    parts += [
        f'<rect x="80" y="8" width="170" height="34" rx="6" fill="{colour("bg.base")}"/>',
        f'<rect x="84" y="6" width="162" height="2" rx="1" fill="{colour("ui.button")}"/>',
        f'<text x="165" y="27" text-anchor="middle" font-size="12" fill="{colour("fg.base")}">rust_in_peace.rs</text>',
    ]

    # Current-line highlight, under the text but over the editor band.
    current_line_top = FIRST_BASELINE + CURRENT_LINE * LINE_H - 16
    parts.append(
        f'<rect y="{fmt(current_line_top)}" width="{W}" height="{LINE_H}" fill="{colour("bg.selection")}" opacity="0.6"/>'
    )

    # Gutter numbers and code lines.
    for index, runs in enumerate(SNIPPET):
        baseline = FIRST_BASELINE + index * LINE_H
        number_fill = colour("fg.muted") if index == CURRENT_LINE else colour("fg.comment")
        parts.append(
            f'<text x="44" y="{fmt(baseline)}" text-anchor="end" font-size="11" fill="{number_fill}">{index + 1}</text>'
        )

        tspans = []
        cursor = float(CODE_X)
        for run in runs:
            width = len(run.text) * CH
            fill, italic = snippet_style(palette, run.role)
            style = ' font-style="italic"' if italic else ""
            tspans.append(
                f'<tspan x="{fmt(cursor)}" textLength="{fmt(width)}" lengthAdjust="spacingAndGlyphs" fill="{fill}"{style}>{escape_xml(run.text)}</tspan>'
            )
            if run.squiggle:
                parts.append(
                    f'<path d="{squiggle_path(cursor, baseline + 4, width)}" fill="none" stroke="{colour("syntax.error")}" stroke-width="1.2"/>'
                )
            cursor += width
        parts.append(
            f'<text y="{fmt(baseline)}" font-size="{FONT}" xml:space="preserve">{"".join(tspans)}</text>'
        )

    # Colour rail: the eight syntax colours as named cells.
    syntax_group = palette["syntax"]
    assert isinstance(syntax_group, dict)  # noqa: S101 — narrows the palette union for mypy
    cell = W / len(syntax_group)
    for index, key in enumerate(syntax_group):
        x = index * cell
        parts += [
            f'<rect x="{fmt(x + 12)}" y="{RAIL_Y + 10}" width="{fmt(cell - 24)}" height="18" rx="4" fill="{colour(f"syntax.{key}")}"/>',
            f'<text x="{fmt(x + cell / 2)}" y="{RAIL_Y + 46}" text-anchor="middle" font-size="9.5" fill="{colour("fg.muted")}">{RAIL_NAMES.get(key, key)}</text>',
        ]

    # Status bar text: ink is white on the dark palettes, navy on light.
    parts += [
        f'<text x="16" y="{STATUS_Y + 20}" font-size="11" fill="{colour("fg.ink")}">{escape_xml(label)}</text>',
        f'<text x="{W - 16}" y="{STATUS_Y + 20}" text-anchor="end" font-size="11" fill="{colour("fg.ink")}" opacity="0.8" xml:space="preserve">Ln 7, Col 29   UTF-8   Rust</text>',
    ]

    parts += [
        "</g>",
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{colour("bg.border")}"/>',
        "</svg>",
    ]
    return "\n".join(parts) + "\n"


def badges(palette: Palette) -> str:
    """CI and marketplace badges, tinted from the palette.

    shields.io retired its visual-studio-marketplace service; badgen.net still
    serves it live and is on vsce's trusted-badge list.
    """

    def tint(path: str) -> str:
        return resolve_palette_path(palette, path)[1:]

    def badgen(kind: str, label: str, color: str) -> str:
        return (
            f"[![{label}](https://flat.badgen.net/vs-marketplace/{kind}/chapmandu.rust-in-peace"
            f"?label={label.lower()}&labelColor={tint('bg.sunken')}&color={color})]({MARKETPLACE_URL})"
        )

    return "\n".join(
        [
            f"[![CI]({REPO}/actions/workflows/ci.yml/badge.svg)]({REPO}/actions/workflows/ci.yml)",
            badgen("v", "Marketplace", tint("ui.button")),
            badgen("i", "Installs", tint("ui.statusBar")),
        ]
    )


def render_png(svg: str) -> bytes:
    """Render an SVG string to a PNG at 2x resolution (crisp on hidpi)."""
    return bytes(
        resvg_py.svg_to_bytes(
            svg_string=svg,
            zoom=2,
            font_family="JetBrains Mono",
            monospace_family="JetBrains Mono",
        )
    )


def hero_block(palette: Palette) -> str:
    """Render the hero: the hand-made banner, tagline, and badges."""
    return f"""<div align="center">

<img src="{REPO_RAW}/assets/banner.png" alt="Rust in Peace — a dark theme for VS Code" width="1280"/>

<br/>

**A dark theme for VS Code, inspired by the album art of Megadeth's 1990 metal masterpiece, _Rust in Peace_.**

{badges(palette)}

<br/>

</div>"""


def palette_block(themes: list[Flavor]) -> str:
    """Render the palette section: album cover and the theme grid, dark to light."""

    def cell(theme: Flavor) -> str:
        swatch_url = f"{REPO_RAW}/assets/generated/{theme.slug}.png"
        label = theme.label.removeprefix("Rust in Peace ")
        return (
            f'<td align="center" width="50%"><strong>{label}</strong><br/>'
            f'<img src="{swatch_url}" alt="{theme.label}" width="400"/></td>'
        )

    # All themes at equal size, reading dark to light. One single-row table
    # per pair, with a spacer between, so the grid rows get breathing room.
    rows = [
        "<table>\n<tr>\n"
        + "\n".join(cell(theme) for theme in themes[i : i + 2])
        + "\n</tr>\n</table>"
        for i in range(0, len(themes), 2)
    ]
    grid = "\n\n<br/>\n\n".join(rows)

    return f"""<div align="center">

<br/>

<img src="{REPO_RAW}/assets/Megadeth-RustInPeace.jpg" alt="Rust in Peace album cover" width="260"/>

_Hand-picked from the record's rusted, cobalt-blue cover art._

<br/>

{grid}

<br/>

</div>"""


def inject(source: str, region: str, block: str) -> str:
    """Splice a generated block into the named marker region."""
    start_marker = f"<!-- GENERATED {region} START (npm run build — do not edit by hand) -->"
    end_marker = f"<!-- GENERATED {region} END -->"
    start = source.find(start_marker)
    end = source.find(end_marker)
    if start == -1 or end == -1 or end < start:
        raise ValueError(f'README.md is missing the "{start_marker}" / "{end_marker}" markers')
    return source[: start + len(start_marker)] + f"\n{block}\n" + source[end:]


def build_readme() -> None:
    """Regenerate the swatch PNGs and the README's generated sections."""
    # Dark to light: base, Hangar 18, Polaris, Dawn Patrol.
    themes = flavors()

    generated_dir = REPO_ROOT / "assets" / "generated"
    shutil.rmtree(generated_dir, ignore_errors=True)
    generated_dir.mkdir(parents=True)
    for theme in themes:
        png = render_png(render_window(theme.palette, theme.label))
        (generated_dir / f"{theme.slug}.png").write_bytes(png)

    readme_path = REPO_ROOT / "README.md"
    readme = readme_path.read_text(encoding="utf-8")

    regions = {
        "HERO": hero_block(themes[0].palette),  # badges tinted from the dark base
        "PALETTE": palette_block(themes),
    }

    updated = readme
    for region, block in regions.items():
        updated = inject(updated, region, block)

    if updated != readme:
        readme_path.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    build_readme()
