# mkpfs-tui

[![CI](https://github.com/ClaudioVarandas/mkpfs-tui/actions/workflows/ci.yml/badge.svg)](https://github.com/ClaudioVarandas/mkpfs-tui/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License: GPL-3.0-or-later](https://img.shields.io/badge/license-GPL--3.0--or--later-green)](LICENSE)

A [Textual](https://textual.textualize.io/) terminal UI for [mkpfs](https://pypi.org/project/mkpfs/) —
**pack, inspect, verify, tree, unpack, and build raw dumps to exFAT** from a single sidebar-driven app. Every
operation has its own view with file/directory pickers, live progress, and a result panel that surfaces
warnings and errors without ever leaving the terminal.

> mkpfs-tui is a third-party frontend. It pins `mkpfs` as a dependency and never modifies it.

**Contents:** [Screenshots](#screenshots) · [Operations](#operations) · [Requirements](#requirements) ·
[Install](#install) · [Usage](#usage) · [Build exFAT](#build-exfat) · [Contributing](#contributing) · [License](#license)

---

## Operations

| Operation | What it does |
|-----------|--------------|
| **Pack**       | Build a PFS image from a source **folder** or **file** (compression, signing, encryption, dry-run). |
| **Inspect**    | Show an image's header, inode/dir/file counts, sizes, and checksums in a table. |
| **Verify**     | Validate an image's structure and checksums — optionally against a source tree or expected CRC32 / manifest. |
| **Tree**       | Browse the file tree stored inside an image. |
| **Unpack**     | Extract an image to a target directory, with progress and a files/dirs/bytes summary. |
| **Build exFAT** | Turn a PS5 dump folder into a `.exfat` image for ShadowMountPlus — adaptive cluster, param.json-derived name/label. |

---

## Screenshots

**About** — the welcome screen:

![mkpfs-tui — the About / welcome screen](https://raw.githubusercontent.com/ClaudioVarandas/mkpfs-tui/master/screenshots/about.png)

**Pack** — build an image from a folder or file:

![mkpfs-tui — the Pack view](https://raw.githubusercontent.com/ClaudioVarandas/mkpfs-tui/master/screenshots/pack.png)

**Inspect** — header, counts, sizes, and checksums:

![mkpfs-tui — the Inspect view](https://raw.githubusercontent.com/ClaudioVarandas/mkpfs-tui/master/screenshots/inspect.png)

**Verify** — structure / checksum checks with a PASS/FAIL banner:

![mkpfs-tui — the Verify view](https://raw.githubusercontent.com/ClaudioVarandas/mkpfs-tui/master/screenshots/verify.png)

**Tree** — browse the file tree stored inside an image:

![mkpfs-tui — the Tree view](https://raw.githubusercontent.com/ClaudioVarandas/mkpfs-tui/master/screenshots/tree.png)

---

## Requirements

- **Python 3.11 or newer** (only needed for the `uvx`/`pipx` install; the Linux binary bundles its own).
- A terminal that renders modern TUIs. Most do; on Windows use **Windows Terminal** (the default on Windows 11),
  not the legacy console.
- `mkpfs` is installed automatically as a dependency — you do not install it yourself.
- **Build exFAT only:** `exfatprogs` and `rsync` must be installed on the host system, and the build step
  requires `sudo` access for the loop-mount copy (`sudo mount`). These are not needed for any other operation.

---

## Install

> Prefer a self-contained download? Grab a build from the
> [Releases](https://github.com/ClaudioVarandas/mkpfs-tui/releases) page.

The cross-platform way is via Python, using either [uv](https://docs.astral.sh/uv/) (recommended —
`uvx` runs it without installing) or [pipx](https://pipx.pypa.io/) (installs the `mkpfs-tui` command).

### Linux

```bash
# Prerequisite — uv (one line, no root):
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run it (downloads + runs in an isolated env, nothing to clean up):
uvx mkpfs-tui
```

Or with pipx — `sudo apt install pipx` (Debian/Ubuntu) / `sudo pacman -S python-pipx` (Arch), then:

```bash
pipx ensurepath        # once, then restart the shell
pipx install mkpfs-tui
mkpfs-tui
```

**No Python?** Download `mkpfs-tui-linux-x86_64.tar.gz` from the
[Releases](https://github.com/ClaudioVarandas/mkpfs-tui/releases) page, then:

```bash
tar -xzf mkpfs-tui-linux-x86_64.tar.gz
./mkpfs-tui/mkpfs-tui
```

### macOS

```bash
# Prerequisite — uv (via Homebrew or the install script):
brew install uv          # or: curl -LsSf https://astral.sh/uv/install.sh | sh

uvx mkpfs-tui
```

Or with pipx: `brew install pipx && pipx ensurepath`, then `pipx install mkpfs-tui`.
*(No prebuilt macOS binary yet — use the Python install above.)*

### Windows

Use **Windows Terminal** for a TUI. In PowerShell:

```powershell
# Prerequisite — uv:
winget install --id=astral-sh.uv  # or: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

uvx mkpfs-tui
```

Or with pipx: `py -m pip install --user pipx`, then `py -m pipx ensurepath` (restart the terminal) and
`pipx install mkpfs-tui`. *(No prebuilt Windows binary yet — use the Python install above.)*

---

## Usage

Launch the app (`uvx mkpfs-tui`, or `mkpfs-tui` if installed). You land on the **Pack** view.

### The interface

- **Left sidebar** — the six operations. Move with `↑`/`↓`; the right pane switches as you go.
- **Right pane** — the selected operation's form, run button, progress, and a result panel
  (errors in red, warnings in amber, success in green).
- **Browse…** buttons open a file/directory picker — navigate with the arrows, **Choose** to accept,
  **Cancel**/`Escape` to dismiss. You can also just type a path into the field.

### Keyboard

| Key | Action |
|-----|--------|
| `↑` / `↓` | Move in the sidebar / lists / tree |
| `Tab` / `Shift+Tab` | Move between form fields |
| `Enter` / `Space` | Activate the focused button / switch |
| `Ctrl+P` | Command palette — includes **theme switching** |
| `Escape` | Close a modal (picker / overwrite prompt) |
| `Ctrl+Q` | Quit |

### By operation

- **Pack** — choose **Folder** or **File** mode, pick the **Source** and the **Output image** path (the
  image is written *exactly* to the path you type — include the extension you want), then set options:
  PS4/PS5 version, inode width (folder mode only), compression level, CPU count, block size, and the
  switches (Compress, Case-insensitive, Signed, Encrypted, Dry run, Verify after). Press **Pack** to watch a
  live progress bar; **Cancel** stops the build. If the output already exists you'll be asked to confirm
  before it's overwritten.
- **Inspect** — point at an **Image** and press **Inspect**; the table fills with version, sizes, counts,
  and checksums.
- **Verify** — give an **Image** and, optionally, a **Source** directory and/or an expected CRC32 / manifest
  SHA-256, then press **Verify** for a **PASS/FAIL** banner plus any errors.
- **Tree** — pick an **Image** and press **Build tree** to browse its contents.
- **Unpack** — pick an **Image** and an **Output directory** and press **Unpack**. Turn on **Overwrite** to
  clear a non-empty output directory first (you'll be asked to confirm the deletion).
- **Build exFAT** — pick a **Dump folder** (a PS5 game dump directory) and an **Output** path, then press
  **Build**. The app reads `param.json` inside the dump to suggest the output filename and the exFAT volume
  label; you can override both. Choose a cluster size or leave it on **Auto** (adaptive). Tick **Verify after**
  to run `fsck.exfat` on the finished image. The pipeline is: `truncate` → `mkfs.exfat` → `sudo mount` (loop)
  → `rsync` → `umount` → optional `fsck.exfat`. ShadowMountPlus keys off the `.exfat` filename, and all game
  files are placed at the image root. Requires `exfatprogs` + `rsync` on the host; the mount step needs
  `sudo`.

### Encrypted images

Every view has an **EKPFS key** field (64 hex characters) and a **newCrypt** switch for encrypted images;
leave them blank/off for unencrypted ones. In Pack, the key is only applied when **Encrypted** is on.

---

## Build exFAT

The `build-exfat` subcommand exposes the same pipeline as the TUI view for scripting:

```bash
mkpfs-tui build-exfat <dump> -o out.exfat [--cluster auto|32K|64K|128K|256K|512K|1M] [--label LABEL] [--no-verify]
```

- `<dump>` — path to the PS5 dump folder (must contain `sce_sys/param.json`).
- `-o` / `--output` — path for the `.exfat` image to create.
- `--cluster` — exFAT cluster size; default `auto` chooses adaptively based on the dump size.
- `--label` — override the volume label (auto-derived from `param.json` if omitted).
- `--no-verify` — skip the `fsck.exfat` check after building.

**Runtime requirements:** `exfatprogs` (provides `mkfs.exfat` + `fsck.exfat`) and `rsync` must be installed.
The copy step mounts the image via a loop device — `sudo` is required for that step. The output `.exfat`
filename is what ShadowMountPlus uses to identify the title; all game files are placed at the image root.

---

## Contributing

Issues and PRs are welcome. The project uses [`uv`](https://docs.astral.sh/uv/) for everything.

### Set up

```bash
git clone https://github.com/ClaudioVarandas/mkpfs-tui
cd mkpfs-tui
uv sync                                              # creates .venv with deps + dev tools
uv run textual run --dev mkpfs_tui.app:MkpfsTuiApp   # run the app (or: uv run python -m mkpfs_tui)
```

Tip: run `uv run textual console` in a second pane to see logs/tracebacks from the `--dev` app.

### Test & lint

```bash
./run-tests.sh        # ruff format + ruff check --fix + pytest (what to run before committing)
uv run pytest         # tests only
```

Tests use Textual's `App.run_test()` Pilot harness with `pytest-asyncio` in auto mode. CI runs
lint + tests (check-mode) on every push and PR.

### Conventions

- **`uv` only** — `uv sync`, `uv run …`; never `pip` or a global Python.
- Type hints everywhere, **Google-style docstrings**, `from __future__ import annotations` at the top of
  every module, prefer `X | None` over `Optional`. **ruff is law** (config in `pyproject.toml`).
- **The mkpfs boundary (most important rule):** all imports of and calls to `mkpfs.*` live in the single
  module **`mkpfs_tui/mkpfs_runner.py`**, which exposes the app's own value types. No other module imports
  mkpfs. When you depend on new mkpfs surface, add an assertion to `tests/test_mkpfs_contract.py` so an
  upstream change fails loudly.
- **Updating the pinned mkpfs:** `uv lock --upgrade-package mkpfs`, run the tests (including the contract
  test), then commit.

See [`CHANGELOG.md`](CHANGELOG.md) for release history. The architecture and the per-milestone build plans
are kept outside the repo (in the author's planning notes).

---

## License

[GPL-3.0-or-later](LICENSE). mkpfs-tui imports `mkpfs`, which is GPLv3, so the combined work is GPL.
