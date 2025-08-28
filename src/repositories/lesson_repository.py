import datetime
import logging
from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, delete, select, update

from models import Lesson

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
        try:
            stmt = (
                update(Lesson)
                .where(Lesson.id == value)
                .values(updated_at=datetime.datetime.now(datetime.timezone.utc))
            )
            result = self.session.exec(stmt)
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            return False

    def Delete(self, value: int) -> bool:
        """Deletes a lesson by ID.

        Args:
            value (int): ID of the lesson to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        try:
            stmt = delete(Lesson).where(Lesson.id == value)
            result = self.session.exec(stmt)
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            return False
