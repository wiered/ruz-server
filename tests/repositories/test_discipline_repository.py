"""Unit tests for DisciplineRepository."""

from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from ruz_server.models.models import Discipline
from ruz_server.repositories.discipline_repository import DisciplineRepository


@pytest.mark.repositories
@pytest.mark.unit
class TestDisciplineRepository:
    """Test cases for DisciplineRepository class."""

    def test_init(self, mock_session):
        """Test DisciplineRepository initialization."""
        repo = DisciplineRepository(mock_session)
        assert repo.session == mock_session

    def test_create_success(
        self, discipline_repository, sample_discipline_static, mock_session
    ):
        """Test successful discipline creation."""
        mock_session.add.return_value = None
        mock_session.commit.return_value = None

        result = discipline_repository.Create(sample_discipline_static)

        assert result == sample_discipline_static
        mock_session.add.assert_called_once_with(sample_discipline_static)
        mock_session.commit.assert_called_once()

    def test_create_with_session_error(
        self, discipline_repository, sample_discipline_static, mock_session
    ):
        """Test discipline creation with database error."""
        mock_session.add.side_effect = SQLAlchemyError("Database error")

        with pytest.raises(SQLAlchemyError):
            discipline_repository.Create(sample_discipline_static)

    def test_get_or_create_existing_discipline(
        self, discipline_repository, sample_discipline_static
    ):
        """Test GetOrCreate when discipline already exists."""
        existing = Discipline(
            id=sample_discipline_static.id,
            name="Existing",
            examtype="credit",
            has_labs=False,
        )
        discipline_repository.GetById = MagicMock(return_value=existing)

        result = discipline_repository.GetOrCreate(sample_discipline_static)

        assert result == existing
        discipline_repository.GetById.assert_called_once_with(
            sample_discipline_static.id
        )

    def test_get_or_create_new_discipline(
        self, discipline_repository, sample_discipline_static
    ):
        """Test GetOrCreate when discipline does not exist."""
        discipline_repository.GetById = MagicMock(return_value=None)
        discipline_repository.Create = MagicMock(return_value=sample_discipline_static)

        result = discipline_repository.GetOrCreate(sample_discipline_static)

        assert result == sample_discipline_static
        discipline_repository.GetById.assert_called_once_with(
            sample_discipline_static.id
        )
        discipline_repository.Create.assert_called_once_with(sample_discipline_static)

    def test_list_all_success(self, discipline_repository, mock_session):
        """Test successful listing of all disciplines."""
        expected = [
            Discipline(id=1, name="Math", examtype="exam", has_labs=True),
            Discipline(id=2, name="History", examtype="credit", has_labs=False),
        ]
        mock_result = MagicMock()
        mock_result.all.return_value = expected
        mock_session.exec.return_value = mock_result

        result = discipline_repository.ListAll()

        assert result == expected
        mock_session.exec.assert_called_once()

    def test_get_by_id_success(
        self, discipline_repository, mock_session, sample_discipline_static
    ):
        """Test successful discipline retrieval by ID."""
        mock_result = MagicMock()
        mock_result.first.return_value = sample_discipline_static
        mock_session.exec.return_value = mock_result

        result = discipline_repository.GetById(sample_discipline_static.id)

        assert result == sample_discipline_static
        mock_session.exec.assert_called_once()

    def test_get_by_id_not_found(self, discipline_repository, mock_session):
        """Test discipline retrieval by ID when discipline does not exist."""
        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_session.exec.return_value = mock_result

        result = discipline_repository.GetById(999999)

        assert result is None

    def test_get_by_name_success(
        self, discipline_repository, mock_session, sample_discipline_static
    ):
        """Test successful discipline retrieval by name."""
        mock_result = MagicMock()
        mock_result.first.return_value = sample_discipline_static
        mock_session.exec.return_value = mock_result

        result = discipline_repository.GetByName(sample_discipline_static.name)

        assert result == sample_discipline_static
        mock_session.exec.assert_called_once()

    def test_get_by_name_not_found(self, discipline_repository, mock_session):
        """Test discipline retrieval by name when discipline does not exist."""
        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_session.exec.return_value = mock_result

        result = discipline_repository.GetByName("NON-EXISTENT")

        assert result is None

    def test_get_by_exam_type_success(self, discipline_repository, mock_session):
        """Test successful discipline retrieval by exam type."""
        expected = [
            Discipline(id=1, name="Math", examtype="exam", has_labs=True),
            Discipline(id=2, name="Physics", examtype="exam", has_labs=True),
        ]
        mock_result = MagicMock()
        mock_result.all.return_value = expected
        mock_session.exec.return_value = mock_result

        result = discipline_repository.GetByExamType("exam")

        assert result == expected
        mock_session.exec.assert_called_once()

    def test_get_by_exam_type_not_found(self, discipline_repository, mock_session):
        """Test discipline retrieval by exam type when disciplines do not exist."""
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_session.exec.return_value = mock_result

        result = discipline_repository.GetByExamType("none")

        assert result == []

    def test_update_success(
        self, discipline_repository, mock_session, sample_discipline_static
    ):
        """Test successful discipline update."""
        discipline_repository.GetById = MagicMock(return_value=sample_discipline_static)
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        result = discipline_repository.Update(
            sample_discipline_static.id,
            name="Updated Name",
            examtype="credit",
            has_labs=False,
        )

        assert result is True
        mock_session.exec.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_update_with_none_values(
        self, discipline_repository, mock_session, sample_discipline_static
    ):
        """Test discipline update with None values (should use current values)."""
        discipline_repository.GetById = MagicMock(return_value=sample_discipline_static)
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        result = discipline_repository.Update(
            sample_discipline_static.id, name=None, examtype=None, has_labs=None
        )

        assert result is True

    def test_update_discipline_not_found(self, discipline_repository):
        """Test update when discipline does not exist."""
        discipline_repository.GetById = MagicMock(return_value=None)

        result = discipline_repository.Update(
            999999, name="Name", examtype="exam", has_labs=True
        )

        assert result is False

    def test_update_database_error(
        self, discipline_repository, mock_session, sample_discipline_static
    ):
        """Test update with database error."""
        discipline_repository.GetById = MagicMock(return_value=sample_discipline_static)
        mock_session.exec.side_effect = SQLAlchemyError("Database error")
        mock_session.rollback.return_value = None

        result = discipline_repository.Update(
            sample_discipline_static.id, name="Name", examtype="exam", has_labs=True
        )

        assert result is False
        mock_session.rollback.assert_called_once()

    def test_delete_success(self, discipline_repository, mock_session):
        """Test successful discipline deletion."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        result = discipline_repository.Delete(123456)

        assert result is True
        mock_session.exec.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_delete_no_rows_affected(self, discipline_repository, mock_session):
        """Test deletion when no rows are affected."""
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        result = discipline_repository.Delete(999999)

        assert result is False

    def test_delete_database_error(self, discipline_repository, mock_session):
        """Test deletion with database error."""
        mock_session.exec.side_effect = SQLAlchemyError("Database error")
        mock_session.rollback.return_value = None

        result = discipline_repository.Delete(123456)

        assert result is False
        mock_session.rollback.assert_called_once()


@pytest.mark.repositories
@pytest.mark.integration
class TestDisciplineRepositoryIntegration:
    """Integration tests for DisciplineRepository with real database session."""

    def test_create_and_retrieve_discipline(
        self, discipline_repository_clean, sample_discipline
    ):
        """Test creating and retrieving a discipline with real database."""
        created = discipline_repository_clean.Create(sample_discipline)
        retrieved = discipline_repository_clean.GetById(sample_discipline.id)

        assert created.id == sample_discipline.id
        assert retrieved is not None
        assert retrieved.name == sample_discipline.name
        assert retrieved.examtype == sample_discipline.examtype
        assert retrieved.has_labs == sample_discipline.has_labs

    def test_get_or_create_existing(
        self, discipline_repository_clean, sample_discipline
    ):
        """Test GetOrCreate with existing discipline."""
        discipline_repository_clean.Create(sample_discipline)

        result = discipline_repository_clean.GetOrCreate(sample_discipline)

        assert result.id == sample_discipline.id

    def test_get_by_name(self, discipline_repository_clean, sample_discipline):
        """Test retrieving discipline by name with real database."""
        discipline_repository_clean.Create(sample_discipline)

        result = discipline_repository_clean.GetByName(sample_discipline.name)

        assert result is not None
        assert result.name == sample_discipline.name

    def test_get_by_exam_type(self, discipline_repository_clean, multiple_disciplines):
        """Test retrieving disciplines by exam type with real database."""
        for discipline in multiple_disciplines:
            discipline_repository_clean.Create(discipline)

        result = discipline_repository_clean.GetByExamType("exam")

        assert len(result) == 2
        for item in result:
            assert item.examtype == "exam"

    def test_update_discipline_data(
        self, discipline_repository_clean, sample_discipline
    ):
        """Test updating discipline data with real database."""
        discipline_repository_clean.Create(sample_discipline)

        result = discipline_repository_clean.Update(
            sample_discipline.id,
            name="Updated Discipline",
            examtype="credit",
            has_labs=False,
        )

        assert result is True

        updated = discipline_repository_clean.GetById(sample_discipline.id)
        assert updated.name == "Updated Discipline"
        assert updated.examtype == "credit"
        assert updated.has_labs is False

    def test_update_with_none_values(
        self, discipline_repository_clean, sample_discipline
    ):
        """Test updating discipline with None values (should keep current values)."""
        discipline_repository_clean.Create(sample_discipline)
        original_name = sample_discipline.name
        original_examtype = sample_discipline.examtype
        original_has_labs = sample_discipline.has_labs

        result = discipline_repository_clean.Update(
            sample_discipline.id, name=None, examtype=None, has_labs=None
        )

        assert result is True

        updated = discipline_repository_clean.GetById(sample_discipline.id)
        assert updated.name == original_name
        assert updated.examtype == original_examtype
        assert updated.has_labs == original_has_labs

    def test_list_all_disciplines(
        self, discipline_repository_clean, multiple_disciplines
    ):
        """Test listing all disciplines with real database."""
        for discipline in multiple_disciplines:
            discipline_repository_clean.Create(discipline)

        all_disciplines = discipline_repository_clean.ListAll()

        assert len(all_disciplines) == 3
        assert all(item.name.startswith("Discipline ") for item in all_disciplines)

    def test_delete_discipline(self, discipline_repository_clean, sample_discipline):
        """Test deleting a discipline with real database."""
        discipline_repository_clean.Create(sample_discipline)

        assert discipline_repository_clean.GetById(sample_discipline.id) is not None

        result = discipline_repository_clean.Delete(sample_discipline.id)

        assert result is True
        assert discipline_repository_clean.GetById(sample_discipline.id) is None

    def test_delete_nonexistent_discipline(self, discipline_repository_clean):
        """Test deleting a nonexistent discipline."""
        result = discipline_repository_clean.Delete(999999)

        assert result is False
