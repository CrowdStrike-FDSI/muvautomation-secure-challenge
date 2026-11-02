"""Regresion F-01: SECRET_KEY debe venir del entorno, no del codigo."""
import importlib
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_falla_al_arrancar_sin_secret_key(monkeypatch, app_main):
    monkeypatch.delenv("SECRET_KEY")
    sys.modules.pop("app.main", None)
    with pytest.raises(KeyError):
        importlib.import_module("app.main")


def test_usa_la_clave_del_entorno(app_main, monkeypatch):
    import os
    assert app_main.SECRET_KEY == os.environ["SECRET_KEY"]


def test_el_codigo_fuente_no_contiene_la_clave_vieja():
    src = (ROOT / "app" / "main.py").read_text(encoding="utf-8")
    assert "CAMBIAR-EN-PRODUCCION" not in src
