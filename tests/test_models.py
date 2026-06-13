"""Tests for PackOptions -> argv mapping."""

from __future__ import annotations

from mkpfs_tui.models import PackOptions, build_pack_argv


def test_defaults_emit_positionals_and_no_adjust_extension() -> None:
    opts = PackOptions(mode="folder", source="src", output="out.pfs")
    assert build_pack_argv(opts) == ["pack", "folder", "src", "out.pfs", "--no-adjust-output-file-extension"]


def test_flags_emitted_only_when_non_default() -> None:
    opts = PackOptions(
        mode="folder",
        source="src",
        output="out.pfs",
        pfs_version="PS4",
        inode_bits=64,
        block_size="65536",
        threshold_gain=5,
        compression_level=6,
        cpu_count=4,
        min_compress_size=1024,
        compress=False,
        signed=True,
        encrypted=True,
        ekpfs_key="ab" * 32,
        dry_run=True,
        verify=True,
        case_insensitive=False,
    )
    argv = build_pack_argv(opts)
    assert argv[:4] == ["pack", "folder", "src", "out.pfs"]
    assert "--no-compress" in argv
    assert argv[argv.index("--version") + 1] == "PS4"
    assert argv[argv.index("--inode-bits") + 1] == "64"
    assert argv[argv.index("--block-size") + 1] == "65536"
    assert argv[argv.index("--threshold-gain") + 1] == "5"
    assert argv[argv.index("--compression-level") + 1] == "6"
    assert argv[argv.index("--cpu-count") + 1] == "4"
    assert argv[argv.index("--min-compress-size") + 1] == "1024"
    assert "--case-sensitive" in argv
    assert "--signed" in argv
    assert "--encrypted" in argv
    assert argv[argv.index("--ekpfs-key") + 1] == "ab" * 32
    assert "--dry-run" in argv
    assert "--verify" in argv
    assert "--no-adjust-output-file-extension" in argv


def test_pfs_version_default_is_ps5_and_omitted() -> None:
    # PS5 is both the app default and mkpfs's CLI default, so --version is not emitted.
    assert PackOptions(mode="folder", source="s", output="o").pfs_version == "PS5"
    assert "--version" not in build_pack_argv(PackOptions(mode="folder", source="s", output="o"))
    # PS4 is non-default and must be passed explicitly.
    ps4 = build_pack_argv(PackOptions(mode="folder", source="s", output="o", pfs_version="PS4"))
    assert ps4[ps4.index("--version") + 1] == "PS4"


def test_ekpfs_key_only_with_encrypted() -> None:
    opts = PackOptions(mode="folder", source="s", output="o", ekpfs_key="ab" * 32, encrypted=False)
    assert "--ekpfs-key" not in build_pack_argv(opts)


def test_file_mode_omits_inode_bits() -> None:
    # file mode forces inode_bits=32 in mkpfs; never emit --inode-bits for files
    opts = PackOptions(mode="file", source="f.bin", output="o.pfs", inode_bits=64)
    assert "--inode-bits" not in build_pack_argv(opts)
