from __future__ import annotations

import os
from pathlib import Path
from threading import Lock

from dotenv import dotenv_values


_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_LOAD_LOCK = Lock()
_ENV_LOADED = False


def _read_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values = dotenv_values(path)
    return {key: value for key, value in values.items() if value is not None}


def load_environment() -> None:
    global _ENV_LOADED

    if _ENV_LOADED:
        return

    with _LOAD_LOCK:
        if _ENV_LOADED:
            return

        base_values = _read_env_file(_BACKEND_ROOT / ".env")
        app_env = (
            (os.getenv("APP_ENV") or base_values.get("APP_ENV") or "").strip().lower()
        )

        scoped_values: dict[str, str] = {}
        if app_env:
            scoped_values = _read_env_file(_BACKEND_ROOT / f".env.{app_env}")

        merged_values = {**base_values, **scoped_values}
        for key, value in merged_values.items():
            os.environ.setdefault(key, value)

        _ENV_LOADED = True
