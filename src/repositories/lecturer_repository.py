import logging
from typing import List, Optional

from sqlalchemy import UUID
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, delete, select, update

from models import Lecturer

logger = logging.getLogger(__name__)


class LecturerRepository:
    def __init__(self, session: Session):
        self.session = session

    def Create(self, lecturer: Lecturer) -> Lecturer:
        """
        Creates a new Lecturer object in the database.

        Args:
            lecturer (Lecturer): The Lecturer object to be created.

        Returns:
            Lecturer: The created Lecturer object.
        """
        logger.info(f"Creating Lecturer {lecturer.full_name}")

        self.session.add(lecturer)
        self.session.commit()
        return lecturer

    def GetOrCreate(self, lecturer: Lecturer) -> Lecturer:
        """
        Gets a Lecturer by ID, or creates a new one if it doesn't exist.

        Args:
            lecturer (Lecturer): The Lecturer to get or create.

        Returns:
            Lecturer: The existing or newly-created Lecturer.
        """
        logger.info(f"Getting or creating Lecturer {lecturer.full_name}")

        existing = self.GetById(lecturer.id)
        if existing:
            logger.debug(f"Lecturer {lecturer.full_name} already exists")
            return existing

        logger.debug(f"Lecturer {lecturer.full_name} does not exist, creating")
        return self.Create(lecturer)

    def ListAll(self) -> List[Lecturer]:
        """
        Returns a list of all Lecturer objects in the database.

        Returns:
            List[Lecturer]: A list of all Lecturer objects in the database.
        """
        logger.info("Listing all Lecturers")

        stmt = select(Lecturer)
        return self.session.exec(stmt).all()

    def GetById(self, value: int) -> Optional[Lecturer]:
        """
        Gets a Lecturer by ID.

        Args:
            value (int): The ID of the Lecturer to get.

        Returns:
            Optional[Lecturer]: The Lecturer with the given ID, or None if no such Lecturer exists.
        """
        logger.info(f"Getting Lecturer {value}")

        stmt = select(Lecturer).where(Lecturer.id == value)
        return self.session.exec(stmt).first()

    def GetByGUID(self, value: UUID) -> Optional[Lecturer]:
        """
        Gets a Lecturer by GUID.

        Args:
            value (UUID): The GUID of the Lecturer to get.

        Returns:
            Optional[Lecturer]: The Lecturer with the given GUID, or None if no such Lecturer exists.
        """
        logger.info(f"Getting Lecturer {value}")

        stmt = select(Lecturer).where(Lecturer.guid == value)
        return self.session.exec(stmt).first()

    def GetWithLessons(self, value: int) -> Optional[Lecturer]:
        """
        Gets a Lecturer by ID, with all its lessons.

        Args:
            value (int): The ID of the Lecturer to get.

        Returns:
            Optional[Lecturer]: The Lecturer with the given ID, or None if no such Lecturer exists.
        """
        logger.info(f"Getting Lecturer {value}")

        stmt = (
            select(Lecturer)
            .where(Lecturer.id == value)
            .options(selectinload(Lecturer.lessons))
        )
        return self.session.exec(stmt).first()

    def Update(
        self,
        value: int,
        full_name: str = None,
        short_name: str = None,
        rank: str = None
    ) -> bool:
        """
        Updates a Lecturer by ID.

        Args:
            value (int): The ID of the Lecturer to update.
            full_name (str, optional): The new full name of the Lecturer. Defaults to the current full name if not provided.
            short_name (str, optional): The new short name of the Lecturer. Defaults to the current short name if not provided.
            rank (str, optional): The new rank of the Lecturer. Defaults to the current rank if not provided.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        logger.info(f"Updating Lecturer {value}")

        try:
            current = self.GetById(value)

            if current is None:
                logger.error(f"Lecturer {value} does not exist")
                return False

            if full_name is None:
                logger.debug(f"Payload does not have a full name")
                full_name = current.full_name
            if short_name is None:
                logger.debug(f"Payload does not have a short name")
                short_name = current.short_name
            if rank is None:
                logger.debug(f"Payload does not have a rank")
                rank = current.rank

            stmt = (
                update(Lecturer).
                where(Lecturer.id == value).
                values(full_name=full_name, short_name=short_name, rank=rank)
            )
            result = self.session.exec(stmt)
            self.session.commit()
            logger.info(f"Updated Lecturer {value}")
            return result.rowcount > 0
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Lecturer update failed: \n{e}")
            return False

    def Delete(self, value: int) -> bool:
        """
        Deletes a Lecturer by ID.

        Args:
            value (int): The ID of the Lecturer to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        logger.info(f"Deleting Lecturer {value}")

        try:
            stmt = delete(Lecturer).where(Lecturer.id == value)
            result = self.session.exec(stmt)
            self.session.commit()
            logger.debug(f"Lecturer {value} deleted")
            return result.rowcount > 0
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Lecturer {value} delete failed: \n{e}")
            return False
