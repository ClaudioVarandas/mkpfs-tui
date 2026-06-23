"""Tests for the build-exfat CLI subcommand and its app.main() dispatch."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from pytest import CaptureFixture, MonkeyPatch

import mkpfs_tui.exfat.cli as cli
from mkpfs_tui.exfat.builder import BuildResult


def test_parser_reads_all_flags() -> None:
    args = cli.build_argv_parser().parse_args(
        ["dump", "-o", "out.exfat", "--cluster", "64K", "--label", "L", "--no-verify"]
    )
    assert args.dump == Path("dump")
    assert args.output == Path("out.exfat")
    assert args.cluster == "64K"
    assert args.label == "L"
    assert args.verify is False


def test_main_success(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]) -> None:
    monkeypatch.setattr(cli, "preflight", lambda *, verify: [])
    monkeypatch.setattr(
        cli,
        "run_build",
        lambda opts: BuildResult(True, str(opts.output), 128, 65536, opts.label, ()),
    )
    rc = cli.main(["dump", "-o", "out.exfat"])
    assert rc == 0
    assert "Built" in capsys.readouterr().out


def test_main_missing_tools(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]) -> None:
    monkeypatch.setattr(cli, "preflight", lambda *, verify: ["mkfs.exfat: install exfatprogs"])
    rc = cli.main(["dump", "-o", "out.exfat"])
    assert rc == 1
    assert "mkfs.exfat" in capsys.readouterr().out


def test_main_build_failure(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]) -> None:
    monkeypatch.setattr(cli, "preflight", lambda *, verify: [])
    monkeypatch.setattr(
        cli,
        "run_build",
        lambda opts: BuildResult(False, str(opts.output), 128, 65536, opts.label, ("mount failed",)),
    )
    rc = cli.main(["dump", "-o", "out.exfat"])
    assert rc == 1
    assert "mount failed" in capsys.readouterr().out


def test_app_main_dispatches_build_exfat(monkeypatch: MonkeyPatch) -> None:
    from mkpfs_tui import app

    captured: dict[str, list[str]] = {}

    def fake_main(argv: list[str]) -> int:
        captured["argv"] = argv
        return 0

    monkeypatch.setattr("mkpfs_tui.exfat.cli.main", fake_main)
    monkeypatch.setattr(sys, "argv", ["mkpfs-tui", "build-exfat", "dump", "-o", "x.exfat"])
    monkeypatch.delenv("MKPFS_TUI_EXEC_MKPFS", raising=False)
    with pytest.raises(SystemExit) as exc:
        app.main()
    assert captured["argv"] == ["dump", "-o", "x.exfat"]
    assert exc.value.code == 0
