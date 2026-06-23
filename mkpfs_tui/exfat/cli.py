"""The ``mkpfs-tui build-exfat`` CLI subcommand (shares run_build with the TUI)."""

from __future__ import annotations

import argparse
from pathlib import Path

from mkpfs_tui.exfat.builder import BuildOptions, run_build
from mkpfs_tui.exfat.naming import read_param, suggest_label
from mkpfs_tui.exfat.sizing import CLUSTER_CHOICES
from mkpfs_tui.exfat.tools import preflight


def build_argv_parser() -> argparse.ArgumentParser:
    """Build the argument parser for ``build-exfat``."""
    parser = argparse.ArgumentParser(
        prog="mkpfs-tui build-exfat",
        description="Build a PS5 dump folder into an exFAT image for ShadowMountPlus.",
    )
    parser.add_argument("dump", type=Path, help="dump folder (its contents go to the image root)")
    parser.add_argument("-o", "--output", type=Path, required=True, help="output .exfat path")
    parser.add_argument(
        "--cluster",
        choices=list(CLUSTER_CHOICES),
        default="auto",
        help="cluster size (default: auto — 32K for small files, else 64K)",
    )
    parser.add_argument("--label", default=None, help="volume label (default: derived from param.json)")
    parser.add_argument("--no-verify", dest="verify", action="store_false", help="skip the fsck.exfat check")
    return parser


def main(argv: list[str]) -> int:
    """Run build-exfat. Returns a process exit code (0 ok, 1 on any failure)."""
    args = build_argv_parser().parse_args(argv)
    missing = preflight(verify=args.verify)
    if missing:
        print("Missing required tools:")
        for line in missing:
            print(f"  - {line}")
        return 1
    label = args.label if args.label is not None else suggest_label(read_param(args.dump), args.dump)
    opts = BuildOptions(
        dump=args.dump,
        output=args.output,
        label=label,
        cluster_override=CLUSTER_CHOICES[args.cluster],
        verify=args.verify,
    )
    result = run_build(opts)
    if result.ok:
        print(
            f"Built {result.output_path} "
            f"({result.size_mb} MB, cluster {result.cluster_bytes // 1024}K, label {result.label})"
        )
        return 0
    print(f"Build failed: {'; '.join(result.errors)}")
    return 1
