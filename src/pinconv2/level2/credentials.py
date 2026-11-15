"""Provider credential lookup without committing or printing secrets.

Resolution order:

1. process environment (``PEXELS_API_KEY`` and friends);
2. the local credential vault at ``D:\\pinaka-credentials\\secrets``;
3. the Windows user environment registry.

Only the caller receives the value. Status helpers return where the key was
found, never the key itself.
"""

from __future__ import annotations

import os
from pathlib import Path

try:  # Windows-only; the loader still works on other platforms via env/vault.
    import winreg
except ImportError:  # pragma: no cover - non-Windows
    winreg = None  # type: ignore[assignment]

ENV_FILES: dict[str, str] = {
    "PEXELS_API_KEY": "pexels-api-key",
    "UNSPLASH_ACCESS_KEY": "unsplash-access-key",
    "FREESOUND_API_KEY": "freesound-api-key",
    "PIXABAY_API_KEY": "pixabay-api-key",
    "FAL_KEY": "fal-api-key",
}

DEFAULT_VAULT = Path(r"D:\pinaka-credentials\secrets")


def _clean(value: str) -> str:
    return value.strip().strip('"').strip("'").lstrip("\ufeff").strip()


def vault_path(env_name: str) -> Path | None:
    file_name = ENV_FILES.get(env_name)
    if file_name is None:
        return None
    root = Path(os.environ.get("PINCONV2_CREDENTIAL_VAULT", str(DEFAULT_VAULT)))
    return root / file_name


def _registry_key(env_name: str) -> str | None:
    if winreg is None:
        return None
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, env_name)
    except OSError:
        return None
    if isinstance(value, str):
        cleaned = _clean(value)
        return cleaned or None
    return None


def provider_key(env_name: str) -> str | None:
    """Return the key value, or ``None``. Never log the result."""

    from_env = _clean(os.environ.get(env_name, ""))
    if from_env:
        return from_env
    path = vault_path(env_name)
    if path is not None and path.is_file():
        from_vault = _clean(path.read_text(encoding="utf-8"))
        if from_vault:
            return from_vault
    return _registry_key(env_name)


def key_status(env_name: str) -> str:
    """Return ``env``, ``vault``, ``registry`` or ``missing``."""

    if _clean(os.environ.get(env_name, "")):
        return "env"
    path = vault_path(env_name)
    if path is not None and path.is_file() and _clean(path.read_text(encoding="utf-8")):
        return "vault"
    if _registry_key(env_name):
        return "registry"
    return "missing"


def status_report() -> dict[str, str]:
    return {name: key_status(name) for name in ENV_FILES}
