# PyInstaller onedir spec for mkpfs-tui.
# Build: uv run pyinstaller mkpfs-tui.spec   ->   dist/mkpfs-tui/mkpfs-tui
from PyInstaller.utils.hooks import collect_all, collect_submodules

datas = [("mkpfs_tui/styles.tcss", "mkpfs_tui")]
binaries = []
hiddenimports = collect_submodules("mkpfs") + [
    # mkpfs_tui.exfat.cli and mkpfs_tui.deploy.cli are reached only via the runtime string
    # dispatch in app.main(); PyInstaller cannot trace them statically, so declare explicitly.
    "mkpfs_tui.exfat.cli",
    "mkpfs_tui.deploy.cli",
]

for pkg in ("textual", "rich"):
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(pkg)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden

a = Analysis(
    ["mkpfs_tui/__main__.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="mkpfs-tui",
    console=True,
    disable_windowed_traceback=False,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="mkpfs-tui")
