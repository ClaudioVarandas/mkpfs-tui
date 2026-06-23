"""Orchestrate a deploy: connect, detect overwrite, then STOR with progress.

UI-free: ``run_deploy`` takes an injectable ``client`` (so tests use a fake) and a
progress callback. When the remote name already exists and ``overwrite`` is False it
returns a ``needs_confirm`` result instead of transferring — the caller (TUI modal or
CLI prompt) decides, then retries with ``overwrite=True``.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from mkpfs_tui.deploy.ftp import FtpClient, FtpTarget, TransferCancelled

ProgressCb = Callable[[int, int], None]
CancelCb = Callable[[], bool]


@dataclass(frozen=True)
class DeployOptions:
    """Inputs for one deploy."""

    local_file: Path
    target: FtpTarget
    remote_name: str | None = None
    overwrite: bool = False


@dataclass(frozen=True)
class DeployResult:
    """Outcome of a deploy."""

    ok: bool
    remote_path: str
    bytes_sent: int
    needs_confirm: bool = False
    cancelled: bool = False
    errors: tuple[str, ...] = ()


def _noop(_sent: int, _total: int) -> None:
    """Default progress sink."""


def _never() -> bool:
    """Default cancel predicate."""
    return False


def run_deploy(
    opts: DeployOptions,
    *,
    client: FtpClient | None = None,
    progress_cb: ProgressCb = _noop,
    should_cancel: CancelCb = _never,
) -> DeployResult:
    """Connect, optionally gate on overwrite, and upload ``opts.local_file``.

    Args:
        opts: Local file, target, optional remote name, overwrite flag.
        client: FTP client (injected in tests; defaults to a real FtpClient).
        progress_cb: Called as ``(bytes_sent, total_bytes)`` during transfer.
        should_cancel: Polled during transfer; True aborts with ``cancelled``.

    Returns:
        A DeployResult. ``needs_confirm`` is True (and nothing is sent) when the
        remote name exists and ``overwrite`` is False.
    """
    client = client or FtpClient()
    name = opts.remote_name or opts.local_file.name
    remote_path = f"{opts.target.path.rstrip('/')}/{name}"

    error = client.test_connect(opts.target)
    if error:
        return DeployResult(False, remote_path, 0, errors=(error,))

    if not opts.overwrite:
        try:
            existing = {entry_name for entry_name, _size in client.list_dir(opts.target, opts.target.path)}
        except Exception:  # listing is best-effort; fall through to transfer
            existing = set()
        if name in existing:
            return DeployResult(False, remote_path, 0, needs_confirm=True)

    try:
        sent = client.upload(opts.target, opts.local_file, name, progress_cb, should_cancel)
    except TransferCancelled:
        return DeployResult(False, remote_path, 0, cancelled=True)
    except Exception as exc:  # surface any ftplib/OS error as a result
        return DeployResult(False, remote_path, 0, errors=(str(exc) or exc.__class__.__name__,))

    return DeployResult(True, remote_path, sent)
