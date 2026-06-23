"""Tests for the sidebar navigation widget."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import ListView

from mkpfs_tui.widgets.sidebar import Sidebar


class _Host(App[None]):
    """Minimal host app that records ActionSelected view ids."""

    def __init__(self) -> None:
        super().__init__()
        self.selected: list[str] = []

    def compose(self) -> ComposeResult:
        yield Sidebar()

    def on_sidebar_action_selected(self, event: Sidebar.ActionSelected) -> None:
        self.selected.append(event.view_id)


async def test_sidebar_lists_eight_actions() -> None:
    app = _Host()
    async with app.run_test():
        assert len(app.query_one(ListView).children) == 8


def test_sidebar_has_about_entry() -> None:
    from mkpfs_tui.widgets.sidebar import ACTIONS

    view_ids = [view_id for view_id, _ in ACTIONS]
    assert "about" in view_ids
    assert view_ids[-1] == "about"


async def test_highlight_emits_matching_view_id() -> None:
    app = _Host()
    async with app.run_test() as pilot:
        nav = app.query_one(ListView)
        nav.index = 2  # third action -> "verify"
        await pilot.pause()
        assert app.selected, "expected at least one ActionSelected message"
        assert app.selected[-1] == "verify"


async def test_highlight_about_emits_about_view_id() -> None:
    from mkpfs_tui.widgets.sidebar import ACTIONS

    app = _Host()
    async with app.run_test() as pilot:
        nav = app.query_one(ListView)
        about_index = next(i for i, (vid, _) in enumerate(ACTIONS) if vid == "about")
        nav.index = about_index
        await pilot.pause()
        assert app.selected, "expected at least one ActionSelected message"
        assert app.selected[-1] == "about"
