import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import UUID, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, delete, select, update

from src.models import Discipline

class DisciplineRepository:
    def __init__(self, session: Session):
        self.session = session

    def Create(self, discipline: Discipline):
        """Adds a new discipline to the database.

        Args:
            discipline (Discipline): The discipline to add.

        Returns:
            Discipline: The added discipline.
        """
        self.session.add(discipline)
        self.session.commit()
        return discipline

    def GetOrCreate(self, discipline: Discipline):
        """Gets a discipline by ID, or creates a new one if it doesn't exist.

        Args:
            discipline (Discipline): The discipline to get or create.

        Returns:
            Discipline: The existing or newly-created discipline.
        """
        existing = self.GetById(discipline.id)
        if existing:
            return existing
        return self.Create(discipline)

    def ListAll(self):
        """Returns a list of all disciplines.

        Returns:
            List[Discipline]: A list of all disciplines in the database.
        """
        stmt = select(Discipline)
        return self.session.exec(stmt).all()

    def GetById(self, value: int):
        """Gets a discipline by ID.

        Args:
            value (int): The ID of the discipline to get.

        Returns:
            Optional[Discipline]: The discipline with the given ID, or None if no such discipline exists.
        """
        stmt = select(Discipline).where(Discipline.id == value)
        return self.session.exec(stmt).first()

    def GetByName(self, value: str):
        """Gets a discipline by name.

        Args:
            value (str): The name of the discipline to get.

        Returns:
            Optional[Discipline]: The discipline with the given name, or None if no such discipline exists.
        """
        stmt = select(Discipline).where(Discipline.name == value)
        return self.session.exec(stmt).first()

    def GetByExamType(self, value: str):
        """Gets all disciplines with the given exam type.

        Args:
            value (str): The exam type to search for.

        Returns:
            List[Discipline]: A list of all disciplines with the given exam type.
        """
        stmt = select(Discipline).where(Discipline.examtype == value)
        return self.session.exec(stmt).all()

    def Update(self, value: int, name: str, examtype: str, has_labs: bool):
        """Updates a discipline by ID.

        Args:
            value (int): The ID of the discipline to update.
            name (str): The new name of the discipline.
            examtype (str): The new exam type of the discipline.
            has_labs (bool): Whether the discipline has labs.

        Returns:
            bool: True if the update was successful, False otherwise.
        """

        try:
            stmt = update(Discipline).where(Discipline.id == value).values(name=name, examtype=examtype, has_labs=has_labs)
            result = self.session.exec(stmt)
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            return False

    def Delete(self, value: int):
        """Deletes a discipline by ID.

        Args:
            value (int): The ID of the discipline to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        try:
            stmt = delete(Discipline).where(Discipline.id == value)
            result = self.session.exec(stmt)
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            return False
