from typing import List, Optional, Dict, Any

from sqlmodel import Session, select, delete, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import UUID

from src.models import Group

class GroupRepository:
    def __init__(self, session: Session):
        self.session = session

    def ListAllGroups(self) -> List[Group]:
        """Возвращает список всех групп

        Returns:
            List[Group]: Список групп
        """
        stmt = select(Group)
        return self.session.exec(stmt).all()

    def GetGroupById(self, value: int) -> Optional[Group]:
        """Возвращает группу по ID

        Args:
            value (int): ID группы

        Returns:
            Optional[Group]: Группа
        """
        stmt = select(Group).where(Group.id == value)
        return self.session.exec(stmt).first()

    def GetGroupByGUID(self, value: UUID) -> Optional[Group]:
        """Возвращает группу по GUID

        Args:
            value (UUID): GUID группы

        Returns:
            Optional[Group]: Группа
        """
        stmt = select(Group).where(Group.guid == value)
        return self.session.exec(stmt).first()

    def GetGroupByName(self, value: str) -> List[Group]:
        """Возвращает группу по названию

        Args:
            value (str): Название группы

        Returns:
            List[Group]: Список групп
        """
        stmt = select(Group).where(Group.name == value)
        return self.session.exec(stmt).all()

    def CreateGroup(
        self,
        id: int,
        guid: UUID,
        name: str,
        faculty_name: str
        ) -> Group:
        """Создает новую группу.

        Args:
            id (int): ID группы
            guid (UUID): GUID группы
            name (str): Имя группы
            faculty_name (str): Название факультета

        Returns:
            Group: Созданная группа
        """
        option = Group(id=id, guid=guid, name=name, faculty_name=faculty_name)
        self.session.add(option)
        self.session.commit()
        self.session.refresh(option)
        return option

    def UpdateGroup(self, value: int, name: str, faculty_name: str) -> bool:
        """Обновляет гурппу по ID.

        Args:
            value (int): ID группы
            name (str): Имя группы
            faculty_name (str): Название факультета

        Returns:
            bool: True, если обновление прошло успешно
        """
        try:
            stmt = update(Group).where(Group.id == value).values(name=name, faculty_name=faculty_name)
            result = self.session.exec(stmt)
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            return False

    def DeleteGroup(self, value: int) -> bool:
        """Удаляет группу по ID.

        Args:
            value (int): ID группы

        Returns:
            bool: True, если удаление прошло успешно
        """
        try:
            stmt = delete(Group).where(Group.id == value)
            result = self.session.exec(stmt)
            self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            self.session.rollback()
            return False
