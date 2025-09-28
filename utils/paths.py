from pathlib import Path
import sys


def get_base_dir() -> Path:
    """
    Return the base directory for locating bundled resources.
    - In PyInstaller bundles, this is sys._MEIPASS
    - In development (source), this is the project root directory
    """
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass)
    # utils/paths.py -> project root is parent of utils
    return Path(__file__).resolve().parent.parent


def resource_path(*relative_parts: str) -> Path:
    """Join parts onto the base dir to get an absolute resource path."""
    return get_base_dir().joinpath(*relative_parts)


def get_exe_dir() -> Path:
    """Directory where the executable (or project root in dev) resides."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    # In dev, use project root (parent of utils)
    return Path(__file__).resolve().parent.parent


def get_portable_config_path() -> Path:
    """configs/config.json beside the executable (or project root in dev)."""
    return get_exe_dir() / "configs" / "config.json"


def ensure_portable_config_path() -> Path:
    """
    Ensure a portable config exists next to the executable in configs/config.json.
    If missing, seed from bundled default (resource_path). Otherwise create minimal default.
    No fallback: if the location is not writable or any I/O error occurs,
    the exception will be raised to the caller.
    """
    cfg = get_portable_config_path()
    if not cfg.exists():
        cfg.parent.mkdir(parents=True, exist_ok=True)
        default_path = resource_path("configs", "config.json")
        if default_path.exists():
            cfg.write_text(default_path.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            cfg.write_text('{"PROVIDER_CONFIG": {}, "DEFAULT_SYSTEM_PROMPT": ""}', encoding="utf-8")
    return cfg





def get_config_path() -> Path:
    """
    Unified accessor used by the app to locate the configuration file.
    Now prefers a portable config next to the executable (or project root in dev):
    <exe_dir>/configs/config.json. If missing, it is seeded from bundled default.
    """
    return ensure_portable_config_path()

