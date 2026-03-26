import logging
import re
from urllib.parse import urlparse

import pytest
from logging.config import dictConfig

from ruz_server.logging_config.logging_config import LOGGING_CONFIG
from ruz_server.settings import settings


def _extract_password_from_pg_uri(uri: str) -> str | None:
    try:
        parsed = urlparse(uri)
    except Exception:
        return None
    password = parsed.password
    if not password:
        return None
    return password


def test_secret_masking_removes_uri_password_from_logs(caplog):
    dictConfig(LOGGING_CONFIG)
    caplog.set_level(logging.DEBUG)

    logger = logging.getLogger("secret_masking_test")
    uri_with_password = "postgresql://u:REALPASS@h:5432/db"
    logger.info("db url=%s", uri_with_password)

    # Проверяем, что в логах не осталось "незамаскированного" user:pass@.
    # В нашем маппинге password заменяется на "***".
    assert "REALPASS" not in caplog.text
    assert re.search(r":(?!\*{3})[^@\s]+@", caplog.text) is None


def test_secret_masking_removes_real_password_from_logs(caplog):
    dictConfig(LOGGING_CONFIG)
    caplog.set_level(logging.DEBUG)

    real_password = _extract_password_from_pg_uri(settings.postgresql_uri)
    if not real_password:
        pytest.skip("postgresql_uri has no password component to validate masking")

    caplog.clear()
    logger = logging.getLogger("secret_masking_test")
    logger.info("db url=%s", settings.postgresql_uri)

    assert real_password not in caplog.text

