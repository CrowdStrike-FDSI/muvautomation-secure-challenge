"""Fixtures: entorno de prueba con clave y usuarios EFIMEROS (sin secretos reales)."""
import importlib
import json
import pathlib
import secrets
import sys

import pytest
from passlib.context import CryptContext

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
_ctx = CryptContext(schemes=["bcrypt"])


@pytest.fixture
def credenciales():
    """Contrasenas aleatorias generadas en cada ejecucion."""
    return {"analista": secrets.token_urlsafe(12), "lector": secrets.token_urlsafe(12)}


@pytest.fixture
def app_main(monkeypatch, credenciales):
    monkeypatch.setenv("SECRET_KEY", secrets.token_hex(32))
    monkeypatch.setenv("APP_USERS", json.dumps({
        "analista": {"role": "analyst", "hashed_password": _ctx.hash(credenciales["analista"])},
        "lector": {"role": "viewer", "hashed_password": _ctx.hash(credenciales["lector"])},
    }))
    sys.modules.pop("app.main", None)
    return importlib.import_module("app.main")
