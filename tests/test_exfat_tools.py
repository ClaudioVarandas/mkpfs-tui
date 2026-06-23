"""Tests for exFAT build pre-flight tool detection."""

from __future__ import annotations

from pytest import MonkeyPatch

import mkpfs_tui.exfat.tools as tools
from mkpfs_tui.exfat.tools import preflight


def test_all_present_returns_empty(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(tools.shutil, "which", lambda _name: "/usr/bin/x")
    assert preflight() == []


def test_reports_missing_with_hint(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(tools.shutil, "which", lambda name: None if name == "mkfs.exfat" else "/usr/bin/x")
    missing = preflight()
    assert len(missing) == 1
    assert missing[0].startswith("mkfs.exfat:")
    assert "exfatprogs" in missing[0]


def test_verify_false_skips_fsck(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(tools.shutil, "which", lambda name: None if name == "fsck.exfat" else "/usr/bin/x")
    assert preflight(verify=True)  # fsck missing -> reported
    assert preflight(verify=False) == []  # fsck not required
