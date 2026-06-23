"""Acceptance tests for the M1 app shell."""

from __future__ import annotations

from textual.widgets import ContentSwitcher, ListView

from mkpfs_tui.app import MkpfsTuiApp


async def test_app_starts_on_tokyo_night() -> None:
    app = MkpfsTuiApp()
    async with app.run_test():
        assert app.theme == "tokyo-night"


def test_command_palette_is_enabled() -> None:
    # Ctrl+P palette (which carries theme switching) is on by default.
    assert MkpfsTuiApp.ENABLE_COMMAND_PALETTE is True


async def test_theme_is_switchable() -> None:
    app = MkpfsTuiApp()
    async with app.run_test():
        app.theme = "nord"  # another built-in theme
        assert app.theme == "nord"


def test_app_title() -> None:
    assert MkpfsTuiApp.TITLE == "mkpfs-tui by ClaudioVarandas"


async def test_default_view_is_about() -> None:
    app = MkpfsTuiApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        switcher = app.query_one("#work", ContentSwitcher)
        assert switcher.current == "about"


async def test_sidebar_switches_every_view() -> None:
    app = MkpfsTuiApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        switcher = app.query_one("#work", ContentSwitcher)
        nav = app.query_one(ListView)
        # Setting nav.index fires ListView.Highlighted -> Sidebar.ActionSelected -> ContentSwitcher.current.
        # One pause() drains that two-hop chain because wait_for_idle polls until the app is idle.
        for index, view_id in enumerate(["pack", "inspect", "verify", "tree", "unpack", "build", "deploy", "about"]):
            nav.index = index
            await pilot.pause()
            assert switcher.current == view_id
