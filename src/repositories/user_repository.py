import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import UUID, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, delete, select, update

from src.models import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def Create(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        return user

    def GetOrCreate(self, user: User) -> User:
        existing = self.GetUserById(user.id)
        if existing:
            return existing
        return self.CreateUser(user)

    def ListAll(self) -> List[User]:
        stmt = select(User)
        return self.session.exec(stmt).all()

    def ListByGroupOid(self, value: int) -> List[User]:
        stmt = select(User).where(User.group_oid == value)
        return self.session.exec(stmt).all()

    def GetById(self, value: int) -> Optional[User]:
        stmt = select(User).where(User.id == value)
        return self.session.exec(stmt).first()

    def GetByUsername(self, value: str) -> Optional[User]:
        stmt = select(User).where(User.username == value)
        return self.session.exec(stmt).first()

    def GetWithGroup(self, value: int) -> Optional[User]:
        stmt = select(User).where(User.id == value).options(selectinload(User.group))
        return self.session.exec(stmt).first()

    def Update(
        self,
        value: int,
        username: str = None,
        group_oid: int = None,
        subgroup: int = None,
        ) -> bool:
        try:
            user = self.GetUserById(value)

            if username is None:
                username = user.username
            if group_oid is None:
                group_oid = user.group_oid
            if subgroup is None:
                subgroup = user.subgroup

            stmt = update(User).where(User.id == value).values(username=username, group_oid=group_oid, subgroup=subgroup)
            result = self.session.exec(stmt)
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            return False

    def UpdateLastUsedAt(self, value: int) -> bool:
        try:
            stmt = (
                update(User)
                .where(User.id == value)
                .values(last_used_at=datetime.datetime.now(datetime.timezone.utc)))
            result = self.session.exec(stmt)
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            return False

    def Delete(self, value: int) -> bool:
        try:
            stmt = delete(User).where(User.id == value)
            result = self.session.exec(stmt)
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            return False
