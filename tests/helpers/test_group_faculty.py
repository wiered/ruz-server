"""Tests for group faculty_name persistence helper."""

import pytest

from ruz_server.helpers.group_faculty import NO_FACULTY_DB_VALUE, persisted_faculty_name


@pytest.mark.helpers
@pytest.mark.unit
def test_persisted_faculty_name_none_and_blank():
    assert persisted_faculty_name(None) == NO_FACULTY_DB_VALUE
    assert persisted_faculty_name("") == NO_FACULTY_DB_VALUE
    assert persisted_faculty_name("   ") == NO_FACULTY_DB_VALUE


@pytest.mark.helpers
@pytest.mark.unit
def test_persisted_faculty_name_keeps_non_empty():
    assert persisted_faculty_name("  ФИВТ  ") == "ФИВТ"
