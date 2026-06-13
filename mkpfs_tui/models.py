"""Form value objects: PackOptions and its mapping to mkpfs CLI argv."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PackOptions:
    """Pack form values. Defaults mirror mkpfs's own CLI defaults."""

    mode: str  # "folder" or "file"
    source: str
    output: str
    pfs_version: str = "PS5"
    inode_bits: int = 32
    block_size: str = "auto"
    threshold_gain: int = 0
    compression_level: int = 9
    cpu_count: int = 0
    min_compress_size: int = 0
    ekpfs_key: str = ""
    compress: bool = True
    signed: bool = False
    encrypted: bool = False
    dry_run: bool = False
    verify: bool = False
    case_insensitive: bool = True


def build_pack_argv(opts: PackOptions) -> list[str]:
    """Build the ``mkpfs pack`` argv, emitting flags only when non-default.

    Args:
        opts: The pack form values.

    Returns:
        argv after the interpreter/module (i.e. starts with "pack"), suitable for
        ``[sys.executable, "-m", "mkpfs", *argv]``.
    """
    argv: list[str] = ["pack", opts.mode, opts.source, opts.output]
    argv.append("--no-adjust-output-file-extension")
    if not opts.compress:
        argv.append("--no-compress")
    # PS5 is mkpfs's own default, so emit --version only for PS4.
    if opts.pfs_version != "PS5":
        argv += ["--version", opts.pfs_version]
    if opts.mode == "folder" and opts.inode_bits != 32:
        argv += ["--inode-bits", str(opts.inode_bits)]
    if opts.block_size and opts.block_size != "auto":
        argv += ["--block-size", opts.block_size]
    if opts.threshold_gain:
        argv += ["--threshold-gain", str(opts.threshold_gain)]
    if opts.compression_level != 9:
        argv += ["--compression-level", str(opts.compression_level)]
    if opts.cpu_count:
        argv += ["--cpu-count", str(opts.cpu_count)]
    if opts.min_compress_size:
        argv += ["--min-compress-size", str(opts.min_compress_size)]
    if not opts.case_insensitive:
        argv.append("--case-sensitive")
    if opts.signed:
        argv.append("--signed")
    if opts.encrypted:
        argv.append("--encrypted")
    if opts.encrypted and opts.ekpfs_key.strip():
        argv += ["--ekpfs-key", opts.ekpfs_key.strip()]
    if opts.dry_run:
        argv.append("--dry-run")
    if opts.verify:
        argv.append("--verify")
    return argv
