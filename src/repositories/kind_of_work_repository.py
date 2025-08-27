import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import UUID, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, delete, select, update

from src.models import KindOfWork


class KindOfWorkRepository:
    def __init__(self, session: Session):
        self.session = session

    def Create(self, kind_of_work: KindOfWork):
        self.session.add(kind_of_work)
        self.session.commit()
        return kind_of_work

    def GetOrCreate(self, kind_of_work: KindOfWork):
        existing = self.GetById(kind_of_work.id)
        if existing:
            return existing
        return self.Create(kind_of_work)

    def ListAll(self):
        stmt = select(KindOfWork)
        return self.session.exec(stmt).all()

    def GetById(self, value: int):
        stmt = select(KindOfWork).where(KindOfWork.id == value)
        return self.session.exec(stmt).first()

    def Update(self, value: int, type_of_work: str, complexity: int):
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
        try:
            stmt = delete(KindOfWork).where(KindOfWork.id == value)
            result = self.session.exec(stmt)
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            return False
