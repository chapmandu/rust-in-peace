"""Generated port files stay slim: no restated defaults, no essay headers."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any

import pytest

from scripts import build_ports
from scripts.targets import helix, herdr, ptyxis, zed, zellij
from scripts.variants import Flavor, flavors

GENERATED_LINE = "{slug} — generated; do not edit. Rebuild via `just build-ports`."

ZED_SCHEMA_DEFAULT_NULLS = (
    "editor.invisible",
    "terminal.foreground",
    "terminal.bright_foreground",
    "terminal.dim_foreground",
    "terminal.ansi.dim_black",
    "terminal.ansi.dim_red",
    "terminal.ansi.dim_green",
    "terminal.ansi.dim_yellow",
    "terminal.ansi.dim_blue",
    "terminal.ansi.dim_magenta",
    "terminal.ansi.dim_cyan",
    "terminal.ansi.dim_white",
    "panel.focused_border",
    "pane.focused_border",
)

ZED_SCOPE_RENAMES = {
    "punctuation.list_marker": "punctuation.markup",
    "link_text": "link",
    "link_uri": "link.url",
    "text.literal": "raw",
}

HELIX_REDUNDANT_CHILDREN = (
    "keyword.control",
    "keyword.control.import",
    "keyword.control.return",
    "keyword.function",
    "keyword.operator",
    "keyword.directive",
    "function.macro",
    "string.regexp",
    "type.builtin",
    "constant.builtin",
    "variable.other.member",
    "comment.block.documentation",
    "comment.line.documentation",
)


@pytest.fixture(scope="module")
def zed_family() -> dict[str, Any]:
    parsed: dict[str, Any] = json.loads(zed.generate(flavors()))
    return parsed


def test_zed_omits_schema_default_nulls(zed_family: dict[str, Any]) -> None:
    for theme in zed_family["themes"]:
        style = theme["style"]
        for key in ZED_SCHEMA_DEFAULT_NULLS:
            assert key not in style, key
        dumped = json.dumps(style)
        assert ": null" not in dumped
        for highlight in style["syntax"].values():
            assert None not in highlight.values()


def test_zed_keeps_official_syntax_aliases(zed_family: dict[str, Any]) -> None:
    syntax = zed_family["themes"][0]["style"]["syntax"]
    for official, current in ZED_SCOPE_RENAMES.items():
        assert official in syntax, official
        assert current in syntax, current
        assert syntax[official] == syntax[current]


def test_zed_author_is_byline(zed_family: dict[str, Any]) -> None:
    author = zed_family["author"]
    assert author == "Adam Chapman"
    assert "generated" not in author.lower()


@pytest.mark.parametrize("flavor", flavors(), ids=lambda flavor: flavor.slug)
def test_ptyxis_is_single_scheme(flavor: Flavor) -> None:
    text = ptyxis.generate(flavor)
    assert "[Light]" not in text
    assert "[Dark]" not in text
    assert text.count("[Palette]") == 1
    assert sum(1 for line in text.splitlines() if line.startswith("Background=")) == 1
    assert f"Name={flavor.label}" in text


@pytest.mark.parametrize("flavor", flavors(), ids=lambda flavor: flavor.slug)
def test_helix_drops_redundant_children(flavor: Flavor) -> None:
    data = tomllib.loads(helix.generate(flavor))
    for key in HELIX_REDUNDANT_CHILDREN:
        assert key not in data, key
    assert data["keyword"] == {"fg": "aqua"}
    assert data["type"] == {"fg": "orange", "modifiers": ["italic"]}
    assert data["type.enum.variant"] == {"fg": "orange"}
    assert "italic" not in data["type.enum.variant"]
    assert data["function.builtin"]["fg"] == "cyan"
    assert "italic" in data["variable.builtin"]["modifiers"]


@pytest.mark.parametrize("flavor", flavors(), ids=lambda flavor: flavor.slug)
def test_generated_headers_are_one_line(flavor: Flavor) -> None:
    expected = GENERATED_LINE.format(slug=flavor.slug)
    samples = (
        (helix.generate(flavor), "#"),
        (herdr.generate(flavor), "#"),
        (ptyxis.generate(flavor), "#"),
        (zellij.generate(flavor), "//"),
    )
    for text, marker in samples:
        first = text.splitlines()[0]
        assert first == f"{marker} {expected}"


def test_helix_palette_has_no_per_key_essays() -> None:
    text = helix.generate(flavors()[0])
    palette = text.split("[palette]", 1)[1]
    for line in palette.splitlines():
        assert " #" not in line


def test_herdr_omits_pairing_lie() -> None:
    text = herdr.generate(flavors()[0])
    assert "dark_name" not in text
    assert "light_name" not in text
    assert "sidebar_bg" not in text
    assert "active_row_bg" not in text
    assert "selection_bg" not in text


def test_build_ports_clears_orphan_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(build_ports, "PORTS_DIR", tmp_path)
    orphan = tmp_path / "helix" / "gone.toml"
    orphan.parent.mkdir(parents=True)
    orphan.write_text("stale\n")

    build_ports.main()

    assert not orphan.exists()
    assert (tmp_path / "helix" / "rust-in-peace.toml").exists()
    assert (tmp_path / "zed" / "rust-in-peace.json").exists()
    assert (tmp_path / "ptyxis" / "rust-in-peace.palette").exists()
