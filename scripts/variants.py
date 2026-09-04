"""Lighter variants of the dark palette.

A VariantSpec drives three HSL transforms: tapered lightness lift for neutrals,
desaturate-and-darken for accents (contrast-guarded), and both for UI chrome.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from typing import Literal, NamedTuple

from coloraide import Color

from scripts.palette import Palette, load_palette, resolve_palette_path


@dataclass(frozen=True)
class VariantSpec:
    """Parameters of one lighter variant."""

    label: str
    """Theme display name, e.g. "Rust in Peace Hangar 18"."""
    slug: str
    """Filename slug, e.g. "rust-in-peace-hangar-18"."""
    lift_a: float
    """Neutral lift at L=0, in HSL lightness points (0–100 scale)."""
    lift_b: float
    """Per-lightness-point taper of the neutral lift."""
    desat: float
    """Proportional saturation cut for accents (0–1)."""
    darken: float
    """Maximum lightness reduction for the brightest accents."""


VARIANTS = [
    VariantSpec(
        label="Rust in Peace Hangar 18",
        slug="rust-in-peace-hangar-18",
        lift_a=3.9,
        lift_b=0.045,
        desat=0.12,
        darken=2,
    ),
    VariantSpec(
        label="Rust in Peace Polaris",
        slug="rust-in-peace-polaris",
        lift_a=9.4,
        lift_b=0.117,
        desat=0.24,
        darken=4,
    ),
]


class Flavor(NamedTuple):
    """A theme flavor: a display name and appearance bound to a resolved palette."""

    label: str
    """Theme display name, e.g. "Rust in Peace Hangar 18"."""
    slug: str
    """Filename / theme-key slug, e.g. "rust-in-peace-hangar-18"."""
    appearance: Literal["dark", "light"]
    palette: Palette


def flavors() -> list[Flavor]:
    """Build the four theme flavors, dark to light, from the two hand-designed palettes."""
    palette = load_palette()
    light_palette = load_palette("palette-light.json")
    return [
        Flavor("Rust in Peace", "rust-in-peace", "dark", palette),
        *(
            Flavor(spec.label, spec.slug, "dark", transform_palette(palette, spec))
            for spec in VARIANTS
        ),
        Flavor("Rust in Peace Dawn Patrol", "rust-in-peace-dawn-patrol", "light", light_palette),
    ]


# ANSI keys that belong to the neutral ladder rather than the accent set.
_NEUTRAL_ANSI_KEYS = frozenset({"black", "brightBlack", "white", "brightWhite"})

# WCAG contrast target for accents on the editor background.
_ACCENT_MIN_CONTRAST = 4.5

ColorTransform = Callable[[str], str]


def _with_hsl(hex_colour: str, mutate: Callable[[list[float]], None]) -> str:
    """Mutate a colour's [hue, saturation, lightness] (s and l in 0–1), clamped back to hex."""
    coords = list(Color(hex_colour).convert("hsl").coords())
    mutate(coords)
    coords[1] = min(1.0, max(0.0, coords[1]))
    coords[2] = min(1.0, max(0.0, coords[2]))
    return Color("hsl", coords).convert("srgb").to_string(hex=True)


def contrast(fg: str, bg: str) -> float:
    """WCAG 2.1 contrast ratio between two colours (1–21, symmetric)."""
    return Color(fg).contrast(bg, method="wcag21")


def _lift(spec: VariantSpec, hex_colour: str) -> str:
    """Tapered lightness lift: strongest on dark surfaces, ~zero by the text end."""

    def mutate(hsl: list[float]) -> None:
        hsl[2] += max(0.0, spec.lift_a - spec.lift_b * hsl[2] * 100) / 100

    return _with_hsl(hex_colour, mutate)


def _mute(spec: VariantSpec, orig_bg: str, new_bg: str, hex_colour: str) -> str:
    """Accent muting: proportional desaturation, slight darkening of bright colours.

    Guarded so an accent never ends up with less contrast against the variant's
    background than it had originally (capped at the WCAG 4.5:1 target) —
    darker accents are lightened back up instead.
    """

    def mutate(hsl: list[float]) -> None:
        hsl[1] -= spec.desat * hsl[1]
        hsl[2] -= (spec.darken * max(0.0, (hsl[2] * 100 - 50) / 38)) / 100

    def lighten(hsl: list[float]) -> None:
        hsl[2] += 0.01

    floor = min(contrast(hex_colour, orig_bg), _ACCENT_MIN_CONTRAST)
    result = _with_hsl(hex_colour, mutate)
    while contrast(result, new_bg) < floor:
        lightened = _with_hsl(result, lighten)
        if lightened == result:  # lightness clamped at 1.0 — the floor is unreachable
            break
        result = lightened
    return result


def _lift_and_desat(spec: VariantSpec, hex_colour: str) -> str:
    """Chrome rises in step with the surfaces without getting louder."""

    def mutate(hsl: list[float]) -> None:
        hsl[2] += max(0.0, spec.lift_a - spec.lift_b * hsl[2] * 100) / 100
        hsl[1] -= spec.desat * hsl[1]

    return _with_hsl(hex_colour, mutate)


def _map_group(group: str | Palette, transform: ColorTransform) -> str | Palette:
    """Apply a colour transform to every colour in a palette subtree."""
    if isinstance(group, str):
        return transform(group)
    return {key: _map_group(value, transform) for key, value in group.items()}


def transform_palette(palette: Palette, spec: VariantSpec) -> Palette:
    """Apply a variant's lightening formula to the whole palette."""
    neutral: ColorTransform = partial(_lift, spec)
    orig_bg = resolve_palette_path(palette, "bg.base")
    accent: ColorTransform = partial(_mute, spec, orig_bg, neutral(orig_bg))
    chrome: ColorTransform = partial(_lift_and_desat, spec)

    result: Palette = {}
    for group_name, group in palette.items():
        if group_name in ("bg", "fg"):
            result[group_name] = _map_group(group, neutral)
        elif group_name == "ui":
            result[group_name] = _map_group(group, chrome)
        elif group_name == "ansi" and isinstance(group, dict):
            result[group_name] = {
                key: _map_group(value, neutral if key in _NEUTRAL_ANSI_KEYS else accent)
                for key, value in group.items()
            }
        else:
            result[group_name] = _map_group(group, accent)
    return result
