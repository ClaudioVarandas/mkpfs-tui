"""Tests for deriving the output filename + volume label from param.json."""

from __future__ import annotations

import json
from pathlib import Path

from mkpfs_tui.exfat.naming import read_param, suggest_filename, suggest_label

_PARAM = {
    "titleId": "PPSA01234",
    "contentVersion": "01.00",
    "localizedParameters": {
        "defaultLanguage": "en-US",
        "en-US": {"titleName": "My Game: Deluxe"},
    },
}


def _dump(tmp_path: Path, param: object | None) -> Path:
    dump = tmp_path / "DUMP"
    (dump / "sce_sys").mkdir(parents=True)
    if param is not None:
        (dump / "sce_sys" / "param.json").write_text(json.dumps(param))
    return dump


def test_read_param_full(tmp_path: Path) -> None:
    info = read_param(_dump(tmp_path, _PARAM))
    assert info is not None
    assert info.title_id == "PPSA01234"
    assert info.title == "My Game: Deluxe"
    assert info.version == "01.00"


def test_filename_strips_illegal_chars(tmp_path: Path) -> None:
    info = read_param(_dump(tmp_path, _PARAM))
    # ':' is illegal in exFAT names and is removed; parens are kept.
    assert suggest_filename(info, tmp_path / "DUMP") == "PPSA01234 - My Game Deluxe (01.00).exfat"


def test_label_is_title_id_within_11_chars(tmp_path: Path) -> None:
    info = read_param(_dump(tmp_path, _PARAM))
    assert suggest_label(info, tmp_path / "DUMP") == "PPSA01234"


def test_missing_param_falls_back_to_dump_name(tmp_path: Path) -> None:
    dump = _dump(tmp_path, None)  # no param.json written
    assert read_param(dump) is None
    assert suggest_filename(None, dump) == "DUMP.exfat"
    assert suggest_label(None, dump) == "DUMP"


def test_garbage_param_returns_none(tmp_path: Path) -> None:
    dump = tmp_path / "D"
    (dump / "sce_sys").mkdir(parents=True)
    (dump / "sce_sys" / "param.json").write_text("{ not json")
    assert read_param(dump) is None


def test_label_truncated_to_11(tmp_path: Path) -> None:
    info = read_param(_dump(tmp_path, {"titleName": "Super Long Game Name"}))
    # No titleId -> label from title, truncated to 11 and stripped.
    assert suggest_label(info, tmp_path / "DUMP") == "Super Long"


from mkpfs_tui.exfat.naming import PRESETS  # noqa: E402  (extends Part A imports)


def test_preset_ppsa_is_title_id_only(tmp_path: Path) -> None:
    info = read_param(_dump(tmp_path, _PARAM))
    assert suggest_filename(info, tmp_path / "DUMP", preset="ppsa") == "PPSA01234.exfat"


def test_preset_title_omits_version(tmp_path: Path) -> None:
    info = read_param(_dump(tmp_path, _PARAM))
    assert suggest_filename(info, tmp_path / "DUMP", preset="title") == "PPSA01234 - My Game Deluxe.exfat"


def test_preset_version_is_default(tmp_path: Path) -> None:
    info = read_param(_dump(tmp_path, _PARAM))
    assert suggest_filename(info, tmp_path / "DUMP") == suggest_filename(info, tmp_path / "DUMP", preset="version")


def test_lowercase_toggle(tmp_path: Path) -> None:
    info = read_param(_dump(tmp_path, _PARAM))
    assert suggest_filename(info, tmp_path / "DUMP", lowercase=True) == "ppsa01234 - my game deluxe (01.00).exfat"


def test_unknown_preset_falls_back_to_version(tmp_path: Path) -> None:
    info = read_param(_dump(tmp_path, _PARAM))
    assert suggest_filename(info, tmp_path / "DUMP", preset="bogus") == suggest_filename(info, tmp_path / "DUMP")


def test_presets_table() -> None:
    assert PRESETS == ("ppsa", "title", "version")
