"""Unit tests for LecturerRepository."""

import uuid
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from ruz_server.models.models import Lecturer
from ruz_server.repositories.lecturer_repository import LecturerRepository


@pytest.mark.repositories
@pytest.mark.unit
class TestLecturerRepository:
    """Test cases for LecturerRepository class."""

    def test_init(self, mock_session):
        """Test LecturerRepository initialization."""
        repo = LecturerRepository(mock_session)
        assert repo.session == mock_session

    def test_create_success(
        self, lecturer_repository, sample_lecturer_static, mock_session
    ):
        """Test successful lecturer creation."""
        mock_session.add.return_value = None
        mock_session.commit.return_value = None

        result = lecturer_repository.Create(sample_lecturer_static)

        assert result == sample_lecturer_static
        mock_session.add.assert_called_once_with(sample_lecturer_static)
        mock_session.commit.assert_called_once()

    def test_create_with_session_error(
        self, lecturer_repository, sample_lecturer_static, mock_session
    ):
        """Test lecturer creation with database error."""
        mock_session.add.side_effect = SQLAlchemyError("Database error")

        with pytest.raises(SQLAlchemyError):
            lecturer_repository.Create(sample_lecturer_static)

    def test_get_or_create_existing_lecturer(
        self, lecturer_repository, sample_lecturer_static
    ):
        """Test GetOrCreate when lecturer already exists."""
        existing = Lecturer(
            id=sample_lecturer_static.id,
            full_name="Existing Lecturer",
            short_name="Existing",
            rank="Professor",
        )
        lecturer_repository.GetById = MagicMock(return_value=existing)

        result = lecturer_repository.GetOrCreate(sample_lecturer_static)

        assert result == existing
        lecturer_repository.GetById.assert_called_once_with(sample_lecturer_static.id)

    def test_get_or_create_new_lecturer(
        self, lecturer_repository, sample_lecturer_static
    ):
        """Test GetOrCreate when lecturer does not exist."""
        lecturer_repository.GetById = MagicMock(return_value=None)
        lecturer_repository.Create = MagicMock(return_value=sample_lecturer_static)

        result = lecturer_repository.GetOrCreate(sample_lecturer_static)

        assert result == sample_lecturer_static
        lecturer_repository.GetById.assert_called_once_with(sample_lecturer_static.id)
        lecturer_repository.Create.assert_called_once_with(sample_lecturer_static)

    def test_list_all_success(self, lecturer_repository, mock_session):
        """Test successful listing of all lecturers."""
        expected = [
            Lecturer(id=1, full_name="John Doe", short_name="J. Doe", rank="Professor"),
            Lecturer(id=2, full_name="Jane Roe", short_name="J. Roe", rank="Assistant"),
        ]
        mock_result = MagicMock()
        mock_result.all.return_value = expected
        mock_session.exec.return_value = mock_result

        result = lecturer_repository.ListAll()

        assert result == expected
        mock_session.exec.assert_called_once()

    def test_get_by_id_success(
        self, lecturer_repository, mock_session, sample_lecturer_static
    ):
        """Test successful lecturer retrieval by ID."""
        mock_result = MagicMock()
        mock_result.first.return_value = sample_lecturer_static
        mock_session.exec.return_value = mock_result

        result = lecturer_repository.GetById(sample_lecturer_static.id)

        assert result == sample_lecturer_static
        mock_session.exec.assert_called_once()

    def test_get_by_id_not_found(self, lecturer_repository, mock_session):
        """Test lecturer retrieval by ID when lecturer does not exist."""
        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_session.exec.return_value = mock_result

        result = lecturer_repository.GetById(999999)

        assert result is None

    def test_get_by_guid_success(
        self, lecturer_repository, mock_session, sample_lecturer_static
    ):
        """Test successful lecturer retrieval by GUID."""
        mock_result = MagicMock()
        mock_result.first.return_value = sample_lecturer_static
        mock_session.exec.return_value = mock_result

        result = lecturer_repository.GetByGUID(sample_lecturer_static.guid)

        assert result == sample_lecturer_static
        mock_session.exec.assert_called_once()

    def test_get_by_guid_not_found(self, lecturer_repository, mock_session):
        """Test lecturer retrieval by GUID when lecturer does not exist."""
        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_session.exec.return_value = mock_result

        result = lecturer_repository.GetByGUID(uuid.uuid4())

        assert result is None

    def test_get_with_lessons_success(
        self, lecturer_repository, mock_session, sample_lecturer_static
    ):
        """Test successful lecturer retrieval with lessons."""
        mock_result = MagicMock()
        mock_result.first.return_value = sample_lecturer_static
        mock_session.exec.return_value = mock_result

        result = lecturer_repository.GetWithLessons(sample_lecturer_static.id)

        assert result == sample_lecturer_static
        mock_session.exec.assert_called_once()

    def test_update_success(
        self, lecturer_repository, mock_session, sample_lecturer_static
    ):
        """Test successful lecturer update."""
        lecturer_repository.GetById = MagicMock(return_value=sample_lecturer_static)
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        result = lecturer_repository.Update(
            sample_lecturer_static.id,
            full_name="Updated Full Name",
            short_name="Updated Short",
            rank="Senior Lecturer",
        )

        assert result is True
        mock_session.exec.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_update_with_none_values(
        self, lecturer_repository, mock_session, sample_lecturer_static
    ):
        """Test lecturer update with None values (should use current values)."""
        lecturer_repository.GetById = MagicMock(return_value=sample_lecturer_static)
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        result = lecturer_repository.Update(
            sample_lecturer_static.id, full_name=None, short_name=None, rank=None
        )

        assert result is True

    def test_update_lecturer_not_found(self, lecturer_repository):
        """Test update when lecturer does not exist."""
        lecturer_repository.GetById = MagicMock(return_value=None)

        result = lecturer_repository.Update(
            999999, full_name="Name", short_name="Short", rank="Rank"
        )

        assert result is False

    def test_update_database_error(
        self, lecturer_repository, mock_session, sample_lecturer_static
    ):
        """Test update with database error."""
        lecturer_repository.GetById = MagicMock(return_value=sample_lecturer_static)
        mock_session.exec.side_effect = SQLAlchemyError("Database error")
        mock_session.rollback.return_value = None

        result = lecturer_repository.Update(
            sample_lecturer_static.id, full_name="Name", short_name="Short", rank="Rank"
        )

        assert result is False
        mock_session.rollback.assert_called_once()

    def test_delete_success(self, lecturer_repository, mock_session):
        """Test successful lecturer deletion."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        result = lecturer_repository.Delete(123456)

        assert result is True
        mock_session.exec.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_delete_no_rows_affected(self, lecturer_repository, mock_session):
        """Test deletion when no rows are affected."""
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        result = lecturer_repository.Delete(999999)

        assert result is False

    def test_delete_database_error(self, lecturer_repository, mock_session):
        """Test deletion with database error."""
        mock_session.exec.side_effect = SQLAlchemyError("Database error")
        mock_session.rollback.return_value = None

        result = lecturer_repository.Delete(123456)

        assert result is False
        mock_session.rollback.assert_called_once()


@pytest.mark.repositories
@pytest.mark.integration
class TestLecturerRepositoryIntegration:
    """Integration tests for LecturerRepository with real database session."""

    def test_create_and_retrieve_lecturer(
        self, lecturer_repository_clean, sample_lecturer
    ):
        """Test creating and retrieving a lecturer with real database."""
        created = lecturer_repository_clean.Create(sample_lecturer)
        retrieved = lecturer_repository_clean.GetById(sample_lecturer.id)

        assert created.id == sample_lecturer.id
        assert retrieved is not None
        assert retrieved.full_name == sample_lecturer.full_name
        assert retrieved.short_name == sample_lecturer.short_name
        assert retrieved.rank == sample_lecturer.rank

    def test_get_or_create_existing(self, lecturer_repository_clean, sample_lecturer):
        """Test GetOrCreate with existing lecturer."""
        lecturer_repository_clean.Create(sample_lecturer)

        result = lecturer_repository_clean.GetOrCreate(sample_lecturer)

        assert result.id == sample_lecturer.id

    def test_get_by_guid(self, lecturer_repository_clean, sample_lecturer):
        """Test retrieving lecturer by GUID with real database."""
        lecturer_repository_clean.Create(sample_lecturer)

        result = lecturer_repository_clean.GetByGUID(sample_lecturer.guid)

        assert result is not None
        assert result.guid == sample_lecturer.guid
        assert result.full_name == sample_lecturer.full_name

    def test_get_with_lessons(self, lecturer_repository_clean, sample_lecturer):
        """Test retrieving lecturer with lessons with real database."""
        lecturer_repository_clean.Create(sample_lecturer)

        result = lecturer_repository_clean.GetWithLessons(sample_lecturer.id)

        assert result is not None
        assert result.id == sample_lecturer.id
        assert isinstance(result.lessons, list)

    def test_update_lecturer_data(self, lecturer_repository_clean, sample_lecturer):
        """Test updating lecturer data with real database."""
        lecturer_repository_clean.Create(sample_lecturer)

        result = lecturer_repository_clean.Update(
            sample_lecturer.id,
            full_name="Updated Lecturer",
            short_name="U. Lecturer",
            rank="Docent",
        )

        assert result is True

        updated = lecturer_repository_clean.GetById(sample_lecturer.id)
        assert updated.full_name == "Updated Lecturer"
        assert updated.short_name == "U. Lecturer"
        assert updated.rank == "Docent"

    def test_update_with_none_values(self, lecturer_repository_clean, sample_lecturer):
        """Test updating lecturer with None values (should keep current values)."""
        lecturer_repository_clean.Create(sample_lecturer)
        original_full_name = sample_lecturer.full_name
        original_short_name = sample_lecturer.short_name
        original_rank = sample_lecturer.rank

        result = lecturer_repository_clean.Update(
            sample_lecturer.id, full_name=None, short_name=None, rank=None
        )

        assert result is True

        updated = lecturer_repository_clean.GetById(sample_lecturer.id)
        assert updated.full_name == original_full_name
        assert updated.short_name == original_short_name
        assert updated.rank == original_rank

    def test_list_all_lecturers(self, lecturer_repository_clean, multiple_lecturers):
        """Test listing all lecturers with real database."""
        for lecturer in multiple_lecturers:
            lecturer_repository_clean.Create(lecturer)

        all_lecturers = lecturer_repository_clean.ListAll()

        assert len(all_lecturers) == 3
        assert all(item.full_name.startswith("Lecturer ") for item in all_lecturers)

    def test_delete_lecturer(self, lecturer_repository_clean, sample_lecturer):
        """Test deleting a lecturer with real database."""
        lecturer_repository_clean.Create(sample_lecturer)

        assert lecturer_repository_clean.GetById(sample_lecturer.id) is not None

        result = lecturer_repository_clean.Delete(sample_lecturer.id)

        assert result is True
        assert lecturer_repository_clean.GetById(sample_lecturer.id) is None

    def test_delete_nonexistent_lecturer(self, lecturer_repository_clean):
        """Test deleting a nonexistent lecturer."""
        result = lecturer_repository_clean.Delete(999999)

        assert result is False
