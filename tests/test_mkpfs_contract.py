"""Contract test: pin the mkpfs symbols and fields mkpfs_runner relies on.

Runs on every mkpfs bump (uv lock --upgrade-package mkpfs) to catch upstream
breakage before shipping. If this goes red, fix mkpfs_runner.py, not this test.
"""

from __future__ import annotations

import inspect as _inspect

from mkpfs import consts
from mkpfs.pbar import Progress
from mkpfs.pfs import (
    BuildError,
    ParsedDirent,
    ParsedHeader,
    PFSExtractionResult,
    PFSImageInspection,
    extract_pfs_image,
    inspect_pfs_image,
    parse_ekpfs_key_hex,
    read_pfs_info,
    verify_file_payload_hashes,
    verify_pfs_image,
)


def test_inspect_pfs_image_accepts_expected_kwargs() -> None:
    params = _inspect.signature(inspect_pfs_image).parameters
    for name in ("image", "ekpfs", "new_crypt"):
        assert name in params, f"inspect_pfs_image lost kwarg {name!r}"


def test_inspection_dataclass_fields() -> None:
    fields = PFSImageInspection.__dataclass_fields__
    for name in (
        "image",
        "errors",
        "warnings",
        "size_bytes",
        "header",
        "inodes",
        "dir_inodes",
        "file_inodes",
        "compressed_files",
        "checked_files",
        "data_crc32",
        "manifest_sha256",
        "logical_file_bytes",
        "stored_file_bytes",
        "uroot_inode",
        "dirents_by_inode",
    ):
        assert name in fields, f"PFSImageInspection lost field {name!r}"
    assert isinstance(PFSImageInspection.version_label, property)


def test_parsed_header_and_dirent_fields() -> None:
    assert "block_size" in ParsedHeader.__dataclass_fields__
    assert {"inode_number", "type_code", "name"} <= set(ParsedDirent.__dataclass_fields__)


def test_consts_and_ekpfs_and_builderror() -> None:
    assert consts.DIRENT_TYPE_DIRECTORY == 3
    assert consts.DIRENT_TYPE_FILE == 2
    assert callable(parse_ekpfs_key_hex)
    assert issubclass(BuildError, Exception)


def test_verify_pfs_image_accepts_expected_kwargs() -> None:
    params = _inspect.signature(verify_pfs_image).parameters
    for name in ("image", "source", "expected_crc32", "expected_manifest_sha256", "ekpfs", "new_crypt"):
        assert name in params, f"verify_pfs_image lost kwarg {name!r}"


def test_extract_pfs_image_and_result_and_progress() -> None:
    params = _inspect.signature(extract_pfs_image).parameters
    for name in ("image", "output_path", "progress", "ekpfs", "new_crypt"):
        assert name in params, f"extract_pfs_image lost kwarg {name!r}"
    fields = PFSExtractionResult.__dataclass_fields__
    for name in ("output_path", "files_written", "directories_created", "bytes_written", "errors", "warnings"):
        assert name in fields, f"PFSExtractionResult lost field {name!r}"
    assert hasattr(Progress, "step")
    assert hasattr(Progress, "status")


def test_verify_file_payload_hashes_exists() -> None:
    # mkpfs_runner gates this global to a no-op so Inspect/Tree skip hashing — which
    # (since mkpfs 0.0.7) reads the whole image off disk, slow on huge images. The pin
    # floor is mkpfs>=0.0.8. An upstream rename of this symbol must fail here.
    assert callable(verify_file_payload_hashes)


def test_read_pfs_info_and_pfs_magic() -> None:
    assert callable(read_pfs_info)
    assert isinstance(consts.PFS_MAGIC, int)
    assert "magic" in ParsedHeader.__dataclass_fields__


def test_mkpfs_cli_main_exists() -> None:
    from mkpfs.cli import main as cli_main

    assert callable(cli_main)
