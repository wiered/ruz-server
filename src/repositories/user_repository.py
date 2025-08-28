import datetime
from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, delete, select, update

from models import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def Create(self, user: User) -> User:
        """Создает нового пользователя

        Args:
            user (User): создаваемый пользователь

        Returns:
            User: созданный пользователь
        """
        self.session.add(user)
        self.session.commit()
        return user

    def GetOrCreate(self, user: User) -> User:
        """Получает пользователя или создает его

        Args:
            user (User): пользователь

        Returns:
            User: созданный или полученный пользователь
        """
        existing = self.GetById(user.id)
        if existing:
            return existing
        return self.Create(user)

    def ListAll(self) -> List[User]:
        """Возвращает список всех пользователей

        Returns:
            List[User]: список пользователей
        """
        stmt = select(User)
        return self.session.exec(stmt).all()

    def ListByGroupOid(self, value: int) -> List[User]:
        """Возвращает список пользователей по ID группы

        Args:
            value (int): ID группы

        Returns:
            List[User]: список пользователей
        """
        stmt = select(User).where(User.group_oid == value)
        return self.session.exec(stmt).all()

    def GetById(self, value: int) -> Optional[User]:
        """Возвращает пользователя по ID

        Args:
            value (int): ID пользователя

        Returns:
            Optional[User]: пользователь
        """
        stmt = select(User).where(User.id == value)
        return self.session.exec(stmt).first()

    def GetByUsername(self, value: str) -> Optional[User]:
        """Возвращает пользователя по тегу телеграм

        Args:
            value (str): тег телеграм

        Returns:
            Optional[User]: пользователь
        """
        stmt = select(User).where(User.username == value)
        return self.session.exec(stmt).first()

    def GetWithGroup(self, value: int) -> Optional[User]:
        """Возвращает пользователя и его группу по ID

        Args:
            value (int): ID пользователя

        Returns:
            Optional[User]: пользователь
        """
        stmt = select(User).where(User.id == value).options(selectinload(User.group))
        return self.session.exec(stmt).first()

    def Update(
        self,
        value: int,
        username: str = None,
        group_oid: int = None,
        subgroup: int = None,
        ) -> bool:
        """Updates a user's details by ID.

        Args:
            value (int): ID of the user to be updated.
            username (str, optional): New username for the user. Defaults to the current username if not provided.
            group_oid (int, optional): New group ID for the user. Defaults to the current group ID if not provided.
            subgroup (int, optional): New subgroup for the user. Defaults to the current subgroup if not provided.

        Returns:
            bool: True if the update was successful, False otherwise.
        """

        try:
            current = self.GetById(value)

            if username is None:
                username = current.username
            if group_oid is None:
                group_oid = current.group_oid
            if subgroup is None:
                subgroup = current.subgroup

            stmt = update(User).where(User.id == value).values(username=username, group_oid=group_oid, subgroup=subgroup)
            result = self.session.exec(stmt)
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            return False

    def UpdateLastUsedAt(self, value: int) -> bool:
        """Updates the last used at time for a user by ID.

        Args:
            value (int): ID of the user to be updated.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
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
        """Deletes a user by ID.

        Args:
            value (int): ID of the user to be deleted.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        try:
            stmt = delete(User).where(User.id == value)
            result = self.session.exec(stmt)
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            return False
