"""The mkpfs-tui application shell."""

from __future__ import annotations

import multiprocessing
import os
import sys
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import ContentSwitcher, Footer, Header

from mkpfs_tui import mkpfs_runner
from mkpfs_tui.screens.about import AboutView
from mkpfs_tui.screens.build_exfat import BuildExfatView
from mkpfs_tui.screens.deploy import DeployView
from mkpfs_tui.screens.inspect import InspectView
from mkpfs_tui.screens.pack import PackView
from mkpfs_tui.screens.picker import DirectoryPickerScreen
from mkpfs_tui.screens.tree import TreeView
from mkpfs_tui.screens.unpack import UnpackView
from mkpfs_tui.screens.verify import VerifyView
from mkpfs_tui.widgets.path_field import PathField
from mkpfs_tui.widgets.sidebar import Sidebar


class MkpfsTuiApp(App[None]):
    """Sidebar-driven TUI: the five mkpfs operations plus an exFAT image builder."""

    # NOTE(M6): when frozen with PyInstaller, styles.tcss must be declared as a data file in the .spec.
    CSS_PATH = "styles.tcss"
    TITLE = "mkpfs-tui by ClaudioVarandas"
    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [("ctrl+q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        """Lay out header, sidebar + content switcher, and footer."""
        yield Header(show_clock=True)
        with Horizontal():
            yield Sidebar(id="sidebar")
            with ContentSwitcher(initial="about", id="work"):
                yield AboutView(id="about")
                yield PackView(id="pack")
                yield InspectView(id="inspect")
                yield VerifyView(id="verify")
                yield TreeView(id="tree")
                yield UnpackView(id="unpack")
                yield BuildExfatView(id="build")
                yield DeployView(id="deploy")
        yield Footer()

    def on_mount(self) -> None:
        """Apply the default theme once the app is mounted."""
        self.theme = "tokyo-night"

    def on_sidebar_action_selected(self, event: Sidebar.ActionSelected) -> None:
        """Switch the visible view when a sidebar action is chosen."""
        self.query_one("#work", ContentSwitcher).current = event.view_id

    def on_path_field_browse_requested(self, event: PathField.BrowseRequested) -> None:
        """Open the picker for a Browse request and write the result back."""
        field_id = event.field_id

        def write_back(path: str | None) -> None:
            if path is not None:
                self.query_one(f"#{field_id}", PathField).value = path

        self.push_screen(DirectoryPickerScreen(want=event.want), write_back)


def main() -> None:
    """Console-script entry point.

    Handles three pre-TUI concerns: multiprocessing's spawn bootstrap, the
    self-dispatch into the bundled mkpfs CLI (pack subprocess), and the
    ``build-exfat`` subcommand. Otherwise it runs the TUI.
    """
    multiprocessing.freeze_support()
    if os.environ.get("MKPFS_TUI_EXEC_MKPFS"):
        raise SystemExit(mkpfs_runner.run_mkpfs_cli())
    if len(sys.argv) > 1 and sys.argv[1] == "build-exfat":
        from mkpfs_tui.exfat import cli as exfat_cli

        raise SystemExit(exfat_cli.main(sys.argv[2:]))
    if len(sys.argv) > 1 and sys.argv[1] == "deploy":
        from mkpfs_tui.deploy import cli as deploy_cli

        raise SystemExit(deploy_cli.main(sys.argv[2:]))
    MkpfsTuiApp().run()
