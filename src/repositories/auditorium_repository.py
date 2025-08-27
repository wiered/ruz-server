import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import UUID, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, delete, select, update

from models import Auditorium

class AuditoriumRepository:
    def __init__(self, session: Session):
        self.session = session

    def Create(self, auditorium: Auditorium):
        """
        Creates a new Auditorium in the database.

        Args:
            auditorium (Auditorium): The Auditorium to be created.

        Returns:
            Auditorium: The created Auditorium.
        """
        self.session.add(auditorium)
        self.session.commit()
        return auditorium

    def GetOrCreate(self, auditorium: Auditorium):
        """
        Gets a Auditorium by ID, or creates a new one if it doesn't exist.

        Args:
            auditorium (Auditorium): The Auditorium to get or create.

        Returns:
            Auditorium: The existing or newly-created Auditorium.
        """

        existing = self.GetById(auditorium.id)
        if existing:
            return existing
        return self.Create(auditorium)

    def ListAll(self):
        """
        Gets all Auditorium objects from the database.

        Returns:
            List[Auditorium]: List of all Auditorium objects.
        """

        stmt = select(Auditorium)
        return self.session.exec(stmt).all()

    def GetById(self, value: int):
        """
        Gets a Auditorium by ID.

        Args:
            value (int): The ID of the Auditorium to get.

        Returns:
            Optional[Auditorium]: The Auditorium with the given ID, or None if no such Auditorium exists.
        """
        stmt = select(Auditorium).where(Auditorium.id == value)
        return self.session.exec(stmt).first()

    def GetByGuid(self, value: UUID):
        """
        Gets a Auditorium by GUID.

        Args:
            value (UUID): The GUID of the Auditorium to get.

        Returns:
            Optional[Auditorium]: The Auditorium with the given GUID, or None if no such Auditorium exists.
        """
        stmt = select(Auditorium).where(Auditorium.guid == value)
        return self.session.exec(stmt).first()

    def GetByName(self, value: str):
        """
        Gets a Auditorium by name.

        Args:
            value (str): The name of the Auditorium to get.

        Returns:
            Optional[Auditorium]: The Auditorium with the given name, or None if no such Auditorium exists.
        """
        stmt = select(Auditorium).where(Auditorium.name == value)
        return self.session.exec(stmt).first()

    def Update(
        self,
        value: int,
        name: Optional[str],
        building: Optional[str]
    ) -> bool:
        """
        Updates a Auditorium by ID.

        Args:
            value (int): The ID of the Auditorium to update.
            name (Optional[str], optional): New name of the Auditorium. Defaults to the current name if not provided.
            building (Optional[str], optional): New name of the building of the Auditorium. Defaults to the current building if not provided.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        try:
            current = self.GetById(value)

            if current is None:
                return False

            if name is None:
                name = current.name
            if building is None:
                building = current.building

            stmt = (
                update(Auditorium)
                .where(Auditorium.id == value)
                .values(name=name, building=building)
            )
            result = self.session.exec(stmt)
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            return False

    def Delete(self, value: int):
        """
        Deletes a Auditorium by ID.

        Args:
            value (int): The ID of the Auditorium to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """

        try:
            stmt = delete(Auditorium).where(Auditorium.id == value)
            result = self.session.exec(stmt)
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            return False
