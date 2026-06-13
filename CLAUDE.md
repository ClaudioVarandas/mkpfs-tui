# mkpfs-tui — conventions

A [Textual](https://textual.textualize.io/) terminal UI over the third-party `mkpfs` library
(pack / inspect / verify / tree / unpack PlayStation PFS images). Feature-complete; published on PyPI as
`mkpfs-tui`, plus a Linux binary on GitHub Releases.

## Working agreement

- **Git: ask first.** Never `git commit`, `git push`, or `git tag` without explicit permission.
- **`uv` only** — `uv sync`, `uv run …`, `./run-tests.sh`. Never call `pip` or a global python.

## Commands

- Run the app: `uv run textual run --dev mkpfs_tui.app:MkpfsTuiApp` (or `uv run python -m mkpfs_tui`);
  `uv run textual console` in a second pane shows logs.
- Tests + lint: `./run-tests.sh` (ruff format + ruff check --fix + pytest). Tests only: `uv run pytest`.
- Build / release: `uv build`; releases are tag-driven — `git tag vX.Y.Z` triggers `release.yml`
  (PyPI via OIDC Trusted Publishing + a Linux PyInstaller binary).

## Style

Type hints everywhere; Google-style docstrings; prefer `X | None` over `Optional`;
`from __future__ import annotations` at the top of every module. **ruff is law** (config in `pyproject.toml`).

## The mkpfs boundary (most important rule)

- mkpfs is a **pinned, read-only dependency** (`mkpfs>=0.0.8,<0.1.0`) — never edit it.
- ALL imports of / calls to `mkpfs.*` live in the single module **`mkpfs_tui/mkpfs_runner.py`**, which
  exposes the app's own value types. No other module imports mkpfs.
- When you depend on new mkpfs surface, add an assertion to `tests/test_mkpfs_contract.py` so an upstream
  change fails loudly. Updating mkpfs: `uv lock --upgrade-package mkpfs`, run tests (incl. the contract test).

## Layout

- `app.py` — app shell + `main()` (+ the frozen-binary self-dispatch for packaging).
- `mkpfs_runner.py` — the mkpfs boundary: value types + operation functions (`inspect_image`, `verify_image`,
  `read_tree`, `unpack_image`, `run_pack`) + the `UiProgress` adapter.
- `screens/` — the five views (Inspect/Verify/Tree subclass `ReadView`; Pack and Unpack are plain
  `Container`s) + `confirm.py` (overwrite modal) + `picker.py` (file/dir picker).
- `widgets/` — `path_field`, `result_panel`, `sidebar`. `messages.py` — worker→view messages.
  `models.py` — `PackOptions` + `build_pack_argv`. `progress_parser.py` — pack stderr parsing.

## Tests

Textual `App.run_test()` Pilot harness, `pytest-asyncio` auto mode (async tests, no decorator). Runner logic
is tested with duck-typed fakes; only `test_mkpfs_contract.py` imports real mkpfs; pack's `run_pack` is tested
with a fake Popen plus one real-subprocess smoke.

## Docs

Design and planning docs live **outside the repo** at `~/Documents/cv/mkpfs-tui/`
(`design.md` = as-built design, `original-plan.md`, `superpowers/plans/`). The repo keeps `README.md`,
`CHANGELOG.md`, this file, and `LICENSE`.
