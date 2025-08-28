import datetime
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import UUID, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, delete, select, update

from models import Auditorium

logger = logging.getLogger(__name__)

class AuditoriumRepository:
    def __init__(self, session: Session):
        logger.debug(f"Created AuditoriumRepository")

        self.session = session

    def Create(self, auditorium: Auditorium):
        """
        Creates a new Auditorium in the database.

        Args:
            auditorium (Auditorium): The Auditorium to be created.

        Returns:
            Auditorium: The created Auditorium.
        """
        logger.info(f"Creating Auditorium {auditorium}")

        self.session.add(auditorium)
        self.session.commit()
        return auditorium

    def GetOrCreate(self, auditorium: Auditorium):
        """
        Gets a Auditorium by ID, or creates a new one if it doesn't exist.

        Args:
            auditorium (Auditorium): The Auditorium to get or create.

        Returns:
            Auditorium: The existing or newly-created Auditorium.
        """
        logger.info(f"Getting or creating Auditorium {auditorium}")

        existing = self.GetById(auditorium.id)
        if existing:
            logger.debug(f"Auditorium {auditorium} already exists")
            return existing
        logger.debug(f"Auditorium {auditorium} does not exist, creating")
        return self.Create(auditorium)

    def ListAll(self):
        """
        Gets all Auditorium objects from the database.

        Returns:
            List[Auditorium]: List of all Auditorium objects.
        """
        logger.info(f"Listing all Auditoriums")

        stmt = select(Auditorium)
        return self.session.exec(stmt).all()

    def GetById(self, value: int):
        """
        Gets a Auditorium by ID.

        Args:
            value (int): The ID of the Auditorium to get.

        Returns:
            Optional[Auditorium]: The Auditorium with the given ID, or None if no such Auditorium exists.
        """
        logger.info(f"Getting Auditorium by ID {value}")

        stmt = select(Auditorium).where(Auditorium.id == value)
        return self.session.exec(stmt).first()

    def GetByGuid(self, value: UUID):
        """
        Gets a Auditorium by GUID.

        Args:
            value (UUID): The GUID of the Auditorium to get.

        Returns:
            Optional[Auditorium]: The Auditorium with the given GUID, or None if no such Auditorium exists.
        """
        logger.info(f"Getting Auditorium by GUID {value}")

        stmt = select(Auditorium).where(Auditorium.guid == value)
        return self.session.exec(stmt).first()

    def GetByName(self, value: str):
        """
        Gets a Auditorium by name.

        Args:
            value (str): The name of the Auditorium to get.

        Returns:
            Optional[Auditorium]: The Auditorium with the given name, or None if no such Auditorium exists.
        """
        logger.info(f"Getting Auditorium by name {value}")

        stmt = select(Auditorium).where(Auditorium.name == value)
        return self.session.exec(stmt).first()

    def Update(
        self,
        value: int,
        name: Optional[str],
        building: Optional[str]
    ) -> bool:
        """
        Updates a Auditorium by ID.

        Args:
            value (int): The ID of the Auditorium to update.
            name (Optional[str], optional): New name of the Auditorium. Defaults to the current name if not provided.
            building (Optional[str], optional): New name of the building of the Auditorium. Defaults to the current building if not provided.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        logger.info(f"Updating Auditorium {value}")

        try:
            current = self.GetById(value)

            if current is None:
                logger.error(f"Auditorium {value} does not exist")
                return False

            if name is None:
                logger.debug(f"Auditorium {value} does not have a name")
                name = current.name
            if building is None:
                logger.debug(f"Auditorium {value} does not have a building")
                building = current.building

            stmt = (
                update(Auditorium)
                .where(Auditorium.id == value)
                .values(name=name, building=building)
            )
            result = self.session.exec(stmt)
            self.session.commit()
            logger.debug(f"Auditorium {value} updated")
            return result.rowcount > 0
        except SQLAlchemyError as e:
            logger.error(f"Auditorium {value} update failed: \n{e}")
            self.session.rollback()
            return False

    def Delete(self, value: int):
        """
        Deletes a Auditorium by ID.

        Args:
            value (int): The ID of the Auditorium to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        logger.info(f"Deleting Auditorium {value}")

        try:
            stmt = delete(Auditorium).where(Auditorium.id == value)
            result = self.session.exec(stmt)
            self.session.commit()
            logger.debug(f"Auditorium {value} deleted")
            return result.rowcount > 0
        except SQLAlchemyError as e:
            logger.error(f"Auditorium {value} delete failed: \n{e}")
            self.session.rollback()
            return False
