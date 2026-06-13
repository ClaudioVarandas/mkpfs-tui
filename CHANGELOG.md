# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

## [0.1.2] — 2026-06-12

### Changed

- Bumped the pinned `mkpfs` floor to **`>=0.0.8`** (from `>=0.0.5`). This pulls in the upstream
  streaming/flat-memory rewrite and several correctness fixes:
  - **Flat-memory verify / tree / unpack** — mkpfs now streams each file block-by-block instead of
    loading it into RAM. Verifying a 14.5 GB image (29.6 GB logical) now peaks at ~50 MB RSS where it
    previously exhausted memory.
  - **`pack file` streams to the image by default** (the legacy spool builder is opt-in upstream).
  - **Faster post-pack verification**, a fix for **corruption on large game folders** (bad inode
    mapping), and **safe inner-image renaming** that could otherwise break mounts.

### Fixed

- **Pack** now defaults the PFS version to **PS5** (matching mkpfs's own default and the common PPSA
  target). This also fixes a mismatch where the old PS4 default emitted no `--version` flag, so mkpfs
  silently built a **PS5** image while the form read "PS4".
- **Pack** now locks compression **off in folder mode** (greyed switch + an inline note). mkpfs warns a
  directly-packed app/game folder must not be compressed — the PS console misreads compressed files
  ([mkpfs#49](https://github.com/PSBrew/MkPFS/issues/49)) — and compressed folder packing also spools up to
  the full image size into the temp folder (which failed outright on a tmpfs `/tmp`). Compression stays
  available in **file** mode (`.exfat`); folder output now auto-derives the uncompressed `.ffpfs` extension.

### Internal

- The Inspect/Tree payload-hashing gate is retained as a **speed** optimisation (skip reading the whole
  image just to inspect its structure), now that the upstream memory pressure it originally guarded
  against is gone. Comments, the OOM message, and the contract-test note were updated to match.

## [0.1.1] — 2026-06-04

### Fixed

- **File/directory picker** now returns the highlighted path on **Choose** (and accepts a file immediately
  on click/Enter) — previously arrow-navigating then Choose did nothing.
- **Inspect** and **Tree** no longer exhaust memory on images containing very large files: they skip payload
  hashing (mkpfs loads each file wholly into RAM to hash it), so they read only the structure. The CRC32 /
  manifest checksums now live in **Verify**; Inspect shows `— (run Verify)` for them.
- Selecting a non-PFS file (e.g. a raw `.exfat`) shows a clear **"Not a PFS image"** message instead of a
  low-level inode-parse error.
- Out-of-memory is reported gracefully where catchable.

### Added

- **Pack**: the Output image path auto-derives from the Source (`.ffpfsc` / `.ffpfs` by compression) and
  respects manual edits.
- **Pack**: toggles are laid out inline and the numeric fields are labelled (less vertical space, clearer).
- A **"Working…" spinner** on Inspect/Tree, and an **indeterminate progress bar + elapsed timer** on Verify.
- An **About / welcome screen** (ASCII banner, description, author, version · license · repo) shown as the
  default landing view and as a sidebar entry.
- Taller path-input fields.

### Changed

- App title is now **"mkpfs-tui by ClaudioVarandas"**.

## [0.1.0] — 2026-06-04

First public release — a [Textual](https://textual.textualize.io/) terminal UI over
[mkpfs](https://pypi.org/project/mkpfs/) exposing all five PlayStation PFS operations from one app.

### Added

- Sidebar-driven app shell: header (with clock), a `ContentSwitcher` of five views, and a footer; the
  built-in `tokyo-night` theme and the `Ctrl+P` command palette (theme switching). `Ctrl+Q` quits.
- **Inspect** — show an image's header, inode/dir/file counts, sizes, and checksums in a table.
- **Verify** — PASS/FAIL banner, with optional source-tree / expected-CRC32 / expected-manifest checks.
- **Tree** — browse the file tree stored inside an image (cycle-guarded).
- **Unpack** — extract an image to a directory in-process, with a live progress bar, a files/dirs/bytes
  summary, and a TUI-owned overwrite guard for a non-empty target.
- **Pack** — build an image from a folder or file via a streaming subprocess, with a live progress bar,
  Cancel (which terminates the child process), and an overwrite confirmation.
- A file/directory **picker** modal wired to every Browse button.
- Encryption options (EKPFS key, newCrypt) on every relevant view.

### Internal

- Anti-corruption boundary: all `mkpfs` access is confined to `mkpfs_runner.py`, guarded by a contract test
  that pins the upstream symbols and dataclass fields the adapter relies on.
- Hybrid integration: inspect/verify/tree/unpack call the mkpfs library in-process; pack shells out to a
  subprocess and parses its progress (CR/LF-aware), with the binary self-dispatching as its own mkpfs runtime
  when frozen.
- Distribution: PyPI via Trusted Publishing (OIDC) plus a Linux PyInstaller `--onedir` binary, built by a
  tag-driven release workflow; CI runs lint + tests on every push/PR.

### Requirements

- Python ≥ 3.11. Pins `mkpfs >= 0.0.5, < 0.1.0` and `textual >= 0.86`.
- Licensed GPL-3.0-or-later (it imports mkpfs, which is GPLv3).

[0.1.2]: https://github.com/ClaudioVarandas/mkpfs-tui/releases/tag/v0.1.2
[0.1.1]: https://github.com/ClaudioVarandas/mkpfs-tui/releases/tag/v0.1.1
[0.1.0]: https://github.com/ClaudioVarandas/mkpfs-tui/releases/tag/v0.1.0
