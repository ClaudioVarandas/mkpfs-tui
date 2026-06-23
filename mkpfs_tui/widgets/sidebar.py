"""Sidebar navigation listing the mkpfs actions plus Build exFAT and Deploy."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import Label, ListItem, ListView

ACTIONS: list[tuple[str, str]] = [
    ("pack", "Pack"),
    ("inspect", "Inspect"),
    ("verify", "Verify"),
    ("tree", "Tree"),
    ("unpack", "Unpack"),
    ("build", "Build exFAT"),
    ("deploy", "Deploy"),
    ("about", "About"),
]


class NavItem(ListItem):
    """A sidebar entry that remembers which view it selects."""

    def __init__(self, view_id: str, label: str) -> None:
        """Store the target view id and render the label.

        Args:
            view_id: ContentSwitcher child id this entry activates.
            label: Human-readable text shown in the list.
        """
        super().__init__(Label(label))
        self.view_id = view_id


class Sidebar(Vertical):
    """Vertical list of actions; emits ActionSelected on highlight."""

    class ActionSelected(Message):
        """Posted when the highlighted action changes."""

        def __init__(self, view_id: str) -> None:
            """Carry the selected view id.

            Args:
                view_id: ContentSwitcher child id to show.
            """
            self.view_id = view_id
            super().__init__()

    def compose(self) -> ComposeResult:
        """Build the ListView of NavItems."""
        yield ListView(*(NavItem(view_id, label) for view_id, label in ACTIONS))

    def on_mount(self) -> None:
        """Set the initial highlighted item to About (the last entry)."""
        lv = self.query_one(ListView)
        lv.index = len(ACTIONS) - 1

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Translate a highlight into an ActionSelected message."""
        event.stop()
        if isinstance(event.item, NavItem):
            self.post_message(self.ActionSelected(event.item.view_id))
