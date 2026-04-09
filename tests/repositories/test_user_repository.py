"""Unit tests for UserRepository."""

import datetime
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError



from ruz_server.repositories.user_repository import UserRepository
from ruz_server.models.models import User


@pytest.mark.repositories
@pytest.mark.unit
class TestUserRepository:
    """Test cases for UserRepository class."""

    def test_init(self, mock_session):
        """Test UserRepository initialization."""
        repo = UserRepository(mock_session)
        assert repo.session == mock_session

    def test_create_success(self, user_repository, sample_user_static, mock_session):
        """Test successful user creation."""
        # Setup
        mock_session.add.return_value = None
        mock_session.commit.return_value = None

        # Execute
        result = user_repository.Create(sample_user_static)

        # Assert
        assert result == sample_user_static
        mock_session.add.assert_called_once_with(sample_user_static)
        mock_session.commit.assert_called_once()

    def test_create_with_session_error(self, user_repository, sample_user_static, mock_session):
        """Test user creation with database error."""
        # Setup
        mock_session.add.side_effect = SQLAlchemyError("Database error")

        # Execute & Assert
        with pytest.raises(SQLAlchemyError):
            user_repository.Create(sample_user_static)

    def test_get_or_create_existing_user(self, user_repository, sample_user_static, mock_session):
        """Test GetOrCreate when user already exists."""
        # Setup
        existing_user = User(id=sample_user_static.id, username="existing_user")
        user_repository.GetById = MagicMock(return_value=existing_user)

        # Execute
        result = user_repository.GetOrCreate(sample_user_static)

        # Assert
        assert result == existing_user
        user_repository.GetById.assert_called_once_with(sample_user_static.id)

    def test_get_or_create_new_user(self, user_repository, sample_user_static, mock_session):
        """Test GetOrCreate when user doesn't exist."""
        # Setup
        user_repository.GetById = MagicMock(return_value=None)
        user_repository.Create = MagicMock(return_value=sample_user_static)

        # Execute
        result = user_repository.GetOrCreate(sample_user_static)

        # Assert
        assert result == sample_user_static
        user_repository.GetById.assert_called_once_with(sample_user_static.id)
        user_repository.Create.assert_called_once_with(sample_user_static)

    def test_list_all_success(self, user_repository, mock_session):
        """Test successful listing of all users."""
        # Setup
        expected_users = [
            User(id=1, username="user1"),
            User(id=2, username="user2")
        ]
        mock_result = MagicMock()
        mock_result.all.return_value = expected_users
        mock_session.exec.return_value = mock_result

        # Execute
        result = user_repository.ListAll()

        # Assert
        assert result == expected_users
        mock_session.exec.assert_called_once()

    def test_list_by_group_oid_success(self, user_repository, mock_session):
        """Test successful listing by group ID."""
        # Setup
        group_oid = 123
        expected_users = [User(id=1, username="user1", group_oid=group_oid)]
        mock_result = MagicMock()
        mock_result.all.return_value = expected_users
        mock_session.exec.return_value = mock_result

        # Execute
        result = user_repository.ListByGroupOid(group_oid)

        # Assert
        assert result == expected_users
        mock_session.exec.assert_called_once()

    def test_get_by_id_success(self, user_repository, mock_session, sample_user_static):
        """Test successful user retrieval by ID."""
        # Setup
        user_id = sample_user_static.id
        mock_result = MagicMock()
        mock_result.first.return_value = sample_user_static
        mock_session.exec.return_value = mock_result

        # Execute
        result = user_repository.GetById(user_id)

        # Assert
        assert result == sample_user_static
        mock_session.exec.assert_called_once()

    def test_get_by_id_not_found(self, user_repository, mock_session):
        """Test user retrieval by ID when user doesn't exist."""
        # Setup
        user_id = 999999
        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_session.exec.return_value = mock_result

        # Execute
        result = user_repository.GetById(user_id)

        # Assert
        assert result is None

    def test_get_by_username_success(self, user_repository, mock_session, sample_user_static):
        """Test successful user retrieval by username."""
        # Setup
        username = sample_user_static.username
        mock_result = MagicMock()
        mock_result.first.return_value = sample_user_static
        mock_session.exec.return_value = mock_result

        # Execute
        result = user_repository.GetByUsername(username)

        # Assert
        assert result == sample_user_static
        mock_session.exec.assert_called_once()

    def test_get_by_username_not_found(self, user_repository, mock_session):
        """Test user retrieval by username when user doesn't exist."""
        # Setup
        username = "nonexistent_user"
        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_session.exec.return_value = mock_result

        # Execute
        result = user_repository.GetByUsername(username)

        # Assert
        assert result is None

    def test_get_with_group_success(self, user_repository, mock_session, user_with_group_static):
        """Test successful user retrieval with group."""
        # Setup
        user_id = user_with_group_static.id
        mock_result = MagicMock()
        mock_result.first.return_value = user_with_group_static
        mock_session.exec.return_value = mock_result

        # Execute
        result = user_repository.GetWithGroup(user_id)

        # Assert
        assert result == user_with_group_static
        mock_session.exec.assert_called_once()

    def test_update_success(self, user_repository, mock_session, sample_user_static):
        """Test successful user update."""
        # Setup
        user_id = sample_user_static.id
        new_username = "updated_username"
        new_group_oid = 456
        new_subgroup = 2

        user_repository.GetById = MagicMock(return_value=sample_user_static)
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        # Execute
        result = user_repository.Update(
            user_id,
            username=new_username,
            group_oid=new_group_oid,
            subgroup=new_subgroup
        )

        # Assert
        assert result is True
        mock_session.exec.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_update_partial_data(self, user_repository, mock_session, sample_user_static):
        """Test user update with partial data."""
        # Setup
        user_id = sample_user_static.id
        new_username = "updated_username"

        user_repository.GetById = MagicMock(return_value=sample_user_static)
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        # Execute
        result = user_repository.Update(user_id, username=new_username)

        # Assert
        assert result is True

    def test_update_user_not_found(self, user_repository, mock_session):
        """Test update when user doesn't exist."""
        # Setup
        user_id = 999999
        user_repository.GetById = MagicMock(return_value=None)

        # Execute
        result = user_repository.Update(user_id, username="new_username")

        # Assert
        assert result is False

    def test_update_database_error(self, user_repository, mock_session, sample_user_static):
        """Test update with database error."""
        # Setup
        user_id = sample_user_static.id
        user_repository.GetById = MagicMock(return_value=sample_user_static)
        mock_session.exec.side_effect = SQLAlchemyError("Database error")
        mock_session.rollback.return_value = None

        # Execute
        result = user_repository.Update(user_id, username="new_username")

        # Assert
        assert result is False
        mock_session.rollback.assert_called_once()

    def test_update_last_used_at_success(self, user_repository, mock_session):
        """Test successful last used at update."""
        # Setup
        user_id = 123456
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        # Execute
        result = user_repository.UpdateLastUsedAt(user_id)

        # Assert
        assert result is True
        mock_session.exec.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_update_last_used_at_no_rows_affected(self, user_repository, mock_session):
        """Test last used at update when no rows are affected."""
        # Setup
        user_id = 999999
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        # Execute
        result = user_repository.UpdateLastUsedAt(user_id)

        # Assert
        assert result is False

    def test_update_last_used_at_database_error(self, user_repository, mock_session):
        """Test last used at update with database error."""
        # Setup
        user_id = 123456
        mock_session.exec.side_effect = SQLAlchemyError("Database error")
        mock_session.rollback.return_value = None

        # Execute
        result = user_repository.UpdateLastUsedAt(user_id)

        # Assert
        assert result is False
        mock_session.rollback.assert_called_once()

    def test_delete_success(self, user_repository, mock_session):
        """Test successful user deletion."""
        # Setup
        user_id = 123456
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        # Execute
        result = user_repository.Delete(user_id)

        # Assert
        assert result is True
        mock_session.exec.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_delete_no_rows_affected(self, user_repository, mock_session):
        """Test deletion when no rows are affected."""
        # Setup
        user_id = 999999
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        # Execute
        result = user_repository.Delete(user_id)

        # Assert
        assert result is False

    def test_delete_database_error(self, user_repository, mock_session):
        """Test deletion with database error."""
        # Setup
        user_id = 123456
        mock_session.exec.side_effect = SQLAlchemyError("Database error")
        mock_session.rollback.return_value = None

        # Execute
        result = user_repository.Delete(user_id)

        # Assert
        assert result is False
        mock_session.rollback.assert_called_once()


@pytest.mark.repositories
@pytest.mark.integration
class TestUserRepositoryIntegration:
    """Integration tests for UserRepository with real database session."""

    def test_create_and_retrieve_user(self, user_repository_clean, sample_user):
        """Test creating and retrieving a user with real database."""
        # Execute
        created_user = user_repository_clean.Create(sample_user)
        retrieved_user = user_repository_clean.GetById(sample_user.id)

        # Assert
        assert created_user.id == sample_user.id
        assert retrieved_user is not None
        assert retrieved_user.username == sample_user.username
        assert retrieved_user.group_oid == sample_user.group_oid

    def test_get_or_create_existing(self, user_repository_clean, sample_user):
        """Test GetOrCreate with existing user."""
        # Setup
        user_repository_clean.Create(sample_user)

        # Execute
        result = user_repository_clean.GetOrCreate(sample_user)

        # Assert
        assert result.id == sample_user.id

    def test_update_user_data(self, user_repository_clean, sample_user):
        """Test updating user data with real database."""
        # Setup
        user_repository_clean.Create(sample_user)

        # Execute
        result = user_repository_clean.Update(
            sample_user.id,
            username="updated_user",
            group_oid=999
        )

        # Assert
        assert result is True

        # Verify update
        updated_user = user_repository_clean.GetById(sample_user.id)
        assert updated_user.username == "updated_user"
        assert updated_user.group_oid == 999

    def test_list_users_by_group(self, user_repository_clean, multiple_users):
        """Test listing users by group ID with real database."""
        # Setup
        for user in multiple_users:
            user_repository_clean.Create(user)

        # Execute
        users_in_group_1 = user_repository_clean.ListByGroupOid(1)

        # Assert
        assert len(users_in_group_1) == 1
        assert users_in_group_1[0].group_oid == 1

    def test_delete_user(self, user_repository_clean, sample_user):
        """Test deleting a user with real database."""
        # Setup
        user_repository_clean.Create(sample_user)

        # Verify user exists
        assert user_repository_clean.GetById(sample_user.id) is not None

        # Execute
        result = user_repository_clean.Delete(sample_user.id)

        # Assert
        assert result is True
        assert user_repository_clean.GetById(sample_user.id) is None
