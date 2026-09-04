import pytest

from scripts.generate import apply_palette, build_theme, generate
from scripts.palette import Palette
from scripts.variants import flavors

PALETTE: Palette = {"bg": {"base": "#101530"}, "fg": {"base": "#d3e0f0"}}


def test_apply_palette_substitutes_placeholders() -> None:
    assert apply_palette("x: '{{bg.base}}'", PALETTE) == "x: '#101530'"


def test_apply_palette_preserves_alpha_suffix() -> None:
    assert apply_palette("x: '{{ bg.base }}80'", PALETTE) == "x: '#10153080'"


def test_apply_palette_unknown_path_raises() -> None:
    with pytest.raises(ValueError, match="syntax.keyword"):
        apply_palette("x: '{{syntax.keyword}}'", PALETTE)


def test_alpha_tag_concatenates_colour_and_alpha() -> None:
    source = 'name: t\ncolors:\n  a: !alpha ["#101530", 99]\ntokenColors: []'
    theme = build_theme(source, {})
    assert theme["colors"] == {"a": "#10153099"}


def test_build_theme_strips_unset_colours() -> None:
    source = "name: t\ncolors:\n  keep: '#101530'\n  drop: null\ntokenColors: []"
    theme = build_theme(source, {})
    assert theme["colors"] == {"keep": "#101530"}


def test_apply_palette_resolves_role_names() -> None:
    palette: Palette = {"syntax": {"builtin": "#99c5f0", "string": "#e8e274"}}
    assert apply_palette("x: '{{builtin}}'", palette) == "x: '#99c5f0'"
    assert apply_palette("x: '{{variable.builtin}}'", palette) == "x: '#e8e274'"


def test_apply_palette_ansi_is_palette_path_not_role() -> None:
    palette: Palette = {"ansi": {"black": "#1c2547", "blue": "#9a63de"}}
    assert apply_palette("{{ansi.black}}", palette) == "#1c2547"
    assert apply_palette("{{ansi.blue}}", palette) == "#9a63de"


def test_info_role_is_builtin_not_syntax_info() -> None:
    palette: Palette = {"syntax": {"builtin": "#99c5f0", "info": "#84bef5"}}
    assert apply_palette("{{info}}", palette) == "#99c5f0"
    assert apply_palette("{{modified}}", palette) == "#99c5f0"
    assert apply_palette("{{syntax.info}}", palette) == "#84bef5"


def test_build_theme_keeps_only_theme_keys() -> None:
    source = (
        "$schema: vscode://schemas/color-theme\n"
        "name: leftover\n"
        "author: someone\n"
        "maintainers:\n  - A <a@b.c>\n"
        "semanticClass: theme.x\n"
        "semanticHighlighting: true\n"
        "rustInPeace:\n  base: []\n"
        "colors:\n  keep: '#101530'\n"
        "tokenColors: []\n"
    )
    theme = build_theme(source, {})
    assert set(theme) == {"semanticHighlighting", "colors", "tokenColors"}
    assert theme["semanticHighlighting"] is True


def test_generate_sets_type_from_appearance_and_slims() -> None:
    allowed = {"name", "type", "semanticHighlighting", "colors", "tokenColors"}
    built = generate()
    for flavor, theme in built:
        assert set(theme) == allowed
        assert theme["name"] == flavor.label
        assert theme["type"] == flavor.appearance
    assert [flavor.appearance for flavor, _theme in built] == [
        flavor.appearance for flavor in flavors()
    ]
