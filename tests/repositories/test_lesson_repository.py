"""Unit tests for LessonRepository."""

import datetime
import pytest
from unittest.mock import MagicMock
from sqlalchemy.exc import SQLAlchemyError

import sys
from pathlib import Path

# Добавляем src в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from repositories.lesson_repository import LessonRepository
from models.models import Lesson


@pytest.mark.repositories
@pytest.mark.unit
class TestLessonRepository:
    """Test cases for LessonRepository class."""

    def test_init(self, mock_session):
        repo = LessonRepository(mock_session)
        assert repo.session == mock_session

    def test_create_success(self, lesson_repository, sample_lesson_static, mock_session):
        mock_session.add.return_value = None
        mock_session.commit.return_value = None

        result = lesson_repository.Create(sample_lesson_static)

        assert result == sample_lesson_static
        mock_session.add.assert_called_once_with(sample_lesson_static)
        mock_session.commit.assert_called_once()

    def test_create_with_session_error(self, lesson_repository, sample_lesson_static, mock_session):
        mock_session.add.side_effect = SQLAlchemyError("Database error")
        with pytest.raises(SQLAlchemyError):
            lesson_repository.Create(sample_lesson_static)

    def test_bulk_save_lessons_success(self, lesson_repository, multiple_lessons, mock_session):
        lesson_repository.BulkSaveLessons(multiple_lessons)
        mock_session.bulk_save_objects.assert_called_once_with(multiple_lessons)
        mock_session.commit.assert_called_once()

    def test_get_or_create_existing(self, lesson_repository, sample_lesson_static):
        lesson_repository.GetById = MagicMock(return_value=sample_lesson_static)
        result = lesson_repository.GetOrCreate(sample_lesson_static)
        assert result == sample_lesson_static
        lesson_repository.GetById.assert_called_once_with(sample_lesson_static.id)

    def test_get_or_create_new(self, lesson_repository, sample_lesson_static):
        lesson_repository.GetById = MagicMock(return_value=None)
        lesson_repository.Create = MagicMock(return_value=sample_lesson_static)
        result = lesson_repository.GetOrCreate(sample_lesson_static)
        assert result == sample_lesson_static
        lesson_repository.Create.assert_called_once_with(sample_lesson_static)

    def test_list_all_success(self, lesson_repository, mock_session, multiple_lessons):
        mock_result = MagicMock()
        mock_result.all.return_value = multiple_lessons
        mock_session.exec.return_value = mock_result
        result = lesson_repository.ListAll()
        assert result == multiple_lessons

    def test_get_by_id_success(self, lesson_repository, mock_session, sample_lesson_static):
        mock_result = MagicMock()
        mock_result.first.return_value = sample_lesson_static
        mock_session.exec.return_value = mock_result
        result = lesson_repository.GetById(sample_lesson_static.id)
        assert result == sample_lesson_static

    def test_get_by_id_not_found(self, lesson_repository, mock_session):
        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_session.exec.return_value = mock_result
        assert lesson_repository.GetById(999999) is None

    def test_get_with_relations_success(self, lesson_repository, mock_session, sample_lesson_static):
        mock_result = MagicMock()
        mock_result.first.return_value = sample_lesson_static
        mock_session.exec.return_value = mock_result
        result = lesson_repository.GetWithRelations(sample_lesson_static.id)
        assert result == sample_lesson_static

    def test_list_by_date_success(self, lesson_repository, mock_session, sample_lesson_static):
        mock_result = MagicMock()
        mock_result.all.return_value = [sample_lesson_static]
        mock_session.exec.return_value = mock_result
        result = lesson_repository.ListByDate(sample_lesson_static.date)
        assert len(result) == 1

    def test_list_by_date_range_success(self, lesson_repository, mock_session, multiple_lessons):
        mock_result = MagicMock()
        mock_result.all.return_value = multiple_lessons
        mock_session.exec.return_value = mock_result
        result = lesson_repository.ListByDateRange(datetime.date(2025, 1, 1), datetime.date(2025, 1, 3))
        assert len(result) == 3

    def test_list_by_lecturer_id_success(self, lesson_repository, mock_session, sample_lesson_static):
        mock_result = MagicMock()
        mock_result.all.return_value = [sample_lesson_static]
        mock_session.exec.return_value = mock_result
        result = lesson_repository.ListByLecturerId(sample_lesson_static.lecturer_id)
        assert len(result) == 1

    def test_list_by_discipline_id_success(self, lesson_repository, mock_session, sample_lesson_static):
        mock_result = MagicMock()
        mock_result.all.return_value = [sample_lesson_static]
        mock_session.exec.return_value = mock_result
        result = lesson_repository.ListByDisciplineId(sample_lesson_static.discipline_id)
        assert len(result) == 1

    def test_list_by_auditorium_id_success(self, lesson_repository, mock_session, sample_lesson_static):
        mock_result = MagicMock()
        mock_result.all.return_value = [sample_lesson_static]
        mock_session.exec.return_value = mock_result
        result = lesson_repository.ListByAuditoriumId(sample_lesson_static.auditorium_id)
        assert len(result) == 1

    def test_list_by_kind_of_work_id_success(self, lesson_repository, mock_session, sample_lesson_static):
        mock_result = MagicMock()
        mock_result.all.return_value = [sample_lesson_static]
        mock_session.exec.return_value = mock_result
        result = lesson_repository.ListByKindOfWorkId(sample_lesson_static.kind_of_work_id)
        assert len(result) == 1

    def test_list_by_sub_group_success(self, lesson_repository, mock_session, sample_lesson_static):
        mock_result = MagicMock()
        mock_result.all.return_value = [sample_lesson_static]
        mock_session.exec.return_value = mock_result
        result = lesson_repository.ListBySubGroup(sample_lesson_static.sub_group)
        assert len(result) == 1

    def test_update_success(self, lesson_repository, mock_session, sample_lesson_static):
        lesson_repository.GetById = MagicMock(return_value=sample_lesson_static)
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.exec.return_value = mock_result

        result = lesson_repository.Update(
            sample_lesson_static.id,
            kind_of_work_id=2,
            discipline_id=2,
            auditorium_id=2,
            lecturer_id=2,
            date=datetime.date(2025, 1, 2),
            begin_lesson=datetime.time(11, 0),
            end_lesson=datetime.time(12, 0),
            sub_group=2,
        )
        assert result is True
        mock_session.commit.assert_called_once()

    def test_update_with_none_values(self, lesson_repository, mock_session, sample_lesson_static):
        lesson_repository.GetById = MagicMock(return_value=sample_lesson_static)
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.exec.return_value = mock_result
        result = lesson_repository.Update(sample_lesson_static.id)
        assert result is True

    def test_update_not_found(self, lesson_repository):
        lesson_repository.GetById = MagicMock(return_value=None)
        assert lesson_repository.Update(999999) is False

    def test_update_database_error(self, lesson_repository, mock_session, sample_lesson_static):
        lesson_repository.GetById = MagicMock(return_value=sample_lesson_static)
        mock_session.exec.side_effect = SQLAlchemyError("Database error")
        assert lesson_repository.Update(sample_lesson_static.id) is False
        mock_session.rollback.assert_called_once()

    def test_update_updated_at_success(self, lesson_repository, mock_session):
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.exec.return_value = mock_result
        assert lesson_repository.UpdateUpdatedAt(1) is True
        mock_session.commit.assert_called_once()

    def test_update_updated_at_database_error(self, lesson_repository, mock_session):
        mock_session.exec.side_effect = SQLAlchemyError("Database error")
        assert lesson_repository.UpdateUpdatedAt(1) is False
        mock_session.rollback.assert_called_once()

    def test_delete_success(self, lesson_repository, mock_session):
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.exec.return_value = mock_result
        assert lesson_repository.Delete(1) is True
        mock_session.commit.assert_called_once()

    def test_delete_database_error(self, lesson_repository, mock_session):
        mock_session.exec.side_effect = SQLAlchemyError("Database error")
        assert lesson_repository.Delete(1) is False
        mock_session.rollback.assert_called_once()

    def test_delete_all_success(self, lesson_repository, mock_session):
        mock_result = MagicMock()
        mock_result.rowcount = 3
        mock_session.exec.return_value = mock_result
        assert lesson_repository.DeleteAll() is True
        mock_session.commit.assert_called_once()

    def test_delete_all_database_error(self, lesson_repository, mock_session):
        mock_session.exec.side_effect = SQLAlchemyError("Database error")
        assert lesson_repository.DeleteAll() is False
        mock_session.rollback.assert_called_once()


@pytest.mark.repositories
@pytest.mark.integration
class TestLessonRepositoryIntegration:
    def test_create_and_get(self, lesson_repository_clean, sample_lesson):
        created = lesson_repository_clean.Create(sample_lesson)
        retrieved = lesson_repository_clean.GetById(sample_lesson.id)
        assert created.id == sample_lesson.id
        assert retrieved is not None

    def test_get_or_create_existing(self, lesson_repository_clean, sample_lesson):
        lesson_repository_clean.Create(sample_lesson)
        result = lesson_repository_clean.GetOrCreate(sample_lesson)
        assert result.id == sample_lesson.id

    def test_bulk_save_lessons(self, lesson_repository_clean, multiple_lessons):
        lesson_repository_clean.BulkSaveLessons(multiple_lessons)
        all_lessons = lesson_repository_clean.ListAll()
        assert len(all_lessons) == 3

    def test_list_filters(self, lesson_repository_clean, multiple_lessons):
        for lesson in multiple_lessons:
            lesson_repository_clean.Create(lesson)
        assert len(lesson_repository_clean.ListByDate(datetime.date(2025, 1, 1))) == 1
        assert len(lesson_repository_clean.ListByDateRange(datetime.date(2025, 1, 1), datetime.date(2025, 1, 3))) == 3
        assert len(lesson_repository_clean.ListByLecturerId(1)) == 2
        assert len(lesson_repository_clean.ListByDisciplineId(2)) == 2
        assert len(lesson_repository_clean.ListByAuditoriumId(1)) == 2
        assert len(lesson_repository_clean.ListByKindOfWorkId(1)) == 2
        assert len(lesson_repository_clean.ListBySubGroup(1)) == 2

    def test_update_lesson(self, lesson_repository_clean, sample_lesson):
        lesson_repository_clean.Create(sample_lesson)
        result = lesson_repository_clean.Update(sample_lesson.id, sub_group=3)
        assert result is True
        updated = lesson_repository_clean.GetById(sample_lesson.id)
        assert updated.sub_group == 3

    def test_update_updated_at(self, lesson_repository_clean, sample_lesson):
        lesson_repository_clean.Create(sample_lesson)
        assert lesson_repository_clean.UpdateUpdatedAt(sample_lesson.id) is True

    def test_delete_lesson(self, lesson_repository_clean, sample_lesson):
        lesson_repository_clean.Create(sample_lesson)
        assert lesson_repository_clean.Delete(sample_lesson.id) is True
        assert lesson_repository_clean.GetById(sample_lesson.id) is None

    def test_delete_all(self, lesson_repository_clean, multiple_lessons):
        for lesson in multiple_lessons:
            lesson_repository_clean.Create(lesson)
        assert lesson_repository_clean.DeleteAll() is True
        assert len(lesson_repository_clean.ListAll()) == 0
