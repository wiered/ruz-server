import datetime
import logging
from typing import Iterable, List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, delete, select, update

from ruz_server.models import Lesson, LessonGroup

logger = logging.getLogger(__name__)


class LessonRepository:
    def __init__(self, session: Session):
        self.session = session

    def Create(self, lesson: Lesson) -> Lesson:
        """Creates a new lesson.

        Args:
            lesson (Lesson): The lesson to create.

        Returns:
            Lesson: The created lesson.
        """
        logger.info(f"Creating lesson {lesson}")

        self.session.add(lesson)
        self.session.commit()
        return lesson

    def BulkSaveLessons(self, lessons: List[Lesson]) -> None:
        """Saves a list of lessons to the database.

        Args:
            lessons (List[Lesson]): A list of lessons to save.

        Returns:
            None
        """
        self.session.bulk_save_objects(lessons)
        self.session.commit()

    def GetOrCreate(self, lesson: Lesson) -> Lesson:
        """Gets a lesson by ID or creates it if it doesn't exist.

        Args:
            lesson (Lesson): The lesson instance to get or create.

        Returns:
            Lesson: The existing or newly created lesson.
        """
        logger.info(f"Getting or creating lesson {lesson}")

        existing = self.GetById(lesson.id)
        if existing:
            logger.debug(f"Lesson {lesson} already exists")
            return existing

        logger.debug(f"Lesson {lesson} does not exist, creating")
        return self.Create(lesson)

    def ListAll(self) -> List[Lesson]:
        """Returns a list of all lessons.

        Returns:
            List[Lesson]: List of lessons.
        """
        logger.info("Listing all lessons")

        stmt = select(Lesson)
        return self.session.exec(stmt).all()

    def GetById(self, value: int) -> Optional[Lesson]:
        """Returns a lesson by ID.

        Args:
            value (int): ID of the lesson.

        Returns:
            Optional[Lesson]: The lesson if found, otherwise None.
        """
        logger.info(f"Getting lesson by ID {value}")

        stmt = select(Lesson).where(Lesson.id == value)
        return self.session.exec(stmt).first()

    def GetWithRelations(self, value: int) -> Optional[Lesson]:
        """Returns a lesson by ID with related entities eagerly loaded.

        Args:
            value (int): ID of the lesson.

        Returns:
            Optional[Lesson]: The lesson with relations if found, otherwise None.
        """
        logger.info(f"Getting lesson by ID {value}")

        stmt = (
            select(Lesson)
            .where(Lesson.id == value)
            .options(
                selectinload(Lesson.kind_of_work),
                selectinload(Lesson.discipline),
                selectinload(Lesson.auditorium),
                selectinload(Lesson.lecturer),
                selectinload(Lesson.lesson_groups),
                selectinload(Lesson.groups),
            )
        )
        return self.session.exec(stmt).first()

    def ListByDate(self, value: datetime.date) -> List[Lesson]:
        """Returns a list of lessons for a specific date.

        Args:
            value (datetime.date): Target date.

        Returns:
            List[Lesson]: List of lessons on the given date.
        """
        logger.info(f"Listing lessons for date {value}")

        stmt = select(Lesson).where(Lesson.date == value)
        return self.session.exec(stmt).all()

    def ListByDateRange(self, start: datetime.date, end: datetime.date) -> List[Lesson]:
        """Returns a list of lessons within a date range (inclusive).

        Args:
            start (datetime.date): Start date.
            end (datetime.date): End date.

        Returns:
            List[Lesson]: List of lessons in the date range.
        """
        logger.info(f"Listing lessons for date range {start} to {end}")

        stmt = select(Lesson).where(Lesson.date >= start, Lesson.date <= end)
        return self.session.exec(stmt).all()

    def ListForUserByDateRange(
        self,
        group_id: int,
        subgroup: int,
        start: datetime.date,
        end: datetime.date,
    ) -> List[Lesson]:
        """Return lessons for a user's group/date range with subgroup policy.

        Subgroup policy: include common lessons (`sub_group=0`) and lessons
        for the user's subgroup.
        """
        logger.info(
            "Listing user lessons for group %s in range %s..%s",
            group_id,
            start,
            end,
        )
        stmt = (
            select(Lesson)
            .join(LessonGroup, LessonGroup.lesson_id == Lesson.id)
            .where(
                LessonGroup.group_id == group_id,
                Lesson.date >= start,
                Lesson.date <= end,
                Lesson.sub_group.in_([0, subgroup]),
            )
            .order_by(Lesson.date, Lesson.begin_lesson)
            .options(
                selectinload(Lesson.kind_of_work),
                selectinload(Lesson.discipline),
                selectinload(Lesson.auditorium),
                selectinload(Lesson.lecturer),
                selectinload(Lesson.lesson_groups),
            )
        )
        # One lesson may be linked multiple times in joins; return unique rows.
        return list(self.session.exec(stmt).unique().all())

    def ListByLecturerId(self, value: int) -> List[Lesson]:
        """Returns a list of lessons by lecturer ID.

        Args:
            value (int): Lecturer ID.

        Returns:
            List[Lesson]: List of lessons for the lecturer.
        """
        logger.info(f"Listing lessons for lecturer ID {value}")

        stmt = select(Lesson).where(Lesson.lecturer_id == value)
        return self.session.exec(stmt).all()

    def _build_search_stmt(
        self,
        *,
        lecturer_id: Optional[int] = None,
        discipline_id: Optional[int] = None,
        start: datetime.date,
        end: datetime.date,
        group_id: Optional[int] = None,
        sub_group: Optional[int] = None,
    ):
        stmt = select(Lesson)
        if group_id is not None:
            stmt = stmt.join(LessonGroup, LessonGroup.lesson_id == Lesson.id)

        conditions = [
            Lesson.date >= start,
            Lesson.date <= end,
        ]
        if lecturer_id is not None:
            conditions.append(Lesson.lecturer_id == lecturer_id)
        if discipline_id is not None:
            conditions.append(Lesson.discipline_id == discipline_id)
        if group_id is not None:
            conditions.append(LessonGroup.group_id == group_id)
        if sub_group is not None:
            conditions.append(Lesson.sub_group == sub_group)

        stmt = (
            stmt.where(*conditions)
            .order_by(Lesson.date, Lesson.begin_lesson)
            .options(
                selectinload(Lesson.kind_of_work),
                selectinload(Lesson.discipline),
                selectinload(Lesson.auditorium),
                selectinload(Lesson.lecturer),
                selectinload(Lesson.lesson_groups),
            )
        )
        return stmt

    def ListByLecturerAndDate(
        self,
        lecturer_id: int,
        value: datetime.date,
        group_id: Optional[int] = None,
        sub_group: Optional[int] = None,
    ) -> List[Lesson]:
        return self.ListByLecturerAndDateRange(
            lecturer_id=lecturer_id,
            start=value,
            end=value,
            group_id=group_id,
            sub_group=sub_group,
        )

    def ListByLecturerAndDateRange(
        self,
        lecturer_id: int,
        start: datetime.date,
        end: datetime.date,
        group_id: Optional[int] = None,
        sub_group: Optional[int] = None,
    ) -> List[Lesson]:
        stmt = self._build_search_stmt(
            lecturer_id=lecturer_id,
            start=start,
            end=end,
            group_id=group_id,
            sub_group=sub_group,
        )
        return list(self.session.exec(stmt).unique().all())

    def ListByDisciplineId(self, value: int) -> List[Lesson]:
        """Returns a list of lessons by discipline ID.

        Args:
            value (int): Discipline ID.

        Returns:
            List[Lesson]: List of lessons for the discipline.
        """
        logger.info(f"Listing lessons for discipline ID {value}")

        stmt = select(Lesson).where(Lesson.discipline_id == value)
        return self.session.exec(stmt).all()

    def ListByDisciplineAndDate(
        self,
        discipline_id: int,
        value: datetime.date,
        group_id: Optional[int] = None,
        sub_group: Optional[int] = None,
    ) -> List[Lesson]:
        return self.ListByDisciplineAndDateRange(
            discipline_id=discipline_id,
            start=value,
            end=value,
            group_id=group_id,
            sub_group=sub_group,
        )

    def ListByDisciplineAndDateRange(
        self,
        discipline_id: int,
        start: datetime.date,
        end: datetime.date,
        group_id: Optional[int] = None,
        sub_group: Optional[int] = None,
    ) -> List[Lesson]:
        stmt = self._build_search_stmt(
            discipline_id=discipline_id,
            start=start,
            end=end,
            group_id=group_id,
            sub_group=sub_group,
        )
        return list(self.session.exec(stmt).unique().all())

    def ListByAuditoriumId(self, value: int) -> List[Lesson]:
        """Returns a list of lessons by auditorium ID.

        Args:
            value (int): Auditorium ID.

        Returns:
            List[Lesson]: List of lessons for the auditorium.
        """
        logger.info(f"Listing lessons for auditorium ID {value}")

        stmt = select(Lesson).where(Lesson.auditorium_id == value)
        return self.session.exec(stmt).all()

    def ListByKindOfWorkId(self, value: int) -> List[Lesson]:
        """Returns a list of lessons by kind of work ID.

        Args:
            value (int): Kind of work ID.

        Returns:
            List[Lesson]: List of lessons matching the kind of work.
        """
        logger.info(f"Listing lessons for kind of work ID {value}")

        stmt = select(Lesson).where(Lesson.kind_of_work_id == value)
        return self.session.exec(stmt).all()

    def ListBySubGroup(self, value: int) -> List[Lesson]:
        """Returns a list of lessons by subgroup.

        Args:
            value (int): Subgroup number.

        Returns:
            List[Lesson]: List of lessons for the subgroup.
        """
        logger.info(f"Listing lessons for subgroup {value}")

        stmt = select(Lesson).where(Lesson.sub_group == value)
        return self.session.exec(stmt).all()

    def Upsert(self, lesson: Lesson) -> tuple[Lesson, bool]:
        """Insert or update a lesson by primary key without committing.

        Returns:
            tuple[Lesson, bool]: (lesson, created_flag)
        """
        logger.info(f"Upserting lesson {lesson.id}")
        existing = self.GetById(lesson.id)
        if existing is None:
            self.session.add(lesson)
            return lesson, True

        existing.kind_of_work_id = lesson.kind_of_work_id
        existing.discipline_id = lesson.discipline_id
        existing.auditorium_id = lesson.auditorium_id
        existing.lecturer_id = lesson.lecturer_id
        existing.date = lesson.date
        existing.begin_lesson = lesson.begin_lesson
        existing.end_lesson = lesson.end_lesson
        existing.sub_group = lesson.sub_group
        existing.updated_at = datetime.datetime.now(datetime.timezone.utc)
        self.session.add(existing)
        return existing, False

    def BulkUpsert(self, lessons: Iterable[Lesson]) -> tuple[int, int]:
        """Upsert lessons collection without committing.

        Returns:
            tuple[int, int]: (created_count, updated_count)
        """
        created_count = 0
        updated_count = 0
        for lesson in lessons:
            _, created = self.Upsert(lesson)
            if created:
                created_count += 1
            else:
                updated_count += 1
        return created_count, updated_count

    def ListIdsInDateRange(self, start: datetime.date, end: datetime.date) -> List[int]:
        """List lesson IDs inside date range (inclusive)."""
        logger.info(f"Listing lesson IDs for date range {start} to {end}")
        stmt = select(Lesson.id).where(Lesson.date >= start, Lesson.date <= end)
        return list(self.session.exec(stmt).all())

    def DeleteByIds(self, lesson_ids: Iterable[int]) -> int:
        """Delete lessons by IDs without committing.

        Returns:
            int: number of deleted rows
        """
        ids = list(lesson_ids)
        if not ids:
            return 0
        logger.info(f"Deleting {len(ids)} lessons by IDs")
        stmt = delete(Lesson).where(Lesson.id.in_(ids))
        result = self.session.exec(stmt)
        return int(result.rowcount or 0)

    def Update(
        self,
        value: int,
        kind_of_work_id: Optional[int] = None,
        discipline_id: Optional[int] = None,
        auditorium_id: Optional[int] = None,
        lecturer_id: Optional[int] = None,
        date: Optional[datetime.date] = None,
        begin_lesson: Optional[datetime.time] = None,
        end_lesson: Optional[datetime.time] = None,
        sub_group: Optional[int] = None,
    ) -> bool:
        """Updates a lesson by ID.

        Args:
            value (int): ID of the lesson to update.
            kind_of_work_id (Optional[int], optional): New kind_of_work_id.
            discipline_id (Optional[int], optional): New discipline_id.
            auditorium_id (Optional[int], optional): New auditorium_id.
            lecturer_id (Optional[int], optional): New lecturer_id.
            date (Optional[datetime.date], optional): New date.
            begin_lesson (Optional[datetime.time], optional): New begin time.
            end_lesson (Optional[datetime.time], optional): New end time.
            sub_group (Optional[int], optional): New subgroup value.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        logger.info(f"Updating Lesson {value}")

        try:
            current = self.GetById(value)
            if not current:
                logger.error(f"Lesson {value} not found")
                return False

            if kind_of_work_id is None:
                logger.debug(f"Payload kind_of_work_id is None")
                kind_of_work_id = current.kind_of_work_id

            if discipline_id is None:
                logger.debug(f"Payload discipline_id is None")
                discipline_id = current.discipline_id

            if auditorium_id is None:
                logger.debug(f"Payload auditorium_id is None")
                auditorium_id = current.auditorium_id

            if lecturer_id is None:
                logger.debug(f"Payload lecturer_id is None")
                lecturer_id = current.lecturer_id

            if date is None:
                logger.debug(f"Payload date is None")
                date = current.date

            if begin_lesson is None:
                logger.debug(f"Payload begin_lesson is None")
                begin_lesson = current.begin_lesson

            if end_lesson is None:
                logger.debug(f"Payload end_lesson is None")
                end_lesson = current.end_lesson

            if sub_group is None:
                logger.debug(f"Payload sub_group is None")
                sub_group = current.sub_group

            stmt = (
                update(Lesson)
                .where(Lesson.id == value)
                .values(
                    kind_of_work_id=kind_of_work_id,
                    discipline_id=discipline_id,
                    auditorium_id=auditorium_id,
                    lecturer_id=lecturer_id,
                    date=date,
                    begin_lesson=begin_lesson,
                    end_lesson=end_lesson,
                    sub_group=sub_group,
                    updated_at=datetime.datetime.now(datetime.timezone.utc),
                )
            )
            result = self.session.exec(stmt)
            self.session.commit()
            logger.debug(f"Updated Lesson {value}")
            return result.rowcount > 0
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Lesson update failed: \n{e}")
            return False

    def UpdateUpdatedAt(self, value: int) -> bool:
        """Updates the updated_at timestamp for a lesson by ID.

        Args:
            value (int): ID of the lesson to update.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        logger.info(f"Updating updated_at for Lesson {value}")

        try:
            stmt = (
                update(Lesson)
                .where(Lesson.id == value)
                .values(updated_at=datetime.datetime.now(datetime.timezone.utc))
            )
            result = self.session.exec(stmt)
            self.session.commit()
            logger.debug(f"Updated updated_at for Lesson {value}")
            return result.rowcount > 0
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to update updated_at for Lesson {value}: \n{e}")
            return False

    def Delete(self, value: int) -> bool:
        """Deletes a lesson by ID.

        Args:
            value (int): ID of the lesson to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        logger.info(f"Deleting Lesson {value}")

        try:
            stmt = delete(Lesson).where(Lesson.id == value)
            result = self.session.exec(stmt)
            self.session.commit()
            logger.debug(f"Deleted Lesson {value}")
            return result.rowcount > 0
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to delete Lesson {value}: \n{e}")
            return False

    def DeleteAll(self) -> bool:
        """Deletes all lessons from the database.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        logger.info("Deleting all Lessons")

        try:
            stmt = delete(Lesson)
            result = self.session.exec(stmt)
            self.session.commit()
            logger.debug("Deleted all Lessons")
            return result.rowcount > 0
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to delete all Lessons: \n{e}")
            return False
