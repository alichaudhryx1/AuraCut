# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller build for AuraCut (Windows .exe).

Built on GitHub Actions (see .github/workflows/build-windows-exe.yml), never
on a Mac or Linux machine: a Windows .exe can only be built on Windows.
Run:  pyinstaller auracut.spec
Output: dist/AuraCut.exe - one file, double-click to start.
"""
import os

from PyInstaller.utils.hooks import collect_all

datas = [
    ("web", "web"),                    # the whole app UI (pages, brand, scripts)
    ("studio/fonts", "studio/fonts"),  # caption fonts, copied into the data folder
]
# ffmpeg.exe is downloaded by the workflow and placed next to this file
# before the build. A local build without it still works, but the .exe
# then needs ffmpeg installed on the machine.
if os.path.exists("ffmpeg.exe"):
    datas.append(("ffmpeg.exe", "."))

# sherpa-onnx (speech to text) is loaded dynamically, so collect all of it:
# code, data files and shared libraries.
try:
    _sherpa_datas, _sherpa_binaries, _sherpa_hiddenimports = collect_all("sherpa_onnx")
except Exception:
    _sherpa_datas, _sherpa_binaries, _sherpa_hiddenimports = [], [], []
datas += _sherpa_datas
binaries = _sherpa_binaries

a = Analysis(
    ["auracut_main.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        "sherpa_onnx",
        "uvicorn",
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.loops.asyncio",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.protocols.http.httptools_impl",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.protocols.websockets.wsproto_impl",
        "uvicorn.protocols.websockets.websockets_impl",
        "uvicorn.protocols.websockets.websockets_sansio_impl",
        "multipart",
        "sqlalchemy.dialects.sqlite",
        "psycopg",
        "psycopg_binary",
    ]
    + _sherpa_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "PyQt5", "PyQt6", "PySide2", "PySide6"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="AuraCut",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    # Keep the console window: it shows the address, and closing it stops AuraCut.
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
