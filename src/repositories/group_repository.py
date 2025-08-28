import logging
from typing import List, Optional, Dict, Any

from sqlmodel import Session, select, delete, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import UUID

from models import Group

logger = logging.getLogger(__name__)

class GroupRepository:
    def __init__(self, session: Session):
        self.session = session

    def Create(
        self,
        group: Group
    ) -> Group:
        """
        Creates a new group.

        Args:
            id (int): The ID of the group to create.
            guid (UUID): The GUID of the group to create.
            name (str): The name of the group to create.
            faculty_name (str): The name of the faculty of the group to create.

        Returns:
            Group: The created group.
        """
        logger.info(f"Creating Group {group.name}")

        self.session.add(group)
        self.session.commit()
        self.session.refresh(group)
        return group

    def GetOrCreate(self, group: Group) -> Group:
        """
        Gets a group by ID, or creates a new one if it doesn't exist.

        Args:
            group (Group): The group to get or create.

        Returns:
            Group: The existing or newly-created group.
        """
        logger.info(f"Getting or creating Group {group.name}")

        existing = self.GetById(group.id)
        if existing:
            logger.debug(f"Group {group.name} already exists")
            return existing

        logger.debug(f"Group {group.name} does not exist, creating")
        return self.Create(group)

    def ListAll(self) -> List[Group]:
        """Returns all groups in the database.

        Returns:
            List[Group]: A list of all groups in the database.
        """
        logger.info("Listing all groups")

        stmt = select(Group)
        return self.session.exec(stmt).all()

    def GetById(self, value: int) -> Optional[Group]:
        """Gets a group by ID.

        Args:
            value (int): The ID of the group to get.

        Returns:
            Optional[Group]: The group with the given ID, or None if no such group exists.
        """
        logger.info(f"Getting Group {value}")

        stmt = select(Group).where(Group.id == value)
        return self.session.exec(stmt).first()

    def GetByGUID(self, value: UUID) -> Optional[Group]:
        """Gets a group by GUID.

        Args:
            value (UUID): The GUID of the group to get.

        Returns:
            Optional[Group]: The group with the given GUID, or None if no such group exists.
        """
        logger.info(f"Getting Group {value}")

        stmt = select(Group).where(Group.guid == value)
        return self.session.exec(stmt).first()

    def GetByName(self, value: str) -> List[Group]:
        """Gets all groups with the given name.

        Args:
            value (str): The name of the groups to get.

        Returns:
            List[Group]: A list of all groups with the given name.
        """
        logger.info(f"Getting Group {value}")

        stmt = select(Group).where(Group.name == value)
        return self.session.exec(stmt).all()

    def Update(self, value: int, name: str, faculty_name: str) -> bool:
        """Updates a group by ID.

        Args:
            value (int): The ID of the group to update.
            name (str): The new name of the group.
            faculty_name (str): The new name of the faculty of the group.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        logger.info(f"Updating Group {value}")

        try:
            current = self.GetById(value)

            if current is None:
                logger.error(f"Group {value} does not exist")
                return False

            if name is None:
                logger.debug(f"Payload does not have a name")
                name = current.name
            if faculty_name is None:
                logger.debug(f"Payload does not have a faculty name")
                faculty_name = current.faculty_name

            stmt = (
                update(Group)
                .where(Group.id == value)
                .values(name=name, faculty_name=faculty_name)
                )
            result = self.session.exec(stmt)
            self.session.commit()
            logger.debug(f"Group {value} updated")
            return result.rowcount > 0
        except SQLAlchemyError as e:
            logger.error(f"Group {value} update failed: \n{e}")
            self.session.rollback()
            return False

    def Delete(self, value: int) -> bool:
        """Deletes a group by ID.

        Args:
            value (int): The ID of the group to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        logger.info(f"Deleting Group {value}")

        try:
            stmt = delete(Group).where(Group.id == value)
            result = self.session.exec(stmt)
            self.session.commit()
            logger.debug(f"Group {value} deleted")
            return result.rowcount > 0
        except SQLAlchemyError as e:
            logger.error(f"Group {value} delete failed: \n{e}")
            self.session.rollback()
            return False
