"""Tests for run_deploy with a recording fake FtpClient."""

from __future__ import annotations

from pathlib import Path

from mkpfs_tui.deploy.deployer import DeployOptions, run_deploy
from mkpfs_tui.deploy.ftp import FtpTarget, TransferCancelled


class _FakeClient:
    def __init__(
        self,
        *,
        connect_error: str | None = None,
        listing: list = (),
        upload_raises: Exception | None = None,
    ) -> None:
        self.connect_error = connect_error
        self.listing = list(listing)
        self.upload_raises = upload_raises
        self.uploaded: list[str] = []

    def test_connect(self, target: object) -> str | None:
        return self.connect_error

    def list_dir(self, target: object, path: object) -> list:
        return list(self.listing)

    def upload(
        self,
        target: object,
        local: object,
        remote_name: str,
        progress_cb: object,
        should_cancel: object,
    ) -> int:
        if self.upload_raises is not None:
            raise self.upload_raises
        progress_cb(100, 100)
        self.uploaded.append(remote_name)
        return 100


def _opts(tmp_path: Path, **kw: object) -> DeployOptions:
    local = tmp_path / "img.exfat"
    local.write_bytes(b"\0" * 100)
    return DeployOptions(local_file=local, target=FtpTarget(host="h"), **kw)


def test_success(tmp_path: Path) -> None:
    client = _FakeClient()
    result = run_deploy(_opts(tmp_path), client=client)
    assert result.ok is True
    assert result.bytes_sent == 100
    assert result.remote_path == "/data/etaHEN/games/img.exfat"
    assert client.uploaded == ["img.exfat"]


def test_connect_error_is_reported(tmp_path: Path) -> None:
    result = run_deploy(_opts(tmp_path), client=_FakeClient(connect_error="refused"))
    assert result.ok is False
    assert result.errors == ("refused",)


def test_existing_file_needs_confirm(tmp_path: Path) -> None:
    client = _FakeClient(listing=[("img.exfat", 50)])
    result = run_deploy(_opts(tmp_path), client=client)
    assert result.needs_confirm is True
    assert result.ok is False
    assert client.uploaded == []  # not transferred without confirmation


def test_overwrite_skips_confirm(tmp_path: Path) -> None:
    client = _FakeClient(listing=[("img.exfat", 50)])
    result = run_deploy(_opts(tmp_path, overwrite=True), client=client)
    assert result.ok is True
    assert client.uploaded == ["img.exfat"]


def test_cancel_is_reported(tmp_path: Path) -> None:
    client = _FakeClient(upload_raises=TransferCancelled())
    result = run_deploy(_opts(tmp_path, overwrite=True), client=client)
    assert result.cancelled is True
    assert result.ok is False


def test_custom_remote_name(tmp_path: Path) -> None:
    client = _FakeClient()
    result = run_deploy(_opts(tmp_path, remote_name="renamed.exfat", overwrite=True), client=client)
    assert result.remote_path.endswith("/renamed.exfat")
    assert client.uploaded == ["renamed.exfat"]
