"""A modal directory/file picker wrapping Textual's DirectoryTree."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DirectoryTree, Input, Label, Tree


class DirectoryPickerScreen(ModalScreen[str | None]):
    """Pick a file or directory; dismisses with the path string, or None on cancel."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    def __init__(self, want: str = "file", root: str | None = None) -> None:
        """Build the picker.

        Args:
            want: "file" or "dir" — which selections are accepted.
            root: Starting directory (defaults to the current working directory).
        """
        super().__init__()
        self.want = want
        self._root = root or str(Path.cwd())
        self._selection: str | None = None

    def compose(self) -> ComposeResult:
        """Render the path bar, the tree, and Choose/Cancel buttons."""
        with Vertical(id="picker-box"):
            yield Label(f"Select a {self.want}")
            with Horizontal(id="picker-path-row"):
                yield Button("Up", id="picker-up")
                yield Input(value=self._root, id="picker-path", placeholder="path (type or ~ then Enter)")
            yield DirectoryTree(self._root, id="picker-tree")
            with Horizontal(id="picker-buttons"):
                yield Button("Choose", id="picker-choose", variant="primary")
                yield Button("Cancel", id="picker-cancel")

    def on_mount(self) -> None:
        """Focus the tree so arrow keys navigate immediately."""
        self.query_one("#picker-tree", DirectoryTree).focus()

    def _reroot(self, raw: str) -> None:
        """Re-root the tree at ``raw`` if it resolves to an existing directory.

        Invalid or non-directory paths are ignored (the current root stays put).
        ``~`` is expanded to the user's home directory.

        Args:
            raw: The candidate directory path (may contain ``~``).
        """
        try:
            resolved = Path(raw).expanduser().resolve()
        except OSError:
            return
        if not resolved.is_dir():
            return
        self._root = str(resolved)
        self.query_one("#picker-path", Input).value = self._root
        self.query_one("#picker-tree", DirectoryTree).path = self._root

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Re-root the tree when a path is entered in the path box.

        Args:
            event: The submit event from the path Input.
        """
        if event.input.id == "picker-path":
            self._reroot(event.value)

    def set_selection(self, path: str) -> None:
        """Set the current selection (used by the tree handlers and tests)."""
        self._selection = path

    def on_tree_node_highlighted(self, event: Tree.NodeHighlighted) -> None:  # type: ignore[type-arg]
        """Track the highlighted (cursor) node so Choose uses the current highlight.

        Sets ``_selection`` whenever the highlighted node matches ``want``:
        a file when ``want=="file"``, a directory when ``want=="dir"``.
        Nodes with no data (e.g. the root placeholder before loading) are skipped.

        Args:
            event: The highlight event carrying the newly focused node.
        """
        node = event.node
        if node.data is None:
            return
        path: Path = node.data.path
        if (self.want == "file" and not path.is_dir()) or (self.want == "dir" and path.is_dir()):
            self._selection = str(path)

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Accept a file immediately when picking a file; otherwise record it.

        Args:
            event: The file-selected event from the DirectoryTree.
        """
        if self.want == "file":
            self.dismiss(str(event.path))
        else:
            self.set_selection(str(event.path))

    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        """Record a directory selection when picking a directory.

        Args:
            event: The directory-selected event from the DirectoryTree.
        """
        if self.want == "dir":
            self.set_selection(str(event.path))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Choose dismisses with the selection; Cancel dismisses with None.

        Args:
            event: The button-pressed event.
        """
        if event.button.id == "picker-up":
            self._reroot(str(Path(self._root).parent))
        elif event.button.id == "picker-choose":
            self.dismiss(self._selection)
        elif event.button.id == "picker-cancel":
            self.dismiss(None)

    def action_cancel(self) -> None:
        """Escape cancels."""
        self.dismiss(None)
