<!-- GENERATED HERO START (npm run build — do not edit by hand) -->
<div align="center">

<img src="https://github.com/chapmandu/rust-in-peace/raw/main/assets/banner.png" alt="Rust in Peace — a dark theme for VS Code" width="1280"/>

<br/>

**A dark theme for VS Code, inspired by the album art of Megadeth's 1990 metal masterpiece, _Rust in Peace_.**

[![CI](https://github.com/chapmandu/rust-in-peace/actions/workflows/ci.yml/badge.svg)](https://github.com/chapmandu/rust-in-peace/actions/workflows/ci.yml)
[![Marketplace](https://flat.badgen.net/vs-marketplace/v/chapmandu.rust-in-peace?label=marketplace&labelColor=0a0e22&color=2a5ca8)](https://marketplace.visualstudio.com/items?itemName=chapmandu.rust-in-peace)
[![Installs](https://flat.badgen.net/vs-marketplace/i/chapmandu.rust-in-peace?label=installs&labelColor=0a0e22&color=391565)](https://marketplace.visualstudio.com/items?itemName=chapmandu.rust-in-peace)

<br/>

</div>
<!-- GENERATED HERO END -->

<br/>

## Colour Palette

The complete palettes, including ANSI terminal colours, live in [`src/palette.json`](https://github.com/chapmandu/rust-in-peace/blob/main/src/palette.json) (dark) and [`src/palette-light.json`](https://github.com/chapmandu/rust-in-peace/blob/main/src/palette-light.json) (Dawn Patrol).

<!-- GENERATED PALETTE START (npm run build — do not edit by hand) -->
<div align="center">

<br/>

<img src="https://github.com/chapmandu/rust-in-peace/raw/main/assets/Megadeth-RustInPeace.jpg" alt="Rust in Peace album cover" width="260"/>

_Hand-picked from the record's rusted, cobalt-blue cover art._

<br/>

<table>
<tr>
<td align="center" width="50%"><strong>Rust in Peace</strong><br/><img src="https://github.com/chapmandu/rust-in-peace/raw/main/assets/generated/rust-in-peace.png" alt="Rust in Peace" width="400"/></td>
<td align="center" width="50%"><strong>Hangar 18</strong><br/><img src="https://github.com/chapmandu/rust-in-peace/raw/main/assets/generated/rust-in-peace-hangar-18.png" alt="Rust in Peace Hangar 18" width="400"/></td>
</tr>
</table>

<br/>

<table>
<tr>
<td align="center" width="50%"><strong>Polaris</strong><br/><img src="https://github.com/chapmandu/rust-in-peace/raw/main/assets/generated/rust-in-peace-polaris.png" alt="Rust in Peace Polaris" width="400"/></td>
<td align="center" width="50%"><strong>Dawn Patrol</strong><br/><img src="https://github.com/chapmandu/rust-in-peace/raw/main/assets/generated/rust-in-peace-dawn-patrol.png" alt="Rust in Peace Dawn Patrol" width="400"/></td>
</tr>
</table>

<br/>

</div>
<!-- GENERATED PALETTE END -->

<br/>

## Installation

Install straight from the [**Visual Studio Marketplace**](https://marketplace.visualstudio.com/items?itemName=chapmandu.rust-in-peace), or from inside the editor:

1. Open the **Extensions** sidebar in VS Code — `View → Extensions`
2. Search for `Megadeth` _(curse you, rust-lang!!!)_
3. Click **Install**
4. `Preferences: Color Theme` (or `File → Preferences → Theme → Color Theme`) and pick **Rust in Peace**, **Rust in Peace Hangar 18**, **Rust in Peace Polaris**, or **Rust in Peace Dawn Patrol**

<br/>

## Companion themes

The VS Code theme isn't the only target. Matching themes for other tools are generated into [`ports/`](https://github.com/chapmandu/rust-in-peace/tree/main/ports). Every target ships all four variants — core, Hangar 18, Polaris, and Dawn Patrol (light) — as separate files, except Zed, whose single file is a theme family carrying all four:

| Tool                                               | Generated files                                                                                                          |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| [Helix](https://helix-editor.com/)                 | [`ports/helix/*.toml`](https://github.com/chapmandu/rust-in-peace/tree/main/ports/helix)                   |
| [Herdr](https://herdr.dev/)                        | [`ports/herdr/*.toml`](https://github.com/chapmandu/rust-in-peace/tree/main/ports/herdr)                   |
| [Zed](https://zed.dev/)                            | [`ports/zed/rust-in-peace.json`](https://github.com/chapmandu/rust-in-peace/blob/main/ports/zed/rust-in-peace.json) |
| [Zellij](https://zellij.dev/)                      | [`ports/zellij/*.kdl`](https://github.com/chapmandu/rust-in-peace/tree/main/ports/zellij)                  |
| [Ptyxis](https://gitlab.gnome.org/chergert/ptyxis) | [`ports/ptyxis/*.palette`](https://github.com/chapmandu/rust-in-peace/tree/main/ports/ptyxis)              |

Copy the relevant file into your tool's theme directory, then select `rust-in-peace` (or a variant slug). Run `just build-ports` to regenerate them all after a palette change.

> Herdr has no standalone theme files — its files are config fragments to merge into `~/.config/herdr/config.toml`, recolouring the `tokyo-night` base theme (`tokyo-night-day` for Dawn Patrol).

<br/>

## Contributing

To work on the theme:

1. Clone this repo and open it in VS Code
2. Run `just setup` (or `mise install`, `uv sync`, and `npm ci`) to provision the toolchain
3. Open `View → Run`
4. Click **Launch Theme** (or **Launch Theme (with extensions)**) — this opens a second VS Code window
5. Target scopes with the **Developer: Inspect Editor Tokens and Scopes** command
6. Edit `src/rust-in-peace.yml` and run `npm run build`; changes appear live in the window from step 4

Colours live in `src/palette.json` and `src/palette-light.json`; `src/rust-in-peace.yml` maps them onto VS Code keys via `{{group.key}}` placeholders. Edit the palette to shift a colour everywhere at once.

> Please include **before & after** screenshots of your changes in pull requests.

<details>
<summary><strong>Maintainer & publishing notes</strong></summary>

### Recipes

Local tasks run through [`just`](https://github.com/casey/just) — run `just` to list them all.

| Recipe               | Purpose                                                      |
| -------------------- | ------------------------------------------------------------ |
| `just setup`         | Provision the toolchain (mise) and install Python/npm dependencies |
| `just check`         | Run the full code-quality suite (lint, types, tests + coverage, dead code, duplication, secrets) |
| `just build`         | Regenerate theme JSON, companion ports, and README art       |
| `just build-ports`  | Regenerate the companion themes (Helix, Herdr, Zed, Zellij, Ptyxis) |
| `just install`       | Build, package, and install the extension into local VS Code |
| `just publish-patch` | Bump the patch version, tag, and push to publish             |
| `just publish-minor` | Bump the minor version, tag, and push to publish             |

A tag push drafts a [release](https://github.com/chapmandu/rust-in-peace/releases); publishing the draft deploys the release VSIX to the Marketplace. Global Azure DevOps PATs stop working 1 Dec 2026; confirm the `VSCE_PAT` repo secret is org-scoped or replace it before then.

</details>

<br/>

---

<div align="center">

Also check out the Slayer [**Reign in Blood**](https://marketplace.visualstudio.com/items?itemName=chapmandu.reign-in-blood) theme.

</div>
