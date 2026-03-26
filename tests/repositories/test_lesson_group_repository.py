"""Unit tests for LessonGroupRepository."""

import pytest
from unittest.mock import MagicMock
from sqlalchemy.exc import SQLAlchemyError

import sys
from pathlib import Path

# Добавляем src в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from repositories.lesson_group_repository import LessonGroupRepository
from models.models import LessonGroup


@pytest.mark.repositories
@pytest.mark.unit
class TestLessonGroupRepository:
    """Test cases for LessonGroupRepository class."""

    def test_init(self, mock_session):
        """Test LessonGroupRepository initialization."""
        repo = LessonGroupRepository(mock_session)
        assert repo.session == mock_session

    def test_create_success(self, lesson_group_repository, sample_lesson_group, mock_session):
        """Test successful lesson-group creation."""
        mock_session.add.return_value = None
        mock_session.commit.return_value = None

        result = lesson_group_repository.Create(sample_lesson_group)

        assert result == sample_lesson_group
        mock_session.add.assert_called_once_with(sample_lesson_group)
        mock_session.commit.assert_called_once()

    def test_create_with_session_error(self, lesson_group_repository, sample_lesson_group, mock_session):
        """Test lesson-group creation with database error."""
        mock_session.add.side_effect = SQLAlchemyError("Database error")

        with pytest.raises(SQLAlchemyError):
            lesson_group_repository.Create(sample_lesson_group)

    def test_get_or_create_existing(self, lesson_group_repository, sample_lesson_group):
        """Test GetOrCreate when association already exists."""
        existing = LessonGroup(lesson_id=sample_lesson_group.lesson_id, group_id=sample_lesson_group.group_id)
        lesson_group_repository.GetByIds = MagicMock(return_value=existing)

        result = lesson_group_repository.GetOrCreate(sample_lesson_group)

        assert result == existing
        lesson_group_repository.GetByIds.assert_called_once_with(
            sample_lesson_group.lesson_id,
            sample_lesson_group.group_id,
        )

    def test_get_or_create_new(self, lesson_group_repository, sample_lesson_group):
        """Test GetOrCreate when association does not exist."""
        lesson_group_repository.GetByIds = MagicMock(return_value=None)
        lesson_group_repository.Create = MagicMock(return_value=sample_lesson_group)

        result = lesson_group_repository.GetOrCreate(sample_lesson_group)

        assert result == sample_lesson_group
        lesson_group_repository.GetByIds.assert_called_once_with(
            sample_lesson_group.lesson_id,
            sample_lesson_group.group_id,
        )
        lesson_group_repository.Create.assert_called_once_with(sample_lesson_group)

    def test_list_all_success(self, lesson_group_repository, mock_session):
        """Test successful listing of all associations."""
        expected = [LessonGroup(lesson_id=1, group_id=1), LessonGroup(lesson_id=1, group_id=2)]
        mock_result = MagicMock()
        mock_result.all.return_value = expected
        mock_session.exec.return_value = mock_result

        result = lesson_group_repository.ListAll()

        assert result == expected
        mock_session.exec.assert_called_once()

    def test_get_by_ids_success(self, lesson_group_repository, mock_session, sample_lesson_group):
        """Test successful association retrieval by composite key."""
        mock_result = MagicMock()
        mock_result.first.return_value = sample_lesson_group
        mock_session.exec.return_value = mock_result

        result = lesson_group_repository.GetByIds(1, 1)

        assert result == sample_lesson_group
        mock_session.exec.assert_called_once()

    def test_get_by_ids_not_found(self, lesson_group_repository, mock_session):
        """Test association retrieval when association does not exist."""
        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_session.exec.return_value = mock_result

        result = lesson_group_repository.GetByIds(999, 999)

        assert result is None

    def test_list_by_lesson_id_success(self, lesson_group_repository, mock_session):
        """Test listing associations by lesson ID."""
        expected = [LessonGroup(lesson_id=1, group_id=1), LessonGroup(lesson_id=1, group_id=2)]
        mock_result = MagicMock()
        mock_result.all.return_value = expected
        mock_session.exec.return_value = mock_result

        result = lesson_group_repository.ListByLessonId(1)

        assert result == expected
        mock_session.exec.assert_called_once()

    def test_list_by_group_id_success(self, lesson_group_repository, mock_session):
        """Test listing associations by group ID."""
        expected = [LessonGroup(lesson_id=1, group_id=1), LessonGroup(lesson_id=2, group_id=1)]
        mock_result = MagicMock()
        mock_result.all.return_value = expected
        mock_session.exec.return_value = mock_result

        result = lesson_group_repository.ListByGroupId(1)

        assert result == expected
        mock_session.exec.assert_called_once()

    def test_get_with_lesson_and_group_success(self, lesson_group_repository, mock_session, sample_lesson_group):
        """Test association retrieval with related lesson/group loaded."""
        mock_result = MagicMock()
        mock_result.first.return_value = sample_lesson_group
        mock_session.exec.return_value = mock_result

        result = lesson_group_repository.GetWithLessonAndGroup(1, 1)

        assert result == sample_lesson_group
        mock_session.exec.assert_called_once()

    def test_list_by_lesson_id_with_group_success(self, lesson_group_repository, mock_session):
        """Test listing associations by lesson ID with group loaded."""
        expected = [LessonGroup(lesson_id=1, group_id=1), LessonGroup(lesson_id=1, group_id=2)]
        mock_result = MagicMock()
        mock_result.all.return_value = expected
        mock_session.exec.return_value = mock_result

        result = lesson_group_repository.ListByLessonIdWithGroup(1)

        assert result == expected
        mock_session.exec.assert_called_once()

    def test_list_by_group_id_with_lesson_success(self, lesson_group_repository, mock_session):
        """Test listing associations by group ID with lesson loaded."""
        expected = [LessonGroup(lesson_id=1, group_id=1), LessonGroup(lesson_id=2, group_id=1)]
        mock_result = MagicMock()
        mock_result.all.return_value = expected
        mock_session.exec.return_value = mock_result

        result = lesson_group_repository.ListByGroupIdWithLesson(1)

        assert result == expected
        mock_session.exec.assert_called_once()

    def test_delete_success(self, lesson_group_repository, mock_session):
        """Test successful deletion by composite key."""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        result = lesson_group_repository.Delete(1, 1)

        assert result is True
        mock_session.exec.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_delete_no_rows_affected(self, lesson_group_repository, mock_session):
        """Test deletion when no rows are affected."""
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        result = lesson_group_repository.Delete(999, 999)

        assert result is False

    def test_delete_database_error(self, lesson_group_repository, mock_session):
        """Test deletion with database error."""
        mock_session.exec.side_effect = SQLAlchemyError("Database error")
        mock_session.rollback.return_value = None

        result = lesson_group_repository.Delete(1, 1)

        assert result is False
        mock_session.rollback.assert_called_once()

    def test_delete_by_lesson_id_success(self, lesson_group_repository, mock_session):
        """Test successful deletion by lesson ID."""
        mock_result = MagicMock()
        mock_result.rowcount = 2
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        result = lesson_group_repository.DeleteByLessonId(1)

        assert result is True
        mock_session.exec.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_delete_by_lesson_id_no_rows_affected(self, lesson_group_repository, mock_session):
        """Test deletion by lesson ID when no rows are affected."""
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        result = lesson_group_repository.DeleteByLessonId(999)

        assert result is False

    def test_delete_by_lesson_id_database_error(self, lesson_group_repository, mock_session):
        """Test deletion by lesson ID with database error."""
        mock_session.exec.side_effect = SQLAlchemyError("Database error")
        mock_session.rollback.return_value = None

        result = lesson_group_repository.DeleteByLessonId(1)

        assert result is False
        mock_session.rollback.assert_called_once()

    def test_delete_by_group_id_success(self, lesson_group_repository, mock_session):
        """Test successful deletion by group ID."""
        mock_result = MagicMock()
        mock_result.rowcount = 2
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        result = lesson_group_repository.DeleteByGroupId(1)

        assert result is True
        mock_session.exec.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_delete_by_group_id_no_rows_affected(self, lesson_group_repository, mock_session):
        """Test deletion by group ID when no rows are affected."""
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.exec.return_value = mock_result
        mock_session.commit.return_value = None

        result = lesson_group_repository.DeleteByGroupId(999)

        assert result is False

    def test_delete_by_group_id_database_error(self, lesson_group_repository, mock_session):
        """Test deletion by group ID with database error."""
        mock_session.exec.side_effect = SQLAlchemyError("Database error")
        mock_session.rollback.return_value = None

        result = lesson_group_repository.DeleteByGroupId(1)

        assert result is False
        mock_session.rollback.assert_called_once()


@pytest.mark.repositories
@pytest.mark.integration
class TestLessonGroupRepositoryIntegration:
    """Integration tests for LessonGroupRepository with real database session."""

    def test_create_and_retrieve_association(self, lesson_group_repository_clean, sample_lesson_group):
        """Test creating and retrieving association with real database."""
        created = lesson_group_repository_clean.Create(sample_lesson_group)
        retrieved = lesson_group_repository_clean.GetByIds(
            sample_lesson_group.lesson_id,
            sample_lesson_group.group_id,
        )

        assert created.lesson_id == sample_lesson_group.lesson_id
        assert created.group_id == sample_lesson_group.group_id
        assert retrieved is not None
        assert retrieved.lesson_id == sample_lesson_group.lesson_id
        assert retrieved.group_id == sample_lesson_group.group_id

    def test_get_or_create_existing(self, lesson_group_repository_clean, sample_lesson_group):
        """Test GetOrCreate with existing association."""
        lesson_group_repository_clean.Create(sample_lesson_group)

        result = lesson_group_repository_clean.GetOrCreate(sample_lesson_group)

        assert result.lesson_id == sample_lesson_group.lesson_id
        assert result.group_id == sample_lesson_group.group_id

    def test_list_by_lesson_id(self, lesson_group_repository_clean, multiple_lesson_groups):
        """Test listing associations by lesson ID with real database."""
        for item in multiple_lesson_groups:
            lesson_group_repository_clean.Create(item)

        result = lesson_group_repository_clean.ListByLessonId(1)

        assert len(result) == 2
        assert all(item.lesson_id == 1 for item in result)

    def test_list_by_group_id(self, lesson_group_repository_clean, multiple_lesson_groups):
        """Test listing associations by group ID with real database."""
        for item in multiple_lesson_groups:
            lesson_group_repository_clean.Create(item)

        result = lesson_group_repository_clean.ListByGroupId(1)

        assert len(result) == 2
        assert all(item.group_id == 1 for item in result)

    def test_get_with_lesson_and_group(self, lesson_group_repository_clean, sample_lesson_group):
        """Test retrieving association with related entities loaded."""
        lesson_group_repository_clean.Create(sample_lesson_group)

        result = lesson_group_repository_clean.GetWithLessonAndGroup(
            sample_lesson_group.lesson_id,
            sample_lesson_group.group_id,
        )

        assert result is not None
        assert result.lesson_id == sample_lesson_group.lesson_id
        assert result.group_id == sample_lesson_group.group_id

    def test_delete_association(self, lesson_group_repository_clean, sample_lesson_group):
        """Test deleting association with real database."""
        lesson_group_repository_clean.Create(sample_lesson_group)

        result = lesson_group_repository_clean.Delete(
            sample_lesson_group.lesson_id,
            sample_lesson_group.group_id,
        )

        assert result is True
        deleted = lesson_group_repository_clean.GetByIds(
            sample_lesson_group.lesson_id,
            sample_lesson_group.group_id,
        )
        assert deleted is None

    def test_delete_by_lesson_id(self, lesson_group_repository_clean, multiple_lesson_groups):
        """Test deleting associations by lesson ID with real database."""
        for item in multiple_lesson_groups:
            lesson_group_repository_clean.Create(item)

        result = lesson_group_repository_clean.DeleteByLessonId(1)

        assert result is True
        remaining = lesson_group_repository_clean.ListByLessonId(1)
        assert len(remaining) == 0

    def test_delete_by_group_id(self, lesson_group_repository_clean, multiple_lesson_groups):
        """Test deleting associations by group ID with real database."""
        for item in multiple_lesson_groups:
            lesson_group_repository_clean.Create(item)

        result = lesson_group_repository_clean.DeleteByGroupId(1)

        assert result is True
        remaining = lesson_group_repository_clean.ListByGroupId(1)
        assert len(remaining) == 0
