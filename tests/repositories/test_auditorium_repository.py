"""Unit tests for AuditoriumRepository."""

import uuid
import pytest
from unittest.mock import MagicMock
from sqlalchemy.exc import SQLAlchemyError



from ruz_server.repositories.auditorium_repository import AuditoriumRepository
from ruz_server.models.models import Auditorium


@pytest.mark.repositories
@pytest.mark.unit
class TestAuditoriumRepository:
    """Test cases for AuditoriumRepository class."""

    def test_init(self, mock_session):
        """Test AuditoriumRepository initialization."""
        repo = AuditoriumRepository(mock_session)
        assert repo.session == mock_session

    def test_create_success(self, auditorium_repository, sample_auditorium_static, mock_session):
        """Test successful auditorium creation."""
        mock_session.add.return_value = None
        mock_session.commit.return_value = None

        result = auditorium_repository.Create(sample_auditorium_static)

        assert result == sample_auditorium_static
        mock_session.add.assert_called_once_with(sample_auditorium_static)
        mock_session.commit.assert_called_once()

    def test_create_with_session_error(self, auditorium_repository, sample_auditorium_static, mock_session):
        """Test auditorium creation with database error."""
        mock_session.add.side_effect = SQLAlchemyError("Database error")

        with pytest.raises(SQLAlchemyError):
            auditorium_repository.Create(sample_auditorium_static)

    def test_get_or_create_existing_auditorium(self, auditorium_repository, sample_auditorium_static):
        """Test GetOrCreate when auditorium already exists."""
        existing = Auditorium(id=sample_auditorium_static.id, name="A-202", building="Building A")
        auditorium_repository.GetById = MagicMock(return_value=existing)

        result = auditorium_repository.GetOrCreate(sample_auditorium_static)

        assert result == existing
        auditorium_repository.GetById.assert_called_once_with(sample_auditorium_static.id)

    def test_get_or_create_new_auditorium(self, auditorium_repository, sample_auditorium_static):
        """Test GetOrCreate when auditorium does not exist."""
        auditorium_repository.GetById = MagicMock(return_value=None)
        auditorium_repository.Create = MagicMock(return_value=sample_auditorium_static)

        result = auditorium_repository.GetOrCreate(sample_auditorium_static)

        assert result == sample_auditorium_static
        auditorium_repository.GetById.assert_called_once_with(sample_auditorium_static.id)
        auditorium_repository.Create.assert_called_once_with(sample_auditorium_static)

    def test_list_all_success(self, auditorium_repository, mock_session):
        """Test successful listing of all auditoriums."""
        expected = [
            Auditorium(id=1, name="A-101", building="Main"),
            Auditorium(id=2, name="B-204", building="Second")
        ]
        mock_result = MagicMock()
        mock_result.all.return_value = expected
        mock_session.exec.return_value = mock_result

        result = auditorium_repository.ListAll()

        assert result == expected
        mock_session.exec.assert_called_once()

    def test_get_by_id_success(self, auditorium_repository, mock_session, sample_auditorium_static):
        """Test successful auditorium retrieval by ID."""
        mock_result = MagicMock()
        mock_result.first.return_value = sample_auditorium_static
        mock_session.exec.return_value = mock_result

        result = auditorium_repository.GetById(sample_auditorium_static.id)

        assert result == sample_auditorium_static
        mock_session.exec.assert_called_once()

    def test_get_by_id_not_found(self, auditorium_repository, mock_session):
        """Test auditorium retrieval by ID when auditorium does not exist."""
        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_session.exec.return_value = mock_result

        result = auditorium_repository.GetById(999999)

        assert result is None

    def test_get_by_guid_success(self, auditorium_repository, mock_session, sample_auditorium_static):
        """Test successful auditorium retrieval by GUID."""
        mock_result = MagicMock()
        mock_result.first.return_value = sample_auditorium_static
        mock_session.exec.return_value = mock_result

        result = auditorium_repository.GetByGuid(sample_auditorium_static.guid)

        assert result == sample_auditorium_static
        mock_session.exec.assert_called_once()

    def test_get_by_guid_not_found(self, auditorium_repository, mock_session):
        """Test auditorium retrieval by GUID when auditorium does not exist."""
        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_session.exec.return_value = mock_result

        result = auditorium_repository.GetByGuid(uuid.uuid4())

        assert result is None

    def test_get_by_name_success(self, auditorium_repository, mock_session, sample_auditorium_static):
        """Test successful auditorium retrieval by name."""
        mock_result = MagicMock()
        mock_result.first.return_value = sample_auditorium_static
        mock_session.exec.return_value = mock_result

        result = auditorium_repository.GetByName(sample_auditorium_static.name)

        assert result == sample_auditorium_static
        mock_session.exec.assert_called_once()

    def test_get_by_name_not_found(self, auditorium_repository, mock_session):
        """Test auditorium retrieval by name when auditorium does not exist."""
        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_session.exec.return_value = mock_result

        result = auditorium_repository.GetByName("NON-EXISTENT")

        assert result is None

    def test_update_success(self, auditorium_repository, mock_session, sample_auditorium_static):
        """Test successful auditorium update."""
        auditorium_repository.GetById = MagicMock(return_value=sample_auditorium_static)
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        result = auditorium_repository.Update(
            sample_auditorium_static.id,
            name="C-301",
            building="Third Building"
        )

        assert result is True
        mock_session.exec.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_update_with_none_values(self, auditorium_repository, mock_session, sample_auditorium_static):
        """Test auditorium update with None values (should use current values)."""
        auditorium_repository.GetById = MagicMock(return_value=sample_auditorium_static)
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        result = auditorium_repository.Update(sample_auditorium_static.id, name=None, building=None)

        assert result is True

    def test_update_auditorium_not_found(self, auditorium_repository):
        """Test update when auditorium does not exist."""
        auditorium_repository.GetById = MagicMock(return_value=None)

        result = auditorium_repository.Update(999999, name="A-999", building="Nowhere")

        assert result is False

    def test_update_database_error(self, auditorium_repository, mock_session, sample_auditorium_static):
        """Test update with database error."""
        auditorium_repository.GetById = MagicMock(return_value=sample_auditorium_static)
        mock_session.exec.side_effect = SQLAlchemyError("Database error")
        mock_session.rollback.return_value = None

        result = auditorium_repository.Update(sample_auditorium_static.id, name="A-102", building="Main")

        assert result is False
        mock_session.rollback.assert_called_once()

    def test_delete_success(self, auditorium_repository, mock_session):
        """Test successful auditorium deletion."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        result = auditorium_repository.Delete(123456)

        assert result is True
        mock_session.exec.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_delete_no_rows_affected(self, auditorium_repository, mock_session):
        """Test deletion when no rows are affected."""
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        result = auditorium_repository.Delete(999999)

        assert result is False

    def test_delete_database_error(self, auditorium_repository, mock_session):
        """Test deletion with database error."""
        mock_session.exec.side_effect = SQLAlchemyError("Database error")
        mock_session.rollback.return_value = None

        result = auditorium_repository.Delete(123456)

        assert result is False
        mock_session.rollback.assert_called_once()


@pytest.mark.repositories
@pytest.mark.integration
class TestAuditoriumRepositoryIntegration:
    """Integration tests for AuditoriumRepository with real database session."""

    def test_create_and_retrieve_auditorium(self, auditorium_repository_clean, sample_auditorium):
        """Test creating and retrieving an auditorium with real database."""
        created = auditorium_repository_clean.Create(sample_auditorium)
        retrieved = auditorium_repository_clean.GetById(sample_auditorium.id)

        assert created.id == sample_auditorium.id
        assert retrieved is not None
        assert retrieved.name == sample_auditorium.name
        assert retrieved.building == sample_auditorium.building

    def test_get_or_create_existing(self, auditorium_repository_clean, sample_auditorium):
        """Test GetOrCreate with existing auditorium."""
        auditorium_repository_clean.Create(sample_auditorium)

        result = auditorium_repository_clean.GetOrCreate(sample_auditorium)

        assert result.id == sample_auditorium.id

    def test_get_by_guid(self, auditorium_repository_clean, sample_auditorium):
        """Test retrieving auditorium by GUID with real database."""
        auditorium_repository_clean.Create(sample_auditorium)

        result = auditorium_repository_clean.GetByGuid(sample_auditorium.guid)

        assert result is not None
        assert result.guid == sample_auditorium.guid
        assert result.name == sample_auditorium.name

    def test_get_by_name(self, auditorium_repository_clean, sample_auditorium):
        """Test retrieving auditorium by name with real database."""
        auditorium_repository_clean.Create(sample_auditorium)

        result = auditorium_repository_clean.GetByName(sample_auditorium.name)

        assert result is not None
        assert result.name == sample_auditorium.name

    def test_update_auditorium_data(self, auditorium_repository_clean, sample_auditorium):
        """Test updating auditorium data with real database."""
        auditorium_repository_clean.Create(sample_auditorium)

        result = auditorium_repository_clean.Update(
            sample_auditorium.id,
            name="Updated Auditorium",
            building="Updated Building"
        )

        assert result is True

        updated = auditorium_repository_clean.GetById(sample_auditorium.id)
        assert updated.name == "Updated Auditorium"
        assert updated.building == "Updated Building"

    def test_update_with_none_values(self, auditorium_repository_clean, sample_auditorium):
        """Test updating auditorium with None values (should keep current values)."""
        auditorium_repository_clean.Create(sample_auditorium)
        original_name = sample_auditorium.name
        original_building = sample_auditorium.building

        result = auditorium_repository_clean.Update(sample_auditorium.id, name=None, building=None)

        assert result is True

        updated = auditorium_repository_clean.GetById(sample_auditorium.id)
        assert updated.name == original_name
        assert updated.building == original_building

    def test_list_all_auditoriums(self, auditorium_repository_clean, multiple_auditoriums):
        """Test listing all auditoriums with real database."""
        for auditorium in multiple_auditoriums:
            auditorium_repository_clean.Create(auditorium)

        all_auditoriums = auditorium_repository_clean.ListAll()

        assert len(all_auditoriums) == 3
        for i, auditorium in enumerate(all_auditoriums):
            assert auditorium.name.startswith("Auditorium ")
            assert auditorium.building == f"Building {i + 1}"

    def test_delete_auditorium(self, auditorium_repository_clean, sample_auditorium):
        """Test deleting an auditorium with real database."""
        auditorium_repository_clean.Create(sample_auditorium)

        assert auditorium_repository_clean.GetById(sample_auditorium.id) is not None

        result = auditorium_repository_clean.Delete(sample_auditorium.id)

        assert result is True
        assert auditorium_repository_clean.GetById(sample_auditorium.id) is None

    def test_delete_nonexistent_auditorium(self, auditorium_repository_clean):
        """Test deleting a nonexistent auditorium."""
        result = auditorium_repository_clean.Delete(999999)

        assert result is False
