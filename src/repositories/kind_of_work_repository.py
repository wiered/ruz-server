import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import UUID, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, delete, select, update

from models import KindOfWork


class KindOfWorkRepository:
    def __init__(self, session: Session):
        self.session = session

    def Create(self, kind_of_work: KindOfWork):
        """
        Creates a new KindOfWork.

        Args:
            kind_of_work (KindOfWork): Kind of work to be created.

        Returns:
            KindOfWork: Created KindOfWork.
        """
        self.session.add(kind_of_work)
        self.session.commit()
        return kind_of_work

    def GetOrCreate(self, kind_of_work: KindOfWork):
        """
        Creates a new KindOfWork if it doesn't exist, otherwise it retrieves the existing one.

        Args:
            kind_of_work (KindOfWork): Kind of work to be created or retrieved.

        Returns:
            KindOfWork: Created or retrieved KindOfWork.
        """
        existing = self.GetById(kind_of_work.id)
        if existing:
            return existing
        return self.Create(kind_of_work)

    def ListAll(self):
        """
        Gets all KindOfWork objects from the database.

        Returns:
            List[KindOfWork]: List of all KindOfWork objects.
        """
        stmt = select(KindOfWork)
        return self.session.exec(stmt).all()

    def GetById(self, value: int):
        """
        Gets a KindOfWork object from the database by its ID.

        Args:
            value (int): ID of the KindOfWork object to be retrieved.

        Returns:
            KindOfWork: Retrieved KindOfWork object or None if no such object exists.
        """
        stmt = select(KindOfWork).where(KindOfWork.id == value)
        return self.session.exec(stmt).first()

    def Update(self, value: int, type_of_work: str, complexity: int):
        """
        Updates a KindOfWork object in the database.

        Args:
            value (int): ID of the KindOfWork object to be updated.
            type_of_work (str): New type of work.
            complexity (int): New complexity.

        Returns:
            bool: True if the update was successful, False otherwise.
        """

        try:
            stmt = update(KindOfWork).where(KindOfWork.id == value).values(
                type_of_work=type_of_work, complexity=complexity
            )
            result = self.session.exec(stmt)
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            return False

    def Delete(self, value: int) -> bool:
        """
        Deletes a KindOfWork object from the database by its ID.

        Args:
            value (int): ID of the KindOfWork object to be deleted.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """

        try:
            stmt = delete(KindOfWork).where(KindOfWork.id == value)
            result = self.session.exec(stmt)
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            return False
