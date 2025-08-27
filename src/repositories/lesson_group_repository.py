from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, delete, select

from src.models import LessonGroup


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
        existing = self.GetByIds(lesson_group.lesson_id, lesson_group.group_id)
        if existing:
            return existing
        return self.Create(lesson_group)

    def ListAll(self) -> List[LessonGroup]:
        """Returns a list of all LessonGroup associations.

        Returns:
            List[LessonGroup]: List of associations.
        """
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
        stmt = select(LessonGroup).where(LessonGroup.lesson_id == lesson_id)
        return self.session.exec(stmt).all()

    def ListByGroupId(self, group_id: int) -> List[LessonGroup]:
        """Returns associations filtered by group ID.

        Args:
            group_id (int): Group ID.

        Returns:
            List[LessonGroup]: List of associations.
        """
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
        stmt = (
            select(LessonGroup)
            .where(LessonGroup.group_id == group_id)
            .options(selectinload(LessonGroup.lesson))
        )
        return self.session.exec(stmt).all()

    def Delete(self, lesson_id: int, group_id: int) -> bool:
        """Deletes an association by composite key.

        Args:
            lesson_id (int): Lesson ID.
            group_id (int): Group ID.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            stmt = delete(LessonGroup).where(
                LessonGroup.lesson_id == lesson_id,
                LessonGroup.group_id == group_id,
            )
            result = self.session.exec(stmt)
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            return False

    def DeleteByLessonId(self, lesson_id: int) -> bool:
        """Deletes all associations for a given lesson ID.

        Args:
            lesson_id (int): Lesson ID.

        Returns:
            bool: True if any rows were deleted, False otherwise.
        """
        try:
            stmt = delete(LessonGroup).where(LessonGroup.lesson_id == lesson_id)
            result = self.session.exec(stmt)
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            return False

    def DeleteByGroupId(self, group_id: int) -> bool:
        """Deletes all associations for a given group ID.

        Args:
            group_id (int): Group ID.

        Returns:
            bool: True if any rows were deleted, False otherwise.
        """
        try:
            stmt = delete(LessonGroup).where(LessonGroup.group_id == group_id)
            result = self.session.exec(stmt)
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            return False
