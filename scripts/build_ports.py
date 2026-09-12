"""Write ports/ for every registered target; Zed is one family JSON."""

from __future__ import annotations

import shutil
from collections.abc import Callable
from typing import NamedTuple

from scripts.palette import REPO_ROOT
from scripts.targets import helix, herdr, ptyxis, zed, zellij
from scripts.variants import Flavor, flavors

PORTS_DIR = REPO_ROOT / "ports"


class Target(NamedTuple):
    """A downstream theme target derived from the shared palettes."""

    name: str
    dir: str
    ext: str
    generate: Callable[[Flavor], str]


TARGETS = [
    Target("Helix", "helix", "toml", helix.generate),
    Target("Herdr", "herdr", "toml", herdr.generate),
    Target("Ptyxis", "ptyxis", "palette", ptyxis.generate),
    Target("Zellij", "zellij", "kdl", zellij.generate),
]


def main() -> None:
    """Render every target theme, in all four flavors, into ports/."""
    shutil.rmtree(PORTS_DIR, ignore_errors=True)
    PORTS_DIR.mkdir()

    all_flavors = flavors()
    for target in TARGETS:
        for flavor in all_flavors:
            file = f"{target.dir}/{flavor.slug}.{target.ext}"
            out_path = PORTS_DIR / file
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(target.generate(flavor), encoding="utf-8")
            print(f"{target.name} -> ports/{file}")

    # Zed themes are families: one file carries all four flavors.
    out_path = PORTS_DIR / "zed" / "rust-in-peace.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(zed.generate(all_flavors), encoding="utf-8")
    print("Zed -> ports/zed/rust-in-peace.json")


if __name__ == "__main__":
    main()
