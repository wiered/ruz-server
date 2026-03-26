"""Smoke and contract tests for infrastructure modules."""

from pathlib import Path
import importlib.util

import pytest
import uvicorn
from fastapi import FastAPI
from sqlmodel import Session


from ruz_server.database import DataBase, db
from ruz_server.logging_config.logging_config import ColoredFormatter, LOGGING_CONFIG, LOGS_DIR
from ruz_server.settings import ROOT, settings


@pytest.mark.integration
class TestInfrastructure:
    def test_settings_contract(self):
        assert ROOT.exists()
        assert ROOT.name == "ruz-server"

        assert isinstance(settings.postgresql_uri, str)
        assert settings.postgresql_uri != ""
        assert isinstance(settings.valid_api_key, str)
        assert settings.valid_api_key != ""

    def test_database_initializes_engine_and_session(self):
        db = DataBase("sqlite://")
        with db.getSession() as session:
            assert isinstance(session, Session)

    def test_database_get_session_generator_yields_session(self):
        db = DataBase("sqlite://")
        generator = db.get_session()
        session = next(generator)
        assert isinstance(session, Session)
        generator.close()

    def test_logging_config_has_expected_handlers(self):
        handlers = LOGGING_CONFIG["handlers"]
        assert "console" in handlers
        assert "file_debug" in handlers
        assert "file_error" in handlers
        assert Path(handlers["file_debug"]["filename"]).name == "debug.log"
        assert Path(handlers["file_error"]["filename"]).name == "error.log"
        assert LOGS_DIR.exists()

    def test_colored_formatter_formats_message(self):
        formatter = ColoredFormatter("%(levelname)s: %(message)s")
        record = __import__("logging").LogRecord(
            name="test",
            level=20,
            pathname=__file__,
            lineno=1,
            msg="hello",
            args=(),
            exc_info=None,
        )
        message = formatter.format(record)
        assert "hello" in message
        assert "INFO" in message

    def test_main_module_exposes_app_and_settings(self, monkeypatch):
        main_path = Path(__file__).parent.parent / "src" / "ruz_server" / "main.py"
        spec = importlib.util.spec_from_file_location("ruz_main_module", main_path)
        main_module = importlib.util.module_from_spec(spec)
        uvicorn_run_called = False

        def fake_uvicorn_run(*args, **kwargs):
            nonlocal uvicorn_run_called
            uvicorn_run_called = True

        monkeypatch.setattr(uvicorn, "run", fake_uvicorn_run)

        assert spec is not None
        assert spec.loader is not None
        spec.loader.exec_module(main_module)

        assert isinstance(main_module.app, FastAPI)
        assert main_module.settings is not None
        assert main_module.settings.host == settings.host
        assert main_module.settings.port == settings.port
        assert main_module.settings.postgresql_uri == settings.postgresql_uri
        assert uvicorn_run_called is False
