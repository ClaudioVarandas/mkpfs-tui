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

PRESETS: tuple[str, str, str] = ("ppsa", "title", "version")


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


def _filename_core(info: ParamInfo | None, dump: Path, preset: str) -> str:
    """Build the pre-sanitization filename stem for the chosen preset.

    Args:
        info: Parsed param info, or None to fall back to the dump name.
        dump: The dump folder (its name is the fallback stem).
        preset: One of ``PRESETS`` (ppsa/title/version).

    Returns:
        The raw stem (illegal chars not yet stripped).
    """
    if info is None:
        return dump.name
    if preset == "ppsa":
        return info.title_id or info.title or dump.name
    base = (
        f"{info.title_id} - {info.title}"
        if info.title_id and info.title
        else (info.title_id or info.title or dump.name)
    )
    if preset == "version" and info.version:
        return f"{base} ({info.version})"
    return base


def suggest_filename(info: ParamInfo | None, dump: Path, *, preset: str = "version", lowercase: bool = False) -> str:
    """Suggest the output .exfat filename (basename only).

    Args:
        info: Parsed param info, or None to fall back to the dump name.
        dump: The dump folder (its name is the fallback stem).
        preset: Naming preset — ``ppsa`` (id only), ``title`` (id + title), or
            ``version`` (id + title + version, the default). Unknown values
            fall back to ``version``.
        lowercase: When True, lowercase the whole stem.

    Returns:
        A sanitized basename ending in ``.exfat``.
    """
    if preset not in PRESETS:
        preset = "version"
    core = _sanitize(_filename_core(info, dump, preset)) or "image"
    if lowercase:
        core = core.lower()
    return f"{core}.exfat"


def suggest_label(info: ParamInfo | None, dump: Path) -> str:
    """Suggest the volume label (≤ 11 chars): title id, else title, else dump name."""
    if info is not None and info.title_id:
        base = info.title_id
    elif info is not None and info.title:
        base = info.title
    else:
        base = dump.name
    return _sanitize(base)[:_LABEL_MAX].strip()
