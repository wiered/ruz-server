from typing import List, Optional, Dict, Any

from sqlmodel import Session, select, delete, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import UUID

from models import Group

class GroupRepository:
    def __init__(self, session: Session):
        self.session = session

    def CreateGroup(
        self,
        id: int,
        guid: UUID,
        name: str,
        faculty_name: str
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
        group = Group(id=id, guid=guid, name=name, faculty_name=faculty_name)
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
        existing = self.GetById(group.id)
        if existing:
            return existing
        return self.CreateUser(group)

    def ListAll(self) -> List[Group]:
        """Returns all groups in the database.

        Returns:
            List[Group]: A list of all groups in the database.
        """
        stmt = select(Group)
        return self.session.exec(stmt).all()

    def GetById(self, value: int) -> Optional[Group]:
        """Gets a group by ID.

        Args:
            value (int): The ID of the group to get.

        Returns:
            Optional[Group]: The group with the given ID, or None if no such group exists.
        """
        stmt = select(Group).where(Group.id == value)
        return self.session.exec(stmt).first()

    def GetByGUID(self, value: UUID) -> Optional[Group]:
        """Gets a group by GUID.

        Args:
            value (UUID): The GUID of the group to get.

        Returns:
            Optional[Group]: The group with the given GUID, or None if no such group exists.
        """
        stmt = select(Group).where(Group.guid == value)
        return self.session.exec(stmt).first()

    def GetByName(self, value: str) -> List[Group]:
        """Gets all groups with the given name.

        Args:
            value (str): The name of the groups to get.

        Returns:
            List[Group]: A list of all groups with the given name.
        """

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
        try:
            stmt = update(Group).where(Group.id == value).values(name=name, faculty_name=faculty_name)
            result = self.session.exec(stmt)
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            return False

    def Delete(self, value: int) -> bool:
        """Deletes a group by ID.

        Args:
            value (int): The ID of the group to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        try:
            stmt = delete(Group).where(Group.id == value)
            result = self.session.exec(stmt)
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            return False
