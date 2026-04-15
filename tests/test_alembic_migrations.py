"""Alembic migration path on a disposable PostgreSQL database."""

from __future__ import annotations

import os
import subprocess
import sys
import uuid
from pathlib import Path

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.engine.url import URL

from ruz_server.settings import ROOT, settings

_CHILD = Path(__file__).resolve().parent / "support" / "pg_alembic_smoke_child.py"


def _alembic_head_revision() -> str:
    cfg = Config(str(ROOT / "alembic.ini"))
    script = ScriptDirectory.from_config(cfg)
    heads = script.get_heads()
    if len(heads) != 1:
        msg = f"expected a single Alembic head, got {heads!r}"
        raise RuntimeError(msg)
    return heads[0]


def _require_postgres_url() -> URL:
    url = make_url(settings.postgresql_uri)
    if url.get_backend_name() != "postgresql":
        pytest.skip("Alembic revisions target PostgreSQL")
    return url


def _maintenance_url(url: URL) -> str:
    return str(url.set(database="postgres"))


@pytest.fixture
def ephemeral_postgres_db() -> str:
    base = _require_postgres_url()
    db_name = f"ruzalembic{uuid.uuid4().hex}"
    admin = _maintenance_url(base)
    engine = create_engine(admin, isolation_level="AUTOCOMMIT")
    created = False
    try:
        with engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE {db_name}"))
        created = True
    except OSError as exc:
        pytest.skip(f"could not reach PostgreSQL for migration test: {exc}")
    except Exception as exc:
        pytest.skip(f"could not create ephemeral database: {exc}")

    test_uri = str(base.set(database=db_name))
    try:
        yield test_uri
    finally:
        if created:
            kill_engine = create_engine(admin, isolation_level="AUTOCOMMIT")
            with kill_engine.connect() as conn:
                conn.execute(
                    text(
                        "SELECT pg_terminate_backend(pg_stat_activity.pid) "
                        "FROM pg_stat_activity "
                        "WHERE pg_stat_activity.datname = :name "
                        "AND pg_stat_activity.pid <> pg_backend_pid()"
                    ),
                    {"name": db_name},
                )
                conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))


@pytest.mark.integration
def test_alembic_upgrade_head_creates_schema(ephemeral_postgres_db: str) -> None:
    """Empty DB -> `alembic upgrade head` -> expected tables and revision."""
    env = {**os.environ, "POSTGRESQL_URI": ephemeral_postgres_db}
    proc = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout

    expected = _alembic_head_revision()
    eng = create_engine(ephemeral_postgres_db)
    names = inspect(eng).get_table_names()
    assert "users" in names
    assert "alembic_version" in names
    with eng.connect() as conn:
        rev = conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
    assert rev == expected

    imp = subprocess.run(
        [sys.executable, str(_CHILD)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert imp.returncode == 0, imp.stderr + imp.stdout
