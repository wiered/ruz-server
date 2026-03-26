import logging
import datetime
from typing import Iterable, List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, delete, select

from ruz_server.models import Lesson, LessonGroup

logger = logging.getLogger(__name__)


class LessonGroupRepository:
    def __init__(self, session: Session):
        self.session = session

    def Create(self, lesson_group: LessonGroup) -> LessonGroup:
        """Creates a new LessonGroup association.

        Args:
            lesson_group (LessonGroup): Association to create.

        Returns:
            LessonGroup: Created association.
        """
        logger.info(f"Creating LessonGroup {lesson_group}")

        self.session.add(lesson_group)
        self.session.commit()
        return lesson_group

    def GetOrCreate(self, lesson_group: LessonGroup) -> LessonGroup:
        """Gets an existing association or creates a new one.

        Args:
            lesson_group (LessonGroup): Association to get or create.

        Returns:
            LessonGroup: Existing or newly created association.
        """
        logger.info(f"Getting or creating LessonGroup {lesson_group}")

        existing = self.GetByIds(lesson_group.lesson_id, lesson_group.group_id)
        if existing:
            logger.debug(f"LessonGroup {lesson_group} already exists")
            return existing

        logger.debug(f"LessonGroup {lesson_group} does not exist, creating")
        return self.Create(lesson_group)

    def ListAll(self) -> List[LessonGroup]:
        """Returns a list of all LessonGroup associations.

        Returns:
            List[LessonGroup]: List of associations.
        """
        logger.info("Listing all LessonGroup associations")

        stmt = select(LessonGroup)
        return self.session.exec(stmt).all()

    def GetByIds(self, lesson_id: int, group_id: int) -> Optional[LessonGroup]:
        """Returns an association by composite key.

        Args:
            lesson_id (int): Lesson ID.
            group_id (int): Group ID.

        Returns:
            Optional[LessonGroup]: Association if found, otherwise None.
        """
        logger.info(f"Getting LessonGroup by IDs {lesson_id} and {group_id}")

        stmt = select(LessonGroup).where(
            LessonGroup.lesson_id == lesson_id,
            LessonGroup.group_id == group_id,
        )
        return self.session.exec(stmt).first()

    def ListByLessonId(self, lesson_id: int) -> List[LessonGroup]:
        """Returns associations filtered by lesson ID.

        Args:
            lesson_id (int): Lesson ID.

        Returns:
            List[LessonGroup]: List of associations.
        """
        logger.info(f"Listing LessonGroup associations by lesson ID {lesson_id}")

        stmt = select(LessonGroup).where(LessonGroup.lesson_id == lesson_id)
        return self.session.exec(stmt).all()

    def ListByGroupId(self, group_id: int) -> List[LessonGroup]:
        """Returns associations filtered by group ID.

        Args:
            group_id (int): Group ID.

        Returns:
            List[LessonGroup]: List of associations.
        """
        logger.info(f"Listing LessonGroup associations by group ID {group_id}")

        stmt = select(LessonGroup).where(LessonGroup.group_id == group_id)
        return self.session.exec(stmt).all()

    def GetWithLessonAndGroup(self, lesson_id: int, group_id: int) -> Optional[LessonGroup]:
        """Returns an association with related Lesson and Group eagerly loaded.

        Args:
            lesson_id (int): Lesson ID.
            group_id (int): Group ID.

        Returns:
            Optional[LessonGroup]: Association with relationships loaded.
        """
        logger.info(f"Getting LessonGroup by IDs {lesson_id} and {group_id}")

        stmt = (
            select(LessonGroup)
            .where(
                LessonGroup.lesson_id == lesson_id,
                LessonGroup.group_id == group_id,
            )
            .options(
                selectinload(LessonGroup.lesson),
                selectinload(LessonGroup.group),
            )
        )
        return self.session.exec(stmt).first()

    def ListByLessonIdWithGroup(self, lesson_id: int) -> List[LessonGroup]:
        """Returns associations by lesson ID with Group eagerly loaded.

        Args:
            lesson_id (int): Lesson ID.

        Returns:
            List[LessonGroup]: List of associations with Group loaded.
        """
        logger.info(f"Listing LessonGroup associations by lesson ID {lesson_id}")

        stmt = (
            select(LessonGroup)
            .where(LessonGroup.lesson_id == lesson_id)
            .options(selectinload(LessonGroup.group))
        )
        return self.session.exec(stmt).all()

    def ListByGroupIdWithLesson(self, group_id: int) -> List[LessonGroup]:
        """Returns associations by group ID with Lesson eagerly loaded.

        Args:
            group_id (int): Group ID.

        Returns:
            List[LessonGroup]: List of associations with Lesson loaded.
        """
        logger.info(f"Listing LessonGroup associations by group ID {group_id}")

        stmt = (
            select(LessonGroup)
            .where(LessonGroup.group_id == group_id)
            .options(selectinload(LessonGroup.lesson))
        )
        return self.session.exec(stmt).all()

    def BulkGetOrCreate(self, lesson_groups: Iterable[LessonGroup]) -> int:
        """Create missing lesson-group links without committing.

        Returns:
            int: number of newly created links
        """
        created_count = 0
        for link in lesson_groups:
            existing = self.GetByIds(link.lesson_id, link.group_id)
            if existing is None:
                self.session.add(link)
                created_count += 1
        return created_count

    def ListPairsInDateRange(self, start: datetime.date, end: datetime.date) -> List[tuple[int, int]]:
        """List (lesson_id, group_id) pairs linked to lessons in date range."""
        stmt = (
            select(LessonGroup.lesson_id, LessonGroup.group_id)
            .join(Lesson, Lesson.id == LessonGroup.lesson_id)
            .where(Lesson.date >= start, Lesson.date <= end)
        )
        return list(self.session.exec(stmt).all())

    def DeleteMissingPairsInDateRange(
        self,
        incoming_pairs: set[tuple[int, int]],
        start,
        end,
    ) -> int:
        """Delete lesson-group pairs in date range missing from incoming snapshot.

        Returns:
            int: number of deleted rows
        """
        existing_pairs = set(self.ListPairsInDateRange(start, end))
        stale_pairs = existing_pairs - incoming_pairs
        if not stale_pairs:
            return 0

        deleted = 0
        for lesson_id, group_id in stale_pairs:
            stmt = delete(LessonGroup).where(
                LessonGroup.lesson_id == lesson_id,
                LessonGroup.group_id == group_id,
            )
            result = self.session.exec(stmt)
            deleted += int(result.rowcount or 0)
        return deleted

    def Delete(self, lesson_id: int, group_id: int) -> bool:
        """Deletes an association by composite key.

        Args:
            lesson_id (int): Lesson ID.
            group_id (int): Group ID.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        logger.info(f"Deleting LessonGroup by IDs {lesson_id} and {group_id}")

        try:
            stmt = delete(LessonGroup).where(
                LessonGroup.lesson_id == lesson_id,
                LessonGroup.group_id == group_id,
            )
            result = self.session.exec(stmt)
            self.session.commit()
            logger.debug(f"Deleted LessonGroup by IDs {lesson_id} and {group_id}")
            return result.rowcount > 0
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to delete LessonGroup by IDs {lesson_id} and {group_id}: \n{e}")
            return False

    def DeleteByLessonId(self, lesson_id: int) -> bool:
        """Deletes all associations for a given lesson ID.

        Args:
            lesson_id (int): Lesson ID.

        Returns:
            bool: True if any rows were deleted, False otherwise.
        """
        logger.info(f"Deleting LessonGroup by lesson ID {lesson_id}")
        try:
            stmt = delete(LessonGroup).where(LessonGroup.lesson_id == lesson_id)
            result = self.session.exec(stmt)
            self.session.commit()
            logger.debug(f"Deleted LessonGroup by lesson ID {lesson_id}")
            return result.rowcount > 0
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to delete LessonGroup by lesson ID {lesson_id}: \n{e}")
            return False

    def DeleteByGroupId(self, group_id: int) -> bool:
        """Deletes all associations for a given group ID.

        Args:
            group_id (int): Group ID.

        Returns:
            bool: True if any rows were deleted, False otherwise.
        """
        logger.info(f"Deleting LessonGroup by group ID {group_id}")
        try:
            stmt = delete(LessonGroup).where(LessonGroup.group_id == group_id)
            result = self.session.exec(stmt)
            self.session.commit()
            logger.debug(f"Deleted LessonGroup by group ID {group_id}")
            return result.rowcount > 0
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to delete LessonGroup by group ID {group_id}: \n{e}")
            return False
