"""Ports must agree with the shared role table on the locked semantic hexes."""

from __future__ import annotations

import json
import re
import tomllib
from typing import Any

import pytest

from scripts.generate import generate
from scripts.palette import load_palette, resolve_palette_path
from scripts.roles import ANSI_SLOTS, ROLES, resolve_role, role_path
from scripts.targets import helix, herdr, ptyxis, zed, zellij
from scripts.variants import Flavor, flavors

LOCKED = ("modified", "info", "builtin", "variable.builtin")


def _hex(value: str) -> str:
    return value.lower()


@pytest.fixture(scope="module")
def vscode_by_slug() -> dict[str, dict[str, Any]]:
    return {flavor.slug: theme for flavor, theme in generate()}


@pytest.fixture(scope="module")
def zed_family() -> dict[str, Any]:
    parsed: dict[str, Any] = json.loads(zed.generate(flavors()))
    return parsed


def _vscode_token_fg(theme: dict[str, Any], name: str) -> str:
    for rule in theme["tokenColors"]:
        if rule.get("name") == name:
            foreground = rule["settings"]["foreground"]
            assert isinstance(foreground, str)
            return foreground
    raise AssertionError(f"no tokenColors rule named {name!r}")


def vscode_roles(theme: dict[str, Any]) -> dict[str, str]:
    return {
        "modified": theme["colors"]["gitDecoration.modifiedResourceForeground"],
        "info": theme["colors"]["editorInfo.foreground"],
        "builtin": _vscode_token_fg(theme, "Language Built-ins"),
        "variable.builtin": _vscode_token_fg(theme, "this, super, self, etc."),
        "ansi.blue": theme["colors"]["terminal.ansiBlue"],
    }


def helix_roles(text: str) -> dict[str, str]:
    data = tomllib.loads(text)
    palette: dict[str, str] = data["palette"]

    def scope_hex(scope: str) -> str:
        return palette[data[scope]["fg"]]

    return {
        "modified": scope_hex("diff.delta"),
        "info": scope_hex("info"),
        "builtin": scope_hex("function.builtin"),
        "variable.builtin": scope_hex("variable.builtin"),
    }


def zed_roles(family: dict[str, Any], label: str) -> dict[str, str]:
    style = next(theme["style"] for theme in family["themes"] if theme["name"] == label)
    syntax = style["syntax"]
    return {
        "modified": style["modified"],
        "info": style["info"],
        "builtin": syntax["function.builtin"]["color"],
        "variable.builtin": syntax["variable.builtin"]["color"],
        "ansi.blue": style["terminal.ansi.blue"],
    }


def _ini_hex(text: str, pattern: str, label: str) -> str:
    match = re.search(pattern, text, re.MULTILINE)
    if match is None:
        raise AssertionError(f"{label} missing from generated output")
    return match.group(1)


@pytest.mark.parametrize("flavor", flavors(), ids=lambda flavor: flavor.slug)
def test_ports_agree_on_locked_roles(
    flavor: Flavor,
    vscode_by_slug: dict[str, dict[str, Any]],
    zed_family: dict[str, Any],
) -> None:
    expected = {name: _hex(resolve_role(flavor.palette, name)) for name in LOCKED}
    vscode_hexes = {
        name: _hex(value) for name, value in vscode_roles(vscode_by_slug[flavor.slug]).items()
    }
    helix_hexes = {name: _hex(value) for name, value in helix_roles(helix.generate(flavor)).items()}
    zed_hexes = {name: _hex(value) for name, value in zed_roles(zed_family, flavor.label).items()}
    ptyxis_blue = _hex(_ini_hex(ptyxis.generate(flavor), r"^Color4=(#[0-9A-Fa-f]{6})$", "Color4"))
    herdr_teal = _hex(_ini_hex(herdr.generate(flavor), r'^teal\s+=\s+"(#[0-9A-Fa-f]{6})"', "teal"))
    ansi_blue = _hex(resolve_palette_path(flavor.palette, "ansi.blue"))

    for name in LOCKED:
        assert vscode_hexes[name] == expected[name], name
        assert helix_hexes[name] == expected[name], name
        assert zed_hexes[name] == expected[name], name

    assert vscode_hexes["ansi.blue"] == ansi_blue
    assert zed_hexes["ansi.blue"] == ansi_blue
    assert ptyxis_blue == ansi_blue
    assert herdr_teal == expected["builtin"]
    # Zellij has no syntax-role table; still generate so a mapping edit cannot
    # silently break the KDL renderer.
    assert flavor.slug in zellij.generate(flavor)


@pytest.mark.parametrize("flavor", flavors(), ids=lambda flavor: flavor.slug)
def test_variable_builtin_is_italic(
    flavor: Flavor,
    vscode_by_slug: dict[str, dict[str, Any]],
    zed_family: dict[str, Any],
) -> None:
    assert ROLES["variable.builtin"].italic
    vscode_rule = next(
        rule
        for rule in vscode_by_slug[flavor.slug]["tokenColors"]
        if rule.get("name") == "this, super, self, etc."
    )
    assert "italic" in vscode_rule["settings"]["fontStyle"]

    helix_theme = tomllib.loads(helix.generate(flavor))
    assert "italic" in helix_theme["variable.builtin"]["modifiers"]

    zed_style = next(
        theme["style"] for theme in zed_family["themes"] if theme["name"] == flavor.label
    )
    assert zed_style["syntax"]["variable.builtin"]["font_style"] == "italic"


def test_role_paths_exist_in_both_palettes() -> None:
    for palette in (load_palette(), load_palette("palette-light.json")):
        for name in ROLES:
            resolve_role(palette, name)


def test_ansi_slots_are_palette_paths_not_roles() -> None:
    assert len(ANSI_SLOTS) == 16
    assert all(not name.startswith("ansi.") for name in ROLES)
    for palette in (load_palette(), load_palette("palette-light.json")):
        for slot in ANSI_SLOTS:
            resolve_palette_path(palette, f"ansi.{slot}")


def test_unknown_role_raises() -> None:
    with pytest.raises(ValueError, match="unknown role"):
        role_path("nope.nothing")
    with pytest.raises(ValueError, match="unknown role"):
        resolve_role({}, "nope.nothing")
    with pytest.raises(ValueError, match="unknown role"):
        role_path("ansi.blue")
