"""Pilot tests for the standalone Deploy view (run_deploy / FtpClient mocked)."""

from __future__ import annotations

from pathlib import Path

import pytest
from textual.widgets import ContentSwitcher, DataTable, Input, Label

import mkpfs_tui.screens.deploy as deploy_screen
from mkpfs_tui.app import MkpfsTuiApp
from mkpfs_tui.config import FtpConfig
from mkpfs_tui.deploy.deployer import DeployResult
from mkpfs_tui.deploy.ftp import FtpTarget
from mkpfs_tui.screens.deploy import DeployView
from mkpfs_tui.widgets.path_field import PathField
from mkpfs_tui.widgets.result_panel import ResultPanel


async def test_fields_prefill_from_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(deploy_screen, "load", lambda: FtpConfig(host="10.0.0.9", port=1337, path="/p/", user="ps5"))
    app = MkpfsTuiApp()
    async with app.run_test() as pilot:
        app.query_one("#work", ContentSwitcher).current = "deploy"
        await pilot.pause()
        view = app.query_one("#deploy", DeployView)
        assert view.query_one("#deploy-host", Input).value == "10.0.0.9"
        assert view.query_one("#deploy-port", Input).value == "1337"


async def test_save_default_persists(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(deploy_screen, "load", lambda: FtpConfig())
    saved: dict[str, FtpConfig] = {}
    monkeypatch.setattr(deploy_screen, "save", lambda cfg: saved.setdefault("cfg", cfg))
    app = MkpfsTuiApp()
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#work", ContentSwitcher).current = "deploy"
        await pilot.pause()
        view = app.query_one("#deploy", DeployView)
        view.query_one("#deploy-host", Input).value = "1.2.3.4"
        await pilot.click("#deploy-save")
        await pilot.pause()
        assert saved["cfg"].host == "1.2.3.4"


async def test_deploy_success_shows_note(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(deploy_screen, "load", lambda: FtpConfig(host="h"))
    monkeypatch.setattr(
        deploy_screen,
        "run_deploy",
        lambda opts, **kw: DeployResult(True, "/p/img.exfat", 123),
    )
    local = tmp_path / "img.exfat"
    local.write_bytes(b"\0" * 10)
    app = MkpfsTuiApp()
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#work", ContentSwitcher).current = "deploy"
        await pilot.pause()
        view = app.query_one("#deploy", DeployView)
        view.query_one("#deploy-file", PathField).value = str(local)
        await pilot.pause()
        await pilot.click("#deploy-run")
        await pilot.pause()
        notes = [str(label.content) for label in view.query_one("#deploy-result", ResultPanel).query(Label)]
        assert any("Deployed" in note for note in notes)


async def test_refresh_populates_table(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(deploy_screen, "load", lambda: FtpConfig(host="h"))

    class _Client:
        def test_connect(self, target: FtpTarget) -> str | None:
            return None

        def list_dir(self, target: FtpTarget, path: str) -> list[tuple[str, int]]:
            return [("a.exfat", 100), ("b.exfat", 200)]

    monkeypatch.setattr(deploy_screen, "FtpClient", lambda: _Client())
    app = MkpfsTuiApp()
    async with app.run_test(size=(120, 40)) as pilot:
        app.query_one("#work", ContentSwitcher).current = "deploy"
        await pilot.pause()
        view = app.query_one("#deploy", DeployView)
        await pilot.click("#deploy-refresh")
        await pilot.pause()
        assert view.query_one("#deploy-listing", DataTable).row_count == 2
