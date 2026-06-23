"""Tests for the directory/file picker modal."""

from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Button, DirectoryTree, Input

from mkpfs_tui.screens.picker import DirectoryPickerScreen


class _Host(App[None]):
    def __init__(self, want: str = "file", root: str | None = None) -> None:
        super().__init__()
        self._want = want
        self._root = root
        self.picked: str | None = "UNSET"

    def compose(self) -> ComposeResult:
        yield Button("open", id="open")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "open":
            self.push_screen(DirectoryPickerScreen(want=self._want, root=self._root), self._got)

    def _got(self, value: str | None) -> None:
        self.picked = value


async def test_choose_returns_selected_path(tmp_path: Path) -> None:
    target = tmp_path / "image.pfs"
    target.write_text("x")
    app = _Host(want="file")
    async with app.run_test() as pilot:
        await pilot.click("#open")
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, DirectoryPickerScreen)
        screen.set_selection(str(target))  # simulate a tree file-selection
        await pilot.click("#picker-choose")
        await pilot.pause()
        assert app.picked == str(target)


async def test_cancel_returns_none(tmp_path: Path) -> None:
    app = _Host(want="dir")
    async with app.run_test() as pilot:
        await pilot.click("#open")
        await pilot.pause()
        await pilot.click("#picker-cancel")
        await pilot.pause()
        assert app.picked is None


async def test_navigate_then_choose_returns_file(tmp_path: Path) -> None:
    """Navigate to a file with arrow keys and click Choose — must return the path.

    This tests the highlight-tracking path: no Enter/click on the file node,
    just arrow-key navigation followed by the Choose button.
    """
    target = tmp_path / "sample.pfs"
    target.write_text("data")

    app = _Host(want="file", root=str(tmp_path))
    async with app.run_test() as pilot:
        await pilot.click("#open")
        # Let the screen mount and the DirectoryTree load its first level.
        await pilot.pause()
        await pilot.pause()

        screen = app.screen
        assert isinstance(screen, DirectoryPickerScreen)

        # Focus the tree so key events are routed to it.
        tree = screen.query_one(DirectoryTree)
        tree.focus()

        # Arrow down moves the highlight from the root dir node to the first
        # child (our file).  The NodeHighlighted handler should set _selection.
        await pilot.press("down")
        await pilot.pause()

        # Choose should dismiss with the highlighted file path.
        await pilot.click("#picker-choose")
        await pilot.pause()

        assert app.picked == str(target)


async def test_up_button_reroots_to_parent(tmp_path: Path) -> None:
    """The Up button re-roots the tree to the parent of the current root."""
    sub = tmp_path / "a" / "b"
    sub.mkdir(parents=True)
    app = _Host(want="dir", root=str(sub))
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.click("#open")
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, DirectoryPickerScreen)
        tree = screen.query_one("#picker-tree", DirectoryTree)
        assert Path(tree.path) == sub

        await pilot.click("#picker-up")
        await pilot.pause()
        assert Path(tree.path) == sub.parent  # tmp_path / "a"
        # The path box reflects the new root.
        assert Path(screen.query_one("#picker-path", Input).value) == sub.parent


async def test_path_box_reroots_to_typed_dir(tmp_path: Path) -> None:
    """Typing a directory in the path box and pressing Enter re-roots the tree."""
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    app = _Host(want="dir", root=str(tmp_path))
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.click("#open")
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, DirectoryPickerScreen)

        path_box = screen.query_one("#picker-path", Input)
        path_box.focus()
        path_box.value = str(elsewhere)
        await pilot.press("enter")
        await pilot.pause()

        assert Path(screen.query_one("#picker-tree", DirectoryTree).path) == elsewhere


async def test_path_box_expands_user_home(tmp_path: Path) -> None:
    """A ``~`` in the path box expands to the user's home directory."""
    app = _Host(want="dir", root=str(tmp_path))
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.click("#open")
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, DirectoryPickerScreen)

        path_box = screen.query_one("#picker-path", Input)
        path_box.focus()
        path_box.value = "~"
        await pilot.press("enter")
        await pilot.pause()

        assert Path(screen.query_one("#picker-tree", DirectoryTree).path) == Path.home()


async def test_invalid_path_is_ignored(tmp_path: Path) -> None:
    """Typing a non-existent path leaves the current root unchanged."""
    app = _Host(want="dir", root=str(tmp_path))
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.click("#open")
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, DirectoryPickerScreen)

        path_box = screen.query_one("#picker-path", Input)
        path_box.focus()
        path_box.value = str(tmp_path / "does-not-exist")
        await pilot.press("enter")
        await pilot.pause()

        assert Path(screen.query_one("#picker-tree", DirectoryTree).path) == tmp_path
