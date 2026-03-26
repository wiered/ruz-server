"""Unit tests for helper functions in api_helpers.py."""

import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from helpers.api_helpers import (
    ensure_entity_exists,
    is_entity_exists,
    create_if_not_exists,
    ensure_entity_doesnot_exist,
)


@pytest.mark.helpers
@pytest.mark.unit
class TestApiHelpers:
    def test_ensure_entity_exists_returns_entity(self):
        lookup = MagicMock(return_value={"id": 1})

        result = ensure_entity_exists(1, lookup)

        assert result == {"id": 1}
        lookup.assert_called_once_with(1)

    def test_ensure_entity_exists_raises_404_when_missing(self):
        lookup = MagicMock(return_value=None)

        with pytest.raises(HTTPException) as exc:
            ensure_entity_exists(42, lookup)

        assert exc.value.status_code == 404
        assert exc.value.detail == "Error: Not Found"

    def test_is_entity_exists_returns_true_when_entity_found(self):
        lookup = MagicMock(return_value={"id": 2})

        result = is_entity_exists(2, lookup)

        assert result is True
        lookup.assert_called_once_with(2)

    def test_is_entity_exists_returns_false_when_missing(self):
        lookup = MagicMock(return_value=None)

        result = is_entity_exists(999, lookup)

        assert result is False

    def test_create_if_not_exists_no_create_when_entity_exists(self):
        repository = MagicMock()
        lookup = MagicMock(return_value={"id": 3})
        entity = MagicMock(id=3, name="exists")

        create_if_not_exists(repository, 3, lookup, entity)

        repository.Create.assert_not_called()

    def test_create_if_not_exists_creates_when_missing(self):
        repository = MagicMock()
        lookup = MagicMock(return_value=None)
        entity = MagicMock(id=4, name="new")

        create_if_not_exists(repository, 4, lookup, entity)
        repository.Create.assert_called_once_with(entity)

    def test_ensure_entity_doesnot_exist_no_error_when_missing(self):
        lookup = MagicMock(return_value=None)

        ensure_entity_doesnot_exist(5, lookup)

        lookup.assert_called_once_with(5)

    def test_ensure_entity_doesnot_exist_raises_409_when_exists(self):
        lookup = MagicMock(return_value={"id": 6})

        with pytest.raises(HTTPException) as exc:
            ensure_entity_doesnot_exist(6, lookup)

        assert exc.value.status_code == 409
        assert exc.value.detail == "Error: Conflict"
