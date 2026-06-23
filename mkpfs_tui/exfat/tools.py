"""Pre-flight: report which system binaries the exFAT build needs but lacks."""

from __future__ import annotations

import shutil

_HINTS: dict[str, str] = {
    "truncate": "install coreutils",
    "mkfs.exfat": "install exfatprogs (Fedora: sudo dnf install exfatprogs)",
    "fsck.exfat": "install exfatprogs (Fedora: sudo dnf install exfatprogs)",
    "rsync": "install rsync (Fedora: sudo dnf install rsync)",
    "mount": "mount not found (util-linux)",
    "umount": "umount not found (util-linux)",
    "sudo": "sudo not found — required to mount the image for copying",
}


def preflight(*, verify: bool = True) -> list[str]:
    """List missing required binaries as ``"<tool>: <hint>"`` lines.

    Args:
        verify: When True, also require ``fsck.exfat`` for the post-build check.

    Returns:
        One line per missing tool (empty if everything needed is present).
    """
    required = ["truncate", "mkfs.exfat", "mount", "umount", "rsync", "sudo"]
    if verify:
        required.append("fsck.exfat")
    return [f"{tool}: {_HINTS[tool]}" for tool in required if shutil.which(tool) is None]
