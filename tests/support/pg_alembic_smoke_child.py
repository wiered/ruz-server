"""Connect to DB after migrations (run in subprocess; POSTGRESQL_URI must be set)."""

from __future__ import annotations


def main() -> None:
    from sqlalchemy import create_engine, text

    from ruz_server.settings import settings

    eng = create_engine(settings.postgresql_uri)
    with eng.connect() as conn:
        conn.execute(text("SELECT 1 FROM users LIMIT 1"))


if __name__ == "__main__":
    main()
