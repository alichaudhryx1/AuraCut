"""Launcher for the frozen (PyInstaller) AuraCut build.

Only used by the Windows .exe. The normal way to run AuraCut is still
`python -m studio.server`; this file just sets up the frozen runtime first:

- videos, clips and settings live in an "AuraCutData" folder next to the
  .exe, so they survive restarts (a frozen app's own folder is temporary)
- a bundled ffmpeg.exe is put on PATH when the build included one
"""
import os
import sys
from pathlib import Path


def _prepare_frozen() -> None:
    if not getattr(sys, "frozen", False):
        return
    exe_dir = Path(sys.executable).resolve().parent
    # Keep everything AuraCut saves next to the .exe, not in a temp folder.
    os.environ.setdefault("PEAKCUT_DATA", str(exe_dir / "AuraCutData"))
    # ffmpeg bundled inside the .exe (PyInstaller onefile) or next to it.
    bundle_dir = getattr(sys, "_MEIPASS", None)
    for folder in (bundle_dir, exe_dir):
        if folder and (Path(folder) / "ffmpeg.exe").exists():
            os.environ["PATH"] = str(folder) + os.pathsep + os.environ.get("PATH", "")
            break


_prepare_frozen()

from studio.server import main  # noqa: E402

if __name__ == "__main__":
    main()
