"""Prueba de regresion F-01: SECRET_KEY debe venir del entorno, no del codigo.

Ejecutar:  SECRET_KEY=$(python -c "import secrets;print(secrets.token_hex(32))") pytest -q
"""
import importlib
import os
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _reload_app():
    sys.modules.pop("app.main", None)
    return importlib.import_module("app.main")


def test_falla_al_arrancar_sin_secret_key(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(KeyError):
        _reload_app()


def test_usa_la_clave_del_entorno(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "clave-de-prueba-solo-para-test")
    main = _reload_app()
    assert main.SECRET_KEY == "clave-de-prueba-solo-para-test"


def test_login_emite_token_y_endpoint_protegido(monkeypatch):
    from fastapi.testclient import TestClient

    monkeypatch.setenv("SECRET_KEY", "clave-de-prueba-solo-para-test")
    main = _reload_app()
    client = TestClient(main.app)
    assert client.get("/alertas").status_code == 401
    r = client.post("/token", data={"username": "auditor", "password": "viewer123"})
    assert r.status_code == 200
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    assert client.get("/alertas", headers=h).status_code == 200


def test_el_codigo_fuente_no_contiene_la_clave_vieja():
    src = (ROOT / "app" / "main.py").read_text(encoding="utf-8")
    assert "CAMBIAR-EN-PRODUCCION" not in src
