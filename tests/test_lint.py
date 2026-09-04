from __future__ import annotations

import urllib.error
from typing import Any

import pytest

from scripts.lint import (
    FETCH_TIMEOUT_SECONDS,
    fetch_theme_color_reference,
    main,
    parse_theme_keys,
    report_theme_keys,
)

# Snippet of the vscode-docs theme-color markdown: list-item keys plus the
# prose / JSON / hex noise the parser must ignore.
THEME_COLOR_MD = """\
# Theme Color

You can customize with the `workbench.colorCustomizations` user setting.

```json
{
  "workbench.colorCustomizations": {
    "activityBar.background": "#00AA00"
  }
}
```

Color formats: `#RGB`, `#RRGGBB`.

## Base colors

- `focusBorder`: Overall border color for focused elements.
- `foreground`: Overall foreground color.
- `widget.border`: Border color of widgets.

## Editor colors

These can also be customized with the `editor.tokenColorCustomizations` setting.

- `editor.background`: Editor background color.
- `editor.foreground`: Editor default foreground color.
- `workbench.colorCustomizations`: not a theme colour key even as a list item.
"""


def test_parse_theme_keys_from_markdown_fixture() -> None:
    assert parse_theme_keys(THEME_COLOR_MD) == {
        "focusBorder",
        "foreground",
        "widget.border",
        "editor.background",
        "editor.foreground",
    }


def test_empty_scrape_fails_loudly() -> None:
    with pytest.raises(RuntimeError, match="No theme keys found"):
        parse_theme_keys("# Theme Color\n\nNo keys here, just `workbench.colorCustomizations`.\n")


def test_html_code_spans_are_not_keys() -> None:
    with pytest.raises(RuntimeError, match="No theme keys found"):
        parse_theme_keys("<code>editor.background</code>")


def test_report_counts_unset_keys(capsys: pytest.CaptureFixture[str]) -> None:
    code = report_theme_keys({"a", "b", "c"}, {"a"}, verbose=False)
    assert code == 0
    out = capsys.readouterr().out
    assert "2 theme keys left at VS Code defaults" in out
    assert '"b"' not in out


def test_report_verbose_lists_unset_keys(capsys: pytest.CaptureFixture[str]) -> None:
    code = report_theme_keys({"b", "a"}, {"a"}, verbose=True)
    assert code == 0
    out = capsys.readouterr().out
    assert '"b" not set; using VS Code\'s default' in out
    assert "theme keys left at VS Code defaults" not in out


def test_report_unsupported_keys_fail(capsys: pytest.CaptureFixture[str]) -> None:
    code = report_theme_keys({"a"}, {"a", "gone"}, verbose=False)
    assert code == 1
    captured = capsys.readouterr()
    assert '"gone" is unsupported, probably deprecated' in captured.out
    assert "1 unsupported theme key(s); see warnings above" in captured.err


class _FakeResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None


def test_fetch_passes_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_urlopen(url: str, timeout: float) -> _FakeResponse:
        captured["url"] = url
        captured["timeout"] = timeout
        return _FakeResponse(b"ok")

    monkeypatch.setattr("scripts.lint.urllib.request.urlopen", fake_urlopen)
    assert fetch_theme_color_reference() == "ok"
    assert captured["timeout"] == FETCH_TIMEOUT_SECONDS


def test_fetch_timeout_fails_loudly(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(url: str, timeout: float) -> object:
        raise TimeoutError("timed out")

    monkeypatch.setattr("scripts.lint.urllib.request.urlopen", fake_urlopen)
    with pytest.raises(RuntimeError, match="Failed to fetch"):
        fetch_theme_color_reference()


def test_fetch_network_error_fails_loudly(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(url: str, timeout: float) -> object:
        raise urllib.error.URLError("dns failed")

    monkeypatch.setattr("scripts.lint.urllib.request.urlopen", fake_urlopen)
    with pytest.raises(RuntimeError, match="Failed to fetch"):
        fetch_theme_color_reference()


def test_main_quiet_summary_and_unsupported_exit(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("scripts.lint.scrape_theme_available_keys", lambda: {"keep", "unset"})
    monkeypatch.setattr(
        "scripts.lint.generate",
        lambda: [(object(), {"colors": {"keep": "#000", "gone": "#111"}})],
    )
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "1 theme keys left at VS Code defaults" in captured.out
    assert '"unset"' not in captured.out
    assert '"gone" is unsupported' in captured.out
    assert "1 unsupported theme key(s)" in captured.err


def test_main_verbose_lists_unset_keys(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("scripts.lint.scrape_theme_available_keys", lambda: {"keep", "unset"})
    monkeypatch.setattr(
        "scripts.lint.generate",
        lambda: [(object(), {"colors": {"keep": "#000"}})],
    )
    with pytest.raises(SystemExit) as exc:
        main(["--verbose"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert '"unset" not set; using VS Code\'s default' in out
    assert "theme keys left at VS Code defaults" not in out
