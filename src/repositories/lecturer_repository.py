import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import UUID, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, delete, select, update

from src.models import Lecturer

class LecturerRepository:
    def __init__(self, session: Session):
        self.session = session

    def CreateLecturer(self, lecturer: Lecturer) -> Lecturer:

        self.session.add(Lecturer)
        self.session.commit()
        return lecturer

    def GetOrCreate(self, lecturer: Lecturer) -> Lecturer:
        existing = self.GetUserById(lecturer.id)
        if existing:
            return existing
        return self.CreateUser(lecturer)

    def listAll(self) -> List[Lecturer]:
        stmt = select(Lecturer)
        return self.session.exec(stmt).all()

    def getById(self, value: int) -> Optional[Lecturer]:
        stmt = select(Lecturer).where(Lecturer.id == value)
        return self.session.exec(stmt).first()

    def getByGUID(self, value: UUID) -> Optional[Lecturer]:
        stmt = select(Lecturer).where(Lecturer.guid == value)
        return self.session.exec(stmt).first()

    def getWithLessons(self, value: int) -> Optional[Lecturer]:
        stmt = select(Lecturer).where(Lecturer.id == value).options(selectinload(Lecturer.lessons))
        return self.session.exec(stmt).first()

    def Update(
        self,
        value: int,
        full_name: str = None,
        short_name: str = None,
        rank: str = None
    ) -> bool:
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
        try:
            stmt = delete(Lecturer).where(Lecturer.id == value)
            result = self.session.exec(stmt)
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            return False
