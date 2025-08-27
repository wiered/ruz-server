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
        existing = self.GetById(discipline.id)
        if existing:
            return existing
        return self.Create(discipline)

    def ListAll(self):
        stmt = select(Discipline)
        return self.session.exec(stmt).all()

    def GetById(self, value: int):
        stmt = select(Discipline).where(Discipline.id == value)
        return self.session.exec(stmt).first()

    def GetByName(self, value: str):
        stmt = select(Discipline).where(Discipline.name == value)
        return self.session.exec(stmt).first()

    def GetByExamType(self, value: str):
        stmt = select(Discipline).where(Discipline.examtype == value)
        return self.session.exec(stmt).all()

    def Update(self, value: int, name: str, examtype: str, has_labs: bool):
        try:
            stmt = update(Discipline).where(Discipline.id == value).values(name=name, examtype=examtype, has_labs=has_labs)
            result = self.session.exec(stmt)
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            return False

    def Delete(self, value: int):
        try:
            stmt = delete(Discipline).where(Discipline.id == value)
            result = self.session.exec(stmt)
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            return False
