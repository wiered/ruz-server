"""Unit tests for KindOfWorkRepository."""

from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from ruz_server.models.models import KindOfWork
from ruz_server.repositories.kind_of_work_repository import KindOfWorkRepository


@pytest.mark.repositories
@pytest.mark.unit
class TestKindOfWorkRepository:
    """Test cases for KindOfWorkRepository class."""

    def test_init(self, mock_session):
        """Test KindOfWorkRepository initialization."""
        repo = KindOfWorkRepository(mock_session)
        assert repo.session == mock_session

    def test_create_success(
        self, kind_of_work_repository, sample_kind_of_work_static, mock_session
    ):
        """Test successful kind-of-work creation."""
        mock_session.add.return_value = None
        mock_session.commit.return_value = None

        result = kind_of_work_repository.Create(sample_kind_of_work_static)

        assert result == sample_kind_of_work_static
        mock_session.add.assert_called_once_with(sample_kind_of_work_static)
        mock_session.commit.assert_called_once()

    def test_create_with_session_error(
        self, kind_of_work_repository, sample_kind_of_work_static, mock_session
    ):
        """Test kind-of-work creation with database error."""
        mock_session.add.side_effect = SQLAlchemyError("Database error")

        with pytest.raises(SQLAlchemyError):
            kind_of_work_repository.Create(sample_kind_of_work_static)

    def test_get_or_create_existing_kind(
        self, kind_of_work_repository, sample_kind_of_work_static
    ):
        """Test GetOrCreate when kind-of-work already exists."""
        existing = KindOfWork(
            id=sample_kind_of_work_static.id, type_of_work="Practice", complexity=1
        )
        kind_of_work_repository.GetById = MagicMock(return_value=existing)

        result = kind_of_work_repository.GetOrCreate(sample_kind_of_work_static)

        assert result == existing
        kind_of_work_repository.GetById.assert_called_once_with(
            sample_kind_of_work_static.id
        )

    def test_get_or_create_new_kind(
        self, kind_of_work_repository, sample_kind_of_work_static
    ):
        """Test GetOrCreate when kind-of-work does not exist."""
        kind_of_work_repository.GetById = MagicMock(return_value=None)
        kind_of_work_repository.Create = MagicMock(
            return_value=sample_kind_of_work_static
        )

        result = kind_of_work_repository.GetOrCreate(sample_kind_of_work_static)

        assert result == sample_kind_of_work_static
        kind_of_work_repository.GetById.assert_called_once_with(
            sample_kind_of_work_static.id
        )
        kind_of_work_repository.Create.assert_called_once_with(
            sample_kind_of_work_static
        )

    def test_list_all_success(self, kind_of_work_repository, mock_session):
        """Test successful listing of all kind-of-work items."""
        expected = [
            KindOfWork(id=1, type_of_work="Lecture", complexity=2),
            KindOfWork(id=2, type_of_work="Lab", complexity=4),
        ]
        mock_result = MagicMock()
        mock_result.all.return_value = expected
        mock_session.exec.return_value = mock_result

        result = kind_of_work_repository.ListAll()

        assert result == expected
        mock_session.exec.assert_called_once()

    def test_get_by_id_success(
        self, kind_of_work_repository, mock_session, sample_kind_of_work_static
    ):
        """Test successful kind-of-work retrieval by ID."""
        mock_result = MagicMock()
        mock_result.first.return_value = sample_kind_of_work_static
        mock_session.exec.return_value = mock_result

        result = kind_of_work_repository.GetById(sample_kind_of_work_static.id)

        assert result == sample_kind_of_work_static
        mock_session.exec.assert_called_once()

    def test_get_by_id_not_found(self, kind_of_work_repository, mock_session):
        """Test kind-of-work retrieval by ID when item does not exist."""
        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_session.exec.return_value = mock_result

        result = kind_of_work_repository.GetById(999999)

        assert result is None

    def test_update_success(
        self, kind_of_work_repository, mock_session, sample_kind_of_work_static
    ):
        """Test successful kind-of-work update."""
        kind_of_work_repository.GetById = MagicMock(
            return_value=sample_kind_of_work_static
        )
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        result = kind_of_work_repository.Update(
            sample_kind_of_work_static.id, type_of_work="Updated Type", complexity=5
        )

        assert result is True
        mock_session.exec.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_update_with_none_values(
        self, kind_of_work_repository, mock_session, sample_kind_of_work_static
    ):
        """Test kind-of-work update with None values (should use current values)."""
        kind_of_work_repository.GetById = MagicMock(
            return_value=sample_kind_of_work_static
        )
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        result = kind_of_work_repository.Update(
            sample_kind_of_work_static.id, type_of_work=None, complexity=None
        )

        assert result is True

    def test_update_kind_not_found(self, kind_of_work_repository):
        """Test update when kind-of-work does not exist."""
        kind_of_work_repository.GetById = MagicMock(return_value=None)

        result = kind_of_work_repository.Update(
            999999, type_of_work="Type", complexity=1
        )

        assert result is False

    def test_update_database_error(
        self, kind_of_work_repository, mock_session, sample_kind_of_work_static
    ):
        """Test update with database error."""
        kind_of_work_repository.GetById = MagicMock(
            return_value=sample_kind_of_work_static
        )
        mock_session.exec.side_effect = SQLAlchemyError("Database error")
        mock_session.rollback.return_value = None

        result = kind_of_work_repository.Update(
            sample_kind_of_work_static.id, type_of_work="Type", complexity=1
        )

        assert result is False
        mock_session.rollback.assert_called_once()

    def test_delete_success(self, kind_of_work_repository, mock_session):
        """Test successful kind-of-work deletion."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        result = kind_of_work_repository.Delete(123456)

        assert result is True
        mock_session.exec.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_delete_no_rows_affected(self, kind_of_work_repository, mock_session):
        """Test deletion when no rows are affected."""
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        result = kind_of_work_repository.Delete(999999)

        assert result is False

    def test_delete_database_error(self, kind_of_work_repository, mock_session):
        """Test deletion with database error."""
        mock_session.exec.side_effect = SQLAlchemyError("Database error")
        mock_session.rollback.return_value = None

        result = kind_of_work_repository.Delete(123456)

        assert result is False
        mock_session.rollback.assert_called_once()


@pytest.mark.repositories
@pytest.mark.integration
class TestKindOfWorkRepositoryIntegration:
    """Integration tests for KindOfWorkRepository with real database session."""

    def test_create_and_retrieve_kind(
        self, kind_of_work_repository_clean, sample_kind_of_work
    ):
        """Test creating and retrieving a kind-of-work with real database."""
        created = kind_of_work_repository_clean.Create(sample_kind_of_work)
        retrieved = kind_of_work_repository_clean.GetById(sample_kind_of_work.id)

        assert created.id == sample_kind_of_work.id
        assert retrieved is not None
        assert retrieved.type_of_work == sample_kind_of_work.type_of_work
        assert retrieved.complexity == sample_kind_of_work.complexity

    def test_get_or_create_existing(
        self, kind_of_work_repository_clean, sample_kind_of_work
    ):
        """Test GetOrCreate with existing kind-of-work."""
        kind_of_work_repository_clean.Create(sample_kind_of_work)

        result = kind_of_work_repository_clean.GetOrCreate(sample_kind_of_work)

        assert result.id == sample_kind_of_work.id

    def test_update_kind_data(self, kind_of_work_repository_clean, sample_kind_of_work):
        """Test updating kind-of-work data with real database."""
        kind_of_work_repository_clean.Create(sample_kind_of_work)

        result = kind_of_work_repository_clean.Update(
            sample_kind_of_work.id, type_of_work="Updated Type", complexity=10
        )

        assert result is True

        updated = kind_of_work_repository_clean.GetById(sample_kind_of_work.id)
        assert updated.type_of_work == "Updated Type"
        assert updated.complexity == 10

    def test_update_with_none_values(
        self, kind_of_work_repository_clean, sample_kind_of_work
    ):
        """Test updating kind-of-work with None values (should keep current values)."""
        kind_of_work_repository_clean.Create(sample_kind_of_work)
        original_type = sample_kind_of_work.type_of_work
        original_complexity = sample_kind_of_work.complexity

        result = kind_of_work_repository_clean.Update(
            sample_kind_of_work.id, type_of_work=None, complexity=None
        )

        assert result is True

        updated = kind_of_work_repository_clean.GetById(sample_kind_of_work.id)
        assert updated.type_of_work == original_type
        assert updated.complexity == original_complexity

    def test_list_all_kinds(
        self, kind_of_work_repository_clean, multiple_kinds_of_work
    ):
        """Test listing all kind-of-work items with real database."""
        for item in multiple_kinds_of_work:
            kind_of_work_repository_clean.Create(item)

        all_items = kind_of_work_repository_clean.ListAll()

        assert len(all_items) == 3
        assert all(item.type_of_work.startswith("Type ") for item in all_items)

    def test_delete_kind(self, kind_of_work_repository_clean, sample_kind_of_work):
        """Test deleting a kind-of-work with real database."""
        kind_of_work_repository_clean.Create(sample_kind_of_work)

        assert kind_of_work_repository_clean.GetById(sample_kind_of_work.id) is not None

        result = kind_of_work_repository_clean.Delete(sample_kind_of_work.id)

        assert result is True
        assert kind_of_work_repository_clean.GetById(sample_kind_of_work.id) is None

    def test_delete_nonexistent_kind(self, kind_of_work_repository_clean):
        """Test deleting a nonexistent kind-of-work."""
        result = kind_of_work_repository_clean.Delete(999999)

        assert result is False
