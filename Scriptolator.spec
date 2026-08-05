# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_all


edge_tts_datas, edge_tts_binaries, edge_tts_hiddenimports = collect_all(
    "edge_tts"
)
azure_datas, azure_binaries, azure_hiddenimports = collect_all(
    "azure.cognitiveservices.speech"
)
keyring_datas, keyring_binaries, keyring_hiddenimports = collect_all(
    "keyring"
)

project_root = Path(SPECPATH)
source_root = project_root / "src" / "scriptalator"
resources_root = source_root / "resources"
docs_root = project_root / "docs"

analysis = Analysis(
    [str(source_root / "main.py")],
    pathex=[str(source_root)],
    binaries=[
        *edge_tts_binaries,
        *azure_binaries,
        *keyring_binaries,
    ],
    datas=[
        (
            str(resources_root),
            "resources",
        ),
        (
            str(docs_root),
            "docs",
        ),
        *edge_tts_datas,
        *azure_datas,
        *keyring_datas,
    ],
    hiddenimports=[
        *edge_tts_hiddenimports,
        *azure_hiddenimports,
        *keyring_hiddenimports,
        "keyring.backends.Windows",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

python_archive = PYZ(analysis.pure)

executable = EXE(
    python_archive,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="Scriptolator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(resources_root / "scriptolator.ico"),
)
