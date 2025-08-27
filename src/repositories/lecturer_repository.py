import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import UUID, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, delete, select, update

from models import Lecturer

class LecturerRepository:
    def __init__(self, session: Session):
        self.session = session

    def CreateLecturer(self, lecturer: Lecturer) -> Lecturer:
        """
        Creates a new Lecturer object in the database.

        Args:
            lecturer (Lecturer): The Lecturer object to be created.

        Returns:
            Lecturer: The created Lecturer object.
        """
        self.session.add(Lecturer)
        self.session.commit()
        return lecturer

    def GetOrCreate(self, lecturer: Lecturer) -> Lecturer:
        """
        Gets a Lecturer by ID, or creates a new one if it doesn't exist.

        Args:
            lecturer (Lecturer): The Lecturer to get or create.

        Returns:
            Lecturer: The existing or newly-created Lecturer.
        """
        existing = self.GetUserById(lecturer.id)
        if existing:
            return existing
        return self.CreateUser(lecturer)

    def listAll(self) -> List[Lecturer]:
        """
        Returns a list of all Lecturer objects in the database.

        Returns:
            List[Lecturer]: A list of all Lecturer objects in the database.
        """
        stmt = select(Lecturer)
        return self.session.exec(stmt).all()

    def getById(self, value: int) -> Optional[Lecturer]:
        """
        Gets a Lecturer by ID.

        Args:
            value (int): The ID of the Lecturer to get.

        Returns:
            Optional[Lecturer]: The Lecturer with the given ID, or None if no such Lecturer exists.
        """
        stmt = select(Lecturer).where(Lecturer.id == value)
        return self.session.exec(stmt).first()

    def getByGUID(self, value: UUID) -> Optional[Lecturer]:
        """
        Gets a Lecturer by GUID.

        Args:
            value (UUID): The GUID of the Lecturer to get.

        Returns:
            Optional[Lecturer]: The Lecturer with the given GUID, or None if no such Lecturer exists.
        """
        stmt = select(Lecturer).where(Lecturer.guid == value)
        return self.session.exec(stmt).first()

    def getWithLessons(self, value: int) -> Optional[Lecturer]:
        """
        Gets a Lecturer by ID, with all its lessons.

        Args:
            value (int): The ID of the Lecturer to get.

        Returns:
            Optional[Lecturer]: The Lecturer with the given ID, or None if no such Lecturer exists.
        """
        stmt = select(Lecturer).where(Lecturer.id == value).options(selectinload(Lecturer.lessons))
        return self.session.exec(stmt).first()

    def Update(
        self,
        value: int,
        full_name: str = None,
        short_name: str = None,
        rank: str = None
    ) -> bool:
        """
        Updates a Lecturer by ID.

        Args:
            value (int): The ID of the Lecturer to update.
            full_name (str, optional): The new full name of the Lecturer. Defaults to the current full name if not provided.
            short_name (str, optional): The new short name of the Lecturer. Defaults to the current short name if not provided.
            rank (str, optional): The new rank of the Lecturer. Defaults to the current rank if not provided.

        Returns:
            bool: True if the update was successful, False otherwise.
        """

        try:
            lecturer = self.GetUserById(value)

            if full_name is None:
                full_name = lecturer.full_name
            if short_name is None:
                short_name = lecturer.short_name
            if rank is None:
                rank = lecturer.rank

            stmt = (
                update(Lecturer).
                where(Lecturer.id == value).
                values(full_name=full_name, short_name=short_name, rank=rank)
            )
            result = self.session.exec(stmt)
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            return False

    def Delete(self, value: int) -> bool:
        """
        Deletes a Lecturer by ID.

        Args:
            value (int): The ID of the Lecturer to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """

        try:
            stmt = delete(Lecturer).where(Lecturer.id == value)
            result = self.session.exec(stmt)
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            return False
