import pytest

from scripts.palette import load_palette, resolve_palette_path
from scripts.readme import SNIPPET, Run, fmt, inject, snippet_style, squiggle_path
from scripts.roles import ROLES, resolve_role


def test_fmt_drops_float_noise() -> None:
    assert fmt(64.0) == "64"
    assert fmt(64.5) == "64.5"
    assert fmt(7.800000000000001) == "7.8"


def test_squiggle_path_repeats_wave_segments() -> None:
    assert squiggle_path(64, 66, 12) == "M 64 66 q 3 3 6 0 t 6 0"


def test_squiggle_path_has_at_least_one_segment() -> None:
    assert squiggle_path(0, 0, 1) == "M 0 0 q 3 3 6 0"


README = """intro
<!-- GENERATED X START (npm run build — do not edit by hand) -->
stale
<!-- GENERATED X END -->
outro"""


def test_inject_replaces_marker_region() -> None:
    updated = inject(README, "X", "fresh")
    assert "fresh" in updated
    assert "stale" not in updated
    assert updated.startswith("intro")
    assert updated.endswith("outro")


def test_inject_missing_markers_raises() -> None:
    with pytest.raises(ValueError, match="missing"):
        inject("no markers here", "X", "block")


def test_snippet_self_uses_variable_builtin() -> None:
    self_runs = [run for line in SNIPPET for run in line if run.text == "self"]
    assert self_runs == [Run("self", "variable.builtin")]


def test_snippet_tokens_resolve_through_roles_or_palette() -> None:
    palette = load_palette()
    for line in SNIPPET:
        for run in line:
            fill, italic = snippet_style(palette, run.role)
            if run.role in ROLES:
                assert fill == resolve_role(palette, run.role)
                assert italic == ROLES[run.role].italic
            else:
                assert fill == resolve_palette_path(palette, run.role)
                assert italic is False


def test_snippet_style_applies_variable_builtin_italic() -> None:
    palette = load_palette()
    fill, italic = snippet_style(palette, "variable.builtin")
    assert italic is True
    assert fill == resolve_role(palette, "variable.builtin")
    assert fill != resolve_role(palette, "keyword")
