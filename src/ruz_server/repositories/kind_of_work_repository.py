import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, delete, select, update

from ruz_server.models import KindOfWork

logger = logging.getLogger(__name__)


class KindOfWorkRepository:
    """
    KindOfWorkRepository handles operations related to KindOfWork entities.
    This repository provides methods for managing KindOfWork objects in the database,
    including creation, retrieval, and listing of records.

    Args:
        session (Session): The database session to be used for operations.

    Returns:
        KindOfWorkRepository: An instance for interacting with KindOfWork data.
    """

    def __init__(self, session: Session):
        self.session = session

    def Create(self, kind_of_work: KindOfWork):
        """
        Creates a new KindOfWork.

        Args:
            kind_of_work (KindOfWork): Kind of work to be created.

        Returns:
            KindOfWork: Created KindOfWork.
        """
        logger.info(f"Creating KindOfWork {kind_of_work.type_of_work}")

        self.session.add(kind_of_work)
        self.session.commit()
        return kind_of_work

    def GetOrCreate(self, kind_of_work: KindOfWork):
        """
        Creates a new KindOfWork if it doesn't exist, otherwise it retrieves the existing one.

        Args:
            kind_of_work (KindOfWork): Kind of work to be created or retrieved.

        Returns:
            KindOfWork: Created or retrieved KindOfWork.
        """
        logger.info(f"Getting or creating KindOfWork {kind_of_work.type_of_work}")

        existing = self.GetById(kind_of_work.id)
        if existing:
            logger.debug(f"KindOfWork {kind_of_work.type_of_work} already exists")
            return existing

        logger.debug(f"KindOfWork {kind_of_work.type_of_work} does not exist, creating")
        return self.Create(kind_of_work)

    def ListAll(self):
        """
        Gets all KindOfWork objects from the database.

        Returns:
            List[KindOfWork]: List of all KindOfWork objects.
        """
        logger.info("Listing all KindOfWorks")

        stmt = select(KindOfWork)
        return self.session.exec(stmt).all()

    def GetById(self, value: int):
        """
        Gets a KindOfWork object from the database by its ID.

        Args:
            value (int): ID of the KindOfWork object to be retrieved.

        Returns:
            KindOfWork: Retrieved KindOfWork object or None if no such object exists.
        """
        logger.info(f"Getting KindOfWork {value}")

        stmt = select(KindOfWork).where(KindOfWork.id == value)
        return self.session.exec(stmt).first()

    def Update(self, value: int, type_of_work: str, complexity: int):
        """
        Updates a KindOfWork object in the database.

        Args:
            value (int): ID of the KindOfWork object to be updated.
            type_of_work (str): New type of work.
            complexity (int): New complexity.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        logger.info(f"Updating KindOfWork {value}")

        try:
            current = self.GetById(value)

            if current is None:
                logger.error(f"KindOfWork {value} does not exist")
                return False

            if type_of_work is None:
                logger.debug("Payload does not have a type of work")
                type_of_work = current.type_of_work
            if complexity is None:
                logger.debug("Payload does not have a complexity")
                complexity = current.complexity

            stmt = (
                update(KindOfWork)
                .where(KindOfWork.id == value)
                .values(type_of_work=type_of_work, complexity=complexity)
            )
            result = self.session.exec(stmt)
            self.session.commit()
            logger.debug(f"KindOfWork {value} updated")
            return result.rowcount > 0
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"KindOfWork {value} update failed: \n{e}")
            return False

    def Delete(self, value: int) -> bool:
        """
        Deletes a KindOfWork object from the database by its ID.

        Args:
            value (int): ID of the KindOfWork object to be deleted.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        logger.info(f"Deleting KindOfWork {value}")

        try:
            stmt = delete(KindOfWork).where(KindOfWork.id == value)
            result = self.session.exec(stmt)
            self.session.commit()
            logger.debug(f"KindOfWork {value} deleted")
            return result.rowcount > 0
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"KindOfWork {value} delete failed: \n{e}")
            return False
