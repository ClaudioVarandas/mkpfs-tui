"""Derive the output filename + exFAT volume label from a PS5 dump's param.json.

SMP identifies images by the .exfat filename (not the label), so the filename is
the meaningful output; the label is set for cosmetics and capped at exFAT's 11
characters. Reads are defensive — any missing/garbage param.json falls back to the
dump directory name.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

_ILLEGAL = re.compile(r'[\\/:*?"<>|\x00-\x1f]')
_LABEL_MAX = 11


@dataclass(frozen=True)
class ParamInfo:
    """The fields lifted from sce_sys/param.json."""

    title_id: str
    title: str
    version: str


def _extract_title(data: dict[str, object]) -> str:
    """Pull a human title from localizedParameters, else a top-level titleName."""
    localized = data.get("localizedParameters")
    if isinstance(localized, dict):
        default = localized.get("defaultLanguage")
        keys = [default, "en-US", *localized.keys()]
        for key in keys:
            entry = localized.get(key) if isinstance(key, str) else None
            if isinstance(entry, dict):
                name = entry.get("titleName")
                if isinstance(name, str) and name.strip():
                    return name.strip()
    name = data.get("titleName")
    return name.strip() if isinstance(name, str) and name.strip() else ""


def read_param(dump: Path) -> ParamInfo | None:
    """Parse sce_sys/param.json, or None if absent/unreadable/uninformative.

    Args:
        dump: The dump folder root.

    Returns:
        A ParamInfo when at least a title id or title is found, else None.
    """
    path = dump / "sce_sys" / "param.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    title_id = str(data.get("titleId") or "").strip()
    version = str(data.get("contentVersion") or data.get("masterVersion") or "").strip()
    title = _extract_title(data)
    if not (title_id or title):
        return None
    return ParamInfo(title_id=title_id, title=title, version=version)


def _sanitize(text: str) -> str:
    """Strip exFAT-illegal characters and collapse whitespace."""
    return re.sub(r"\s+", " ", _ILLEGAL.sub("", text)).strip()


def suggest_filename(info: ParamInfo | None, dump: Path) -> str:
    """Suggest the output .exfat filename (basename only).

    Args:
        info: Parsed param info, or None to fall back to the dump name.
        dump: The dump folder (its name is the fallback stem).

    Returns:
        A sanitized basename ending in ``.exfat``.
    """
    if info is None:
        return f"{_sanitize(dump.name) or 'image'}.exfat"
    if info.title_id and info.title:
        core = f"{info.title_id} - {info.title}"
    else:
        core = info.title_id or info.title or dump.name
    if info.version:
        core = f"{core} ({info.version})"
    return f"{_sanitize(core) or 'image'}.exfat"


def suggest_label(info: ParamInfo | None, dump: Path) -> str:
    """Suggest the volume label (≤ 11 chars): title id, else title, else dump name."""
    if info is not None and info.title_id:
        base = info.title_id
    elif info is not None and info.title:
        base = info.title
    else:
        base = dump.name
    return _sanitize(base)[:_LABEL_MAX].strip()
