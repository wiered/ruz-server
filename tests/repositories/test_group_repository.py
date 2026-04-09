"""Unit tests for GroupRepository."""

import pytest
from unittest.mock import MagicMock
from sqlalchemy.exc import SQLAlchemyError
import uuid



from ruz_server.repositories.group_repository import GroupRepository
from ruz_server.models.models import Group


@pytest.mark.repositories
@pytest.mark.unit
class TestGroupRepository:
    """Test cases for GroupRepository class."""

    def test_init(self, mock_session):
        """Test GroupRepository initialization."""
        repo = GroupRepository(mock_session)
        assert repo.session == mock_session

    def test_create_success(self, group_repository, sample_group_static, mock_session):
        """Test successful group creation."""
        # Setup
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh.return_value = None

        # Execute
        result = group_repository.Create(sample_group_static)

        # Assert
        assert result == sample_group_static
        mock_session.add.assert_called_once_with(sample_group_static)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(sample_group_static)

    def test_create_with_session_error(self, group_repository, sample_group_static, mock_session):
        """Test group creation with database error."""
        # Setup
        mock_session.add.side_effect = SQLAlchemyError("Database error")

        # Execute & Assert
        with pytest.raises(SQLAlchemyError):
            group_repository.Create(sample_group_static)

    def test_get_or_create_existing_group(self, group_repository, sample_group_static, mock_session):
        """Test GetOrCreate when group already exists."""
        # Setup
        existing_group = Group(id=sample_group_static.id, name="existing_group")
        group_repository.GetById = MagicMock(return_value=existing_group)

        # Execute
        result = group_repository.GetOrCreate(sample_group_static)

        # Assert
        assert result == existing_group
        group_repository.GetById.assert_called_once_with(sample_group_static.id)

    def test_get_or_create_new_group(self, group_repository, sample_group_static, mock_session):
        """Test GetOrCreate when group doesn't exist."""
        # Setup
        group_repository.GetById = MagicMock(return_value=None)
        group_repository.Create = MagicMock(return_value=sample_group_static)

        # Execute
        result = group_repository.GetOrCreate(sample_group_static)

        # Assert
        assert result == sample_group_static
        group_repository.GetById.assert_called_once_with(sample_group_static.id)
        group_repository.Create.assert_called_once_with(sample_group_static)

    def test_list_all_success(self, group_repository, mock_session):
        """Test successful listing of all groups."""
        # Setup
        expected_groups = [
            Group(id=1, name="group1"),
            Group(id=2, name="group2")
        ]
        mock_result = MagicMock()
        mock_result.all.return_value = expected_groups
        mock_session.exec.return_value = mock_result

        # Execute
        result = group_repository.ListAll()

        # Assert
        assert result == expected_groups
        mock_session.exec.assert_called_once()

    def test_get_by_id_success(self, group_repository, mock_session, sample_group_static):
        """Test successful group retrieval by ID."""
        # Setup
        group_id = sample_group_static.id
        mock_result = MagicMock()
        mock_result.first.return_value = sample_group_static
        mock_session.exec.return_value = mock_result

        # Execute
        result = group_repository.GetById(group_id)

        # Assert
        assert result == sample_group_static
        mock_session.exec.assert_called_once()

    def test_get_by_id_not_found(self, group_repository, mock_session):
        """Test group retrieval by ID when group doesn't exist."""
        # Setup
        group_id = 999999
        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_session.exec.return_value = mock_result

        # Execute
        result = group_repository.GetById(group_id)

        # Assert
        assert result is None

    def test_get_by_guid_success(self, group_repository, mock_session, sample_group_static):
        """Test successful group retrieval by GUID."""
        # Setup
        group_guid = sample_group_static.guid
        mock_result = MagicMock()
        mock_result.first.return_value = sample_group_static
        mock_session.exec.return_value = mock_result

        # Execute
        result = group_repository.GetByGUID(group_guid)

        # Assert
        assert result == sample_group_static
        mock_session.exec.assert_called_once()

    def test_get_by_guid_not_found(self, group_repository, mock_session):
        """Test group retrieval by GUID when group doesn't exist."""
        # Setup
        group_guid = uuid.uuid4()
        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_session.exec.return_value = mock_result

        # Execute
        result = group_repository.GetByGUID(group_guid)

        # Assert
        assert result is None

    def test_get_by_name_success(self, group_repository, mock_session):
        """Test successful group retrieval by name."""
        # Setup
        group_name = "Test Group"
        expected_groups = [
            Group(id=1, name=group_name),
            Group(id=2, name=group_name)
        ]
        mock_result = MagicMock()
        mock_result.all.return_value = expected_groups
        mock_session.exec.return_value = mock_result

        # Execute
        result = group_repository.GetByName(group_name)

        # Assert
        assert result == expected_groups
        mock_session.exec.assert_called_once()

    def test_get_by_name_not_found(self, group_repository, mock_session):
        """Test group retrieval by name when no groups exist."""
        # Setup
        group_name = "Nonexistent Group"
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_session.exec.return_value = mock_result

        # Execute
        result = group_repository.GetByName(group_name)

        # Assert
        assert result == []

    def test_update_success(self, group_repository, mock_session, sample_group_static):
        """Test successful group update."""
        # Setup
        group_id = sample_group_static.id
        new_name = "Updated Group"
        new_faculty = "Updated Faculty"

        group_repository.GetById = MagicMock(return_value=sample_group_static)
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        # Execute
        result = group_repository.Update(group_id, new_name, new_faculty)

        # Assert
        assert result is True
        mock_session.exec.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_update_with_none_values(self, group_repository, mock_session, sample_group_static):
        """Test group update with None values (should use current values)."""
        # Setup
        group_id = sample_group_static.id
        new_name = None
        new_faculty = None

        group_repository.GetById = MagicMock(return_value=sample_group_static)
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        # Execute
        result = group_repository.Update(group_id, new_name, new_faculty)

        # Assert
        assert result is True

    def test_update_group_not_found(self, group_repository, mock_session):
        """Test update when group doesn't exist."""
        # Setup
        group_id = 999999
        group_repository.GetById = MagicMock(return_value=None)

        # Execute
        result = group_repository.Update(group_id, "new_name", "new_faculty")

        # Assert
        assert result is False

    def test_update_database_error(self, group_repository, mock_session, sample_group_static):
        """Test update with database error."""
        # Setup
        group_id = sample_group_static.id
        group_repository.GetById = MagicMock(return_value=sample_group_static)
        mock_session.exec.side_effect = SQLAlchemyError("Database error")
        mock_session.rollback.return_value = None

        # Execute
        result = group_repository.Update(group_id, "new_name", "new_faculty")

        # Assert
        assert result is False
        mock_session.rollback.assert_called_once()

    def test_delete_success(self, group_repository, mock_session):
        """Test successful group deletion."""
        # Setup
        group_id = 123456
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        # Execute
        result = group_repository.Delete(group_id)

        # Assert
        assert result is True
        mock_session.exec.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_delete_no_rows_affected(self, group_repository, mock_session):
        """Test deletion when no rows are affected."""
        # Setup
        group_id = 999999
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        # Execute
        result = group_repository.Delete(group_id)

        # Assert
        assert result is False

    def test_delete_database_error(self, group_repository, mock_session):
        """Test deletion with database error."""
        # Setup
        group_id = 123456
        mock_session.exec.side_effect = SQLAlchemyError("Database error")
        mock_session.rollback.return_value = None

        # Execute
        result = group_repository.Delete(group_id)

        # Assert
        assert result is False
        mock_session.rollback.assert_called_once()


@pytest.mark.repositories
@pytest.mark.integration
class TestGroupRepositoryIntegration:
    """Integration tests for GroupRepository with real database session."""

    def test_create_and_retrieve_group(self, group_repository_clean, sample_group):
        """Test creating and retrieving a group with real database."""
        # Execute
        created_group = group_repository_clean.Create(sample_group)
        retrieved_group = group_repository_clean.GetById(sample_group.id)

        # Assert
        assert created_group.id == sample_group.id
        assert retrieved_group is not None
        assert retrieved_group.name == sample_group.name
        assert retrieved_group.faculty_name == sample_group.faculty_name

    def test_get_or_create_existing(self, group_repository_clean, sample_group):
        """Test GetOrCreate with existing group."""
        # Setup
        group_repository_clean.Create(sample_group)

        # Execute
        result = group_repository_clean.GetOrCreate(sample_group)

        # Assert
        assert result.id == sample_group.id

    def test_get_by_guid(self, group_repository_clean, sample_group):
        """Test retrieving group by GUID with real database."""
        # Setup
        group_repository_clean.Create(sample_group)

        # Execute
        result = group_repository_clean.GetByGUID(sample_group.guid)

        # Assert
        assert result is not None
        assert result.guid == sample_group.guid
        assert result.name == sample_group.name

    def test_get_by_name(self, group_repository_clean, multiple_groups):
        """Test retrieving groups by name with real database."""
        # Setup - создаем группы с разными именами, но потом ищем по одному имени
        for i, group in enumerate(multiple_groups):
            group.name = f"Test Group {i}"
            group_repository_clean.Create(group)

        # Execute - ищем первую группу по имени
        result = group_repository_clean.GetByName("Test Group 0")

        # Assert
        assert len(result) == 1
        assert result[0].name == "Test Group 0"

    def test_update_group_data(self, group_repository_clean, sample_group):
        """Test updating group data with real database."""
        # Setup
        group_repository_clean.Create(sample_group)

        # Execute
        result = group_repository_clean.Update(
            sample_group.id,
            name="Updated Group Name",
            faculty_name="Updated Faculty"
        )

        # Assert
        assert result is True

        # Verify update
        updated_group = group_repository_clean.GetById(sample_group.id)
        assert updated_group.name == "Updated Group Name"
        assert updated_group.faculty_name == "Updated Faculty"

    def test_update_with_none_values(self, group_repository_clean, sample_group):
        """Test updating group with None values (should keep current values)."""
        # Setup
        group_repository_clean.Create(sample_group)
        original_name = sample_group.name
        original_faculty = sample_group.faculty_name

        # Execute
        result = group_repository_clean.Update(
            sample_group.id,
            name=None,
            faculty_name=None
        )

        # Assert
        assert result is True

        # Verify values remain the same
        updated_group = group_repository_clean.GetById(sample_group.id)
        assert updated_group.name == original_name
        assert updated_group.faculty_name == original_faculty

    def test_list_all_groups(self, group_repository_clean, multiple_groups):
        """Test listing all groups with real database."""
        # Setup
        for group in multiple_groups:
            group_repository_clean.Create(group)

        # Execute
        all_groups = group_repository_clean.ListAll()

        # Assert
        assert len(all_groups) == 3
        for i, group in enumerate(all_groups):
            assert group.name == f"Group {group.id}"
            assert group.faculty_name == f"Faculty {i + 1}"

    def test_delete_group(self, group_repository_clean, sample_group):
        """Test deleting a group with real database."""
        # Setup
        group_repository_clean.Create(sample_group)

        # Verify group exists
        assert group_repository_clean.GetById(sample_group.id) is not None

        # Execute
        result = group_repository_clean.Delete(sample_group.id)

        # Assert
        assert result is True
        assert group_repository_clean.GetById(sample_group.id) is None

    def test_delete_nonexistent_group(self, group_repository_clean):
        """Test deleting a nonexistent group."""
        # Execute
        result = group_repository_clean.Delete(999999)

        # Assert
        assert result is False
