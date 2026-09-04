"""Check theme colour keys against the VS Code theme-color reference.

Run as `python -m scripts.lint` (wrapped by `just lint`; network-dependent).
Keys the theme sets that the reference no longer lists fail the run; keys
left at VS Code defaults are a single INFO count unless `--verbose`.

Design: supported keys are scraped from markdown list items
("- `key`: description") in the vscode-docs source. An empty scrape fails
loudly rather than passing.
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request

from scripts.generate import generate

THEME_COLOR_REFERENCE_URL = (
    "https://raw.githubusercontent.com/microsoft/vscode-docs/main/api/references/theme-color.md"
)
FETCH_TIMEOUT_SECONDS = 20

# List items of the form `- `activityBar.background`: description`.
_KEY_RE = re.compile(r"^- `([A-Za-z][\w.]+)`:", re.MULTILINE)

# Setting names that can appear in backticks but are not theme colour keys.
NOT_THEME_KEYS = frozenset(
    {
        "workbench.colorCustomizations",
        "editor.tokenColorCustomizations",
    }
)

LEVEL_COLORS = {
    "INFO": "\x1b[36m",  # cyan
    "WARN": "\x1b[33m",  # yellow
    "ERROR": "\x1b[31m",  # red
}
RESET = "\x1b[0m"


def log(level: str, message: str) -> None:
    """Print a colour-coded log line (errors go to stderr)."""
    line = f"{LEVEL_COLORS[level]}{level}{RESET}: {message}"
    print(line, file=sys.stderr if level == "ERROR" else sys.stdout)


def fetch_theme_color_reference(
    url: str = THEME_COLOR_REFERENCE_URL,
    timeout: float = FETCH_TIMEOUT_SECONDS,
) -> str:
    """Fetch the theme-color reference; fail loudly on timeout or network error."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:  # noqa: S310 — fixed https URL
            return str(response.read().decode("utf-8"))
    except (TimeoutError, urllib.error.URLError) as exc:
        raise RuntimeError(
            f"Failed to fetch VS Code theme-color reference from {url}: {exc}"
        ) from exc


def parse_theme_keys(source: str) -> set[str]:
    """Extract theme keys from markdown list items; raise if none match."""
    keys = {key for key in _KEY_RE.findall(source) if key not in NOT_THEME_KEYS}
    if not keys:
        raise RuntimeError(
            "No theme keys found in the VS Code theme-color reference; "
            "maybe the docs format has changed?"
        )
    return keys


def scrape_theme_available_keys() -> set[str]:
    """Fetch and parse the supported colour keys from the markdown reference."""
    return parse_theme_keys(fetch_theme_color_reference())


def report_theme_keys(
    supported_keys: set[str],
    theme_keys: set[str],
    *,
    verbose: bool = False,
) -> int:
    """Log unset and unsupported keys. Return 1 if any theme key is unsupported."""
    unset_keys = sorted(supported_keys - theme_keys)
    if verbose:
        for key in unset_keys:
            log("INFO", f'"{key}" not set; using VS Code\'s default')
    else:
        log("INFO", f"{len(unset_keys)} theme keys left at VS Code defaults")

    unsupported_keys = sorted(theme_keys - supported_keys)
    for key in unsupported_keys:
        log("WARN", f'"{key}" is unsupported, probably deprecated')

    if unsupported_keys:
        log("ERROR", f"{len(unsupported_keys)} unsupported theme key(s); see warnings above")
        return 1
    return 0


def main(argv: list[str] | None = None) -> None:
    """Fetch the live reference and exit 1 if the theme sets unsupported keys."""
    parser = argparse.ArgumentParser(
        description="Check theme keys against the VS Code theme-color reference."
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="List every unset key instead of a count.",
    )
    args = parser.parse_args(argv)

    supported_keys = scrape_theme_available_keys()
    # Every flavor resolves the same YAML mapping, so any one carries the keys.
    _, base_theme = generate()[0]
    sys.exit(report_theme_keys(supported_keys, set(base_theme["colors"]), verbose=args.verbose))


if __name__ == "__main__":
    main()
