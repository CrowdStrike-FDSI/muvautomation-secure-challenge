"""Regresion F-02: sin contrasenas en el codigo; usuarios y hashes desde el entorno."""
import importlib
import pathlib
import sys

import pytest
from fastapi.testclient import TestClient

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_falla_al_arrancar_sin_app_users(monkeypatch, app_main):
    monkeypatch.delenv("APP_USERS")
    sys.modules.pop("app.main", None)
    with pytest.raises(KeyError):
        importlib.import_module("app.main")


def test_rechaza_rol_invalido(monkeypatch, app_main):
    monkeypatch.setenv("APP_USERS", '{"x": {"role": "root", "hashed_password": "h"}}')
    sys.modules.pop("app.main", None)
    with pytest.raises(ValueError):
        importlib.import_module("app.main")


def test_codigo_y_comentarios_sin_contrasenas_demo():
    src = (ROOT / "app" / "main.py").read_text(encoding="utf-8")
    for viejo in ("analyst123", "viewer123"):
        assert viejo not in src


def test_contrasenas_del_repositorio_ya_no_sirven(app_main):
    c = TestClient(app_main.app)
    for usuario, pwd in (("oscar", "analyst123"), ("auditor", "viewer123")):
        assert c.post("/token", data={"username": usuario, "password": pwd}).status_code == 401


def test_login_y_roles_siguen_funcionando(app_main, credenciales):
    c = TestClient(app_main.app)
    assert c.get("/alertas").status_code == 401
    tok = lambda u, k: {"Authorization": "Bearer " + c.post(
        "/token", data={"username": u, "password": credenciales[k]}).json()["access_token"]}
    assert c.get("/alertas", headers=tok("lector", "lector")).status_code == 200
    alerta = {"id": 1, "host": "h1", "severity": "low", "indicator_type": "malware"}
    assert c.post("/alertas", json=alerta, headers=tok("lector", "lector")).status_code == 403
    assert c.post("/alertas", json=alerta, headers=tok("analista", "analista")).status_code == 200
