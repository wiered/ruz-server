import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, delete, select, update

from models import Discipline

logger = logging.getLogger(__name__)

class DisciplineRepository:
    def __init__(self, session: Session):
        self.session = session

    def Create(self, discipline: Discipline):
        """Adds a new discipline to the database.

        Args:
            discipline (Discipline): The discipline to add.

        Returns:
            Discipline: The added discipline.
        """
        logger.info(f"Creating Discipline {discipline.name}")

        self.session.add(discipline)
        self.session.commit()
        return discipline

    def GetOrCreate(self, discipline: Discipline):
        """Gets a discipline by ID, or creates a new one if it doesn't exist.

        Args:
            discipline (Discipline): The discipline to get or create.

        Returns:
            Discipline: The existing or newly-created discipline.
        """
        logger.info(f"Getting or creating Discipline {discipline.name}")

        existing = self.GetById(discipline.id)
        if existing:
            logger.debug(f"Discipline {discipline.name} already exists")
            return existing

        logger.debug(f"Discipline {discipline.name} does not exist, creating")
        return self.Create(discipline)

    def ListAll(self):
        """Returns a list of all disciplines.

        Returns:
            List[Discipline]: A list of all disciplines in the database.
        """
        logger.info("Listing all disciplines")

        stmt = select(Discipline)
        return self.session.exec(stmt).all()

    def GetById(self, value: int):
        """Gets a discipline by ID.

        Args:
            value (int): The ID of the discipline to get.

        Returns:
            Optional[Discipline]: The discipline with the given ID, or None if no such discipline exists.
        """
        logger.info(f"Getting Discipline {value}")

        stmt = select(Discipline).where(Discipline.id == value)
        return self.session.exec(stmt).first()

    def GetByName(self, value: str):
        """Gets a discipline by name.

        Args:
            value (str): The name of the discipline to get.

        Returns:
            Optional[Discipline]: The discipline with the given name, or None if no such discipline exists.
        """
        logger.info(f"Getting Discipline {value}")

        stmt = select(Discipline).where(Discipline.name == value)
        return self.session.exec(stmt).first()

    def GetByExamType(self, value: str):
        """Gets all disciplines with the given exam type.

        Args:
            value (str): The exam type to search for.

        Returns:
            List[Discipline]: A list of all disciplines with the given exam type.
        """
        logger.info(f"Getting Discipline {value}")

        stmt = select(Discipline).where(Discipline.examtype == value)
        return self.session.exec(stmt).all()

    def Update(self, value: int, name: str, examtype: str, has_labs: bool):
        """Updates a discipline by ID.

        Args:
            value (int): The ID of the discipline to update.
            name (str): The new name of the discipline.
            examtype (str): The new exam type of the discipline.
            has_labs (bool): Whether the discipline has labs.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        logger.info(f"Updating Discipline {value}")

        try:
            current = self.GetById(value)

            if current is None:
                logger.error(f"Discipline {value} does not exist")
                return False

            if name is None:
                logger.debug(f"Payload does not have a name")
                name = current.name
            if examtype is None:
                logger.debug(f"Payload does not have an exam type")
                examtype = current.examtype
            if has_labs is None:
                logger.debug(f"Payload does not have a has_labs")
                has_labs = current.has_labs

            stmt = (
                update(Discipline)
                .where(Discipline.id == value)
                .values(name=name, examtype=examtype, has_labs=has_labs)
            )
            result = self.session.exec(stmt)
            self.session.commit()
            logger.debug(f"Discipline {value} updated")
            return result.rowcount > 0
        except SQLAlchemyError as e:
            logger.error(f"Discipline {value} update failed: \n{e}")
            self.session.rollback()
            return False

    def Delete(self, value: int):
        """Deletes a discipline by ID.

        Args:
            value (int): The ID of the discipline to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        logger.info(f"Deleting Discipline {value}")
        try:
            stmt = delete(Discipline).where(Discipline.id == value)
            result = self.session.exec(stmt)
            self.session.commit()
            logger.debug(f"Discipline {value} deleted")
            return result.rowcount > 0
        except SQLAlchemyError as e:
            logger.error(f"Discipline {value} delete failed: \n{e}")
            self.session.rollback()
            return False
