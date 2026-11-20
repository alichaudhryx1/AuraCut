"""Settings for this computer, chosen in the dashboard (Settings, Computer): which speech model listens,
and how many clips render at once. Saved in spec.json in the data folder; what .env says wins over what the
dashboard saved, and the dashboard value wins over the built-in default.

    PEAKCUT_ASR_ENGINE      parakeet | fw-base | fw-small (which speech model listens)
    PEAKCUT_FW_MODEL        base | small (the faster-whisper size; only when the engine is a faster-whisper one)
    PEAKCUT_RENDER_WORKERS  1 | 2 | 4 (how many clips render at once; 0 or unset = the dashboard's choice)

The file follows the same shape as ai.json and apps.json: one JSON file in the data folder, read again only
when it changes, so a running server picks up a new choice without a restart. It holds no secrets.
Nothing here needs a signed-in user: background threads and tests read it too, so it never asks ctx."""
import json
import os
import threading
from pathlib import Path

from . import config

# The speech models to pick from. need_mb is the most memory the model itself holds while it works, measured
# on this machine (upper end of what was seen, so the warning on the settings page stays on the safe side):
# Parakeet peaked at about 1.0 GB, faster-whisper base at 350-450 MB, faster-whisper small at 650-900 MB.
ASR_ENGINES = {
    "fw-small": {"label": "faster-whisper small",
                 "blurb": "The most accurate listener here. Best on accented speech.",
                 "need_mb": 900},
    "fw-base": {"label": "faster-whisper base",
                "blurb": "Small and quick. Good on most speech, uses the least memory.",
                "need_mb": 450},
    "parakeet": {"label": "Parakeet 0.6b",
                 "blurb": "The built-in listener. Good on clear speech, struggles with strong accents and game noise.",
                 "need_mb": 1000},
}
ASR_DEFAULT = "fw-small"

# How many clips render at once. need_mb is what one clip's encode holds while it runs, measured from a
# single-worker render (the ffmpeg step peaked at 331 MB), rounded up a little for safety.
WORKER_NEED_MB = 350
WORKER_OPTIONS = [
    {"n": 1, "label": "Single", "blurb": "One clip at a time. The safe choice for 8 GB of RAM or a slow machine."},
    {"n": 2, "label": "Dual", "blurb": "Two clips at once. Needs about 16 GB of RAM."},
    {"n": 4, "label": "Quad", "blurb": "Four clips at once. Needs about 32 GB of RAM and plenty of processor cores."},
]
WORKERS_DEFAULT = 1

_lock = threading.Lock()
_saved = {"at": None, "data": {}}


def _file():
    return config.DATA_DIR / "spec.json"


def _from_dashboard() -> dict:
    """What was saved from the dashboard, read again only when the file changes."""
    f = _file()
    try:
        at = f.stat().st_mtime_ns
    except OSError:
        at = 0
    if _saved["at"] != at:
        try:
            data = json.loads(f.read_text(encoding="utf-8")) if at else {}
        except (OSError, ValueError):
            data = {}
        _saved.update(at=at, data=data if isinstance(data, dict) else {})
    return _saved["data"]


def _env_asr():
    """The speech engine .env asks for, if it names a real one."""
    v = (config.env("PEAKCUT_ASR_ENGINE", "") or "").strip().lower()
    if v in ASR_ENGINES:
        return v
    v = (config.env("PEAKCUT_FW_MODEL", "") or "").strip().lower()
    if v in ("base", "small"):
        return "fw-" + v
    return ""


def _env_workers():
    """The render count .env asks for, if it names a real one (0 or unset means: let the dashboard decide)."""
    try:
        n = int(str(config.env("PEAKCUT_RENDER_WORKERS", "") or "").strip() or 0)
    except (TypeError, ValueError):
        return 0
    return n if 1 <= n <= 8 else 0


def asr_engine() -> str:
    """Which speech model listens: .env first, then the dashboard, then the default."""
    env = _env_asr()
    if env:
        return env
    saved = _from_dashboard().get("asr_engine")
    if saved in ASR_ENGINES:
        return saved
    return ASR_DEFAULT


def asr_engine_from() -> str:
    """Where the speech choice came from: env, saved, or default. The page shows this, so nobody wonders
    why a choice they made is not the one in use."""
    if _env_asr():
        return "env"
    if _from_dashboard().get("asr_engine") in ASR_ENGINES:
        return "saved"
    return "default"


def fw_model() -> str:
    """The faster-whisper size in use: base or small. .env wins, then the chosen engine, then small."""
    v = (config.env("PEAKCUT_FW_MODEL", "") or "").strip().lower()
    if v in ("base", "small"):
        return v
    return "base" if asr_engine() == "fw-base" else "small"


def render_workers() -> int:
    """.env first, then the dashboard, then one worker. Always a plain number the pool can use."""
    n = _env_workers()
    if n:
        return n
    try:
        n = int(_from_dashboard().get("render_workers") or 0)
    except (TypeError, ValueError):
        n = 0
    return max(1, min(8, n)) if n else WORKERS_DEFAULT


def render_workers_from() -> str:
    if _env_workers():
        return "env"
    if _from_dashboard().get("render_workers") in (1, 2, 4):
        return "saved"
    return "default"


def current() -> dict:
    return {"asr_engine": asr_engine(), "render_workers": render_workers()}


def _fw_cached(size: str) -> bool:
    """Is this faster-whisper size already downloaded on this computer?"""
    base = Path(os.environ.get("HF_HOME") or Path.home() / ".cache" / "huggingface" / "hub")
    d = base / f"models--Systran--faster-whisper-{size}"
    return any((d / "snapshots").glob("*/model.bin")) if d.is_dir() else False


def _fw_installed() -> bool:
    try:
        import faster_whisper  # noqa: F401
        return True
    except ImportError:
        return False


def _parakeet_installed() -> bool:
    from . import fetch_model
    return fetch_model.ready()


def _engine_can_run(engine: str) -> bool:
    """Can this engine start here: the model is on the computer (faster-whisper downloads its model on
    first use, so it counts as runnable when the package is installed)."""
    if engine == "parakeet":
        return _parakeet_installed()
    return _fw_installed()


def effective_asr_engine() -> tuple:
    """The engine transcription should actually use: the chosen one when it can run, else the first one
    that can, in the order small, base, Parakeet. Returns (engine, fell_back). It never raises: when
    nothing can run, the chosen engine is returned and the caller reports it plainly instead of
    crashing the job."""
    want = asr_engine()
    if _engine_can_run(want):
        return want, False
    for cand in ("fw-small", "fw-base", "parakeet"):
        if cand != want and _engine_can_run(cand):
            return cand, True
    return want, False


def public() -> dict:
    """What the settings page may see: the choices in use, the options, and whether each one can run here."""
    fw_ok = _fw_installed()
    opts = []
    for eid, info in ASR_ENGINES.items():
        if eid == "parakeet":
            installed = _parakeet_installed()
            note = "Ready." if installed else "Not downloaded yet. AuraCut downloads it (about 480 MB) the first time it is needed."
        else:
            size = "small" if eid == "fw-small" else "base"
            installed = fw_ok
            if not fw_ok:
                note = "Not installed on this computer, so this choice falls back to Parakeet."
            elif _fw_cached(size):
                note = "Ready."
            else:
                note = f"Downloads on first use (about {240 if size == 'small' else 75} MB)."
        opts.append({"id": eid, "label": info["label"], "blurb": info["blurb"], "need_mb": info["need_mb"],
                     "installed": installed, "note": note})
    return {"asr_engine": asr_engine(), "asr_engine_from": asr_engine_from(), "fw_model": fw_model(),
            "render_workers": render_workers(), "render_workers_from": render_workers_from(),
            "asr_options": opts, "worker_options": WORKER_OPTIONS, "worker_need_mb": WORKER_NEED_MB}


def save(asr_engine_id, workers) -> dict:
    """Save the choice made in the dashboard. Either value may be left out to keep what is there."""
    d = _from_dashboard()
    if asr_engine_id is not None:
        e = str(asr_engine_id or "").strip().lower()
        if e not in ASR_ENGINES:
            raise ValueError("Choose one of the speech models in the list.")
        d["asr_engine"] = e
    if workers is not None:
        try:
            n = int(workers)
        except (TypeError, ValueError):
            raise ValueError("Choose Single, Dual or Quad for rendering.")
        if n not in (1, 2, 4):
            raise ValueError("Choose Single, Dual or Quad for rendering.")
        d["render_workers"] = n
    with _lock:
        f = _file()
        tmp = f.with_suffix(".tmp")
        tmp.write_text(json.dumps({"asr_engine": d.get("asr_engine", ASR_DEFAULT),
                                   "render_workers": d.get("render_workers", WORKERS_DEFAULT)}, indent=1),
                       encoding="utf-8")
        tmp.replace(f)
        _saved["at"] = None
    return public()
