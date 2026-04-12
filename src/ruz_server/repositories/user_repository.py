import datetime
import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, delete, select, update

from ruz_server.models import User

logger = logging.getLogger(__name__)
_UNSET = object()


class UserRepository:
    """
    UserRepository provides CRUD operations and data access logic for User objects.

    Args:
        session (Session): SQLModel database session used for queries.

    Returns:
        UserRepository: Instance for performing operations on User entities.
    """

    def __init__(self, session: Session):
        self.session = session

    def Create(self, user: User) -> User:
        """Создает нового пользователя

        Args:
            user (User): создаваемый пользователь

        Returns:
            User: созданный пользователь
        """
        if isinstance(user, dict):
            user = User(**user)

        if not isinstance(user, User):
            raise ValueError("User must be a User object")

        logger.info(f"Creating user {user}")

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
        logger.info(f"Getting or creating user {user}")

        if isinstance(user, dict):
            user = User(**user)

        if not isinstance(user, User):
            raise ValueError("User must be a User object")

        existing = self.GetById(user.id)
        if existing:
            logger.debug(f"User {user} already exists")
            return existing

        logger.debug(f"User {user} does not exist, creating")
        return self.Create(user)

    def ListAll(self) -> list[User]:
        """Возвращает список всех пользователей

        Returns:
            List[User]: список пользователей
        """
        logger.info("Listing all users")

        stmt = select(User)
        return self.session.exec(stmt).all()

    def ListByGroupOid(self, value: int) -> list[User]:
        """Возвращает список пользователей по ID группы

        Args:
            value (int): ID группы

        Returns:
            List[User]: список пользователей
        """
        if not isinstance(value, int):
            raise ValueError("GroupOid must be an integer")

        logger.info(f"Listing users by group {value}")

        stmt = select(User).where(User.group_oid == value)
        return self.session.exec(stmt).all()

    def GetById(self, value: int) -> User | None:
        """Возвращает пользователя по ID

        Args:
            value (int): ID пользователя

        Returns:
            Optional[User]: пользователь
        """
        logger.info(f"Getting user {value}")

        if not isinstance(value, int):
            raise ValueError("UserId must be an integer")

        stmt = select(User).where(User.id == value)
        return self.session.exec(stmt).first()

    def GetByUsername(self, value: str) -> User | None:
        """Возвращает пользователя по тегу телеграм

        Args:
            value (str): тег телеграм

        Returns:
            Optional[User]: пользователь
        """
        logger.info(f"Getting user {value}")

        if not isinstance(value, str):
            raise ValueError("Username must be a string")

        stmt = select(User).where(User.username == value)
        return self.session.exec(stmt).first()

    def GetWithGroup(self, value: int) -> User | None:
        """Возвращает пользователя и его группу по ID

        Args:
            value (int): ID пользователя

        Returns:
            Optional[User]: пользователь
        """
        logger.info(f"Getting user {value} with group")

        if not isinstance(value, int):
            raise ValueError("UserId must be an integer")

        stmt = select(User).where(User.id == value).options(selectinload(User.group))
        return self.session.exec(stmt).first()

    def Update(
        self,
        value: int,
        username: str | None | object = _UNSET,
        group_oid: int | None | object = _UNSET,
        subgroup: int | None | object = _UNSET,
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
        logger.info(f"Updating user {value}")

        if not isinstance(value, int):
            raise ValueError("UserId must be an integer")

        if (
            username is not _UNSET
            and username is not None
            and not isinstance(username, str)
        ):
            raise ValueError("Username must be a string")

        if (
            group_oid is not _UNSET
            and group_oid is not None
            and not isinstance(group_oid, int)
        ):
            raise ValueError("GroupOid must be an integer")

        if (
            subgroup is not _UNSET
            and subgroup is not None
            and not isinstance(subgroup, int)
        ):
            raise ValueError("Subgroup must be an integer")

        try:
            current = self.GetById(value)

            if current is None:
                logger.error(f"User {value} does not exist")
                return False

            if username is _UNSET:
                logger.debug("Payload does not have a username")
                username = current.username

            if group_oid is _UNSET:
                logger.debug("Payload does not have a group_oid")
                group_oid = current.group_oid

            if subgroup is _UNSET:
                logger.debug("Payload does not have a subgroup")
                subgroup = current.subgroup

            stmt = (
                update(User)
                .where(User.id == value)
                .values(username=username, group_oid=group_oid, subgroup=subgroup)
            )
            result = self.session.exec(stmt)
            self.session.commit()
            logger.debug(f"Updated user {value}")
            return result.rowcount > 0
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to update user {value}: \n{e}")
            return False

    def UpdateLastUsedAt(self, value: int) -> bool:
        """Updates the last used at time for a user by ID.

        Args:
            value (int): ID of the user to be updated.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        logger.info(f"Updating last used at for user {value}")

        if not isinstance(value, int):
            raise ValueError("UserId must be an integer")

        try:
            stmt = (
                update(User)
                .where(User.id == value)
                .values(last_used_at=datetime.datetime.now(datetime.UTC))
            )
            result = self.session.exec(stmt)
            self.session.commit()
            logger.debug(f"Updated last used at for user {value}")
            return result.rowcount > 0
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to update last used at for user {value}: \n{e}")
            return False

    def Delete(self, value: int) -> bool:
        """Deletes a user by ID.

        Args:
            value (int): ID of the user to be deleted.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        logger.info(f"Deleting user {value}")

        if not isinstance(value, int):
            raise ValueError("UserId must be an integer")

        try:
            stmt = delete(User).where(User.id == value)
            result = self.session.exec(stmt)
            self.session.commit()
            logger.debug(f"Deleted user {value}")
            return result.rowcount > 0
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to delete user {value}: \n{e}")
            return False
