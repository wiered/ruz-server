"""This is db module.

This module handles dealing with postgre database.
"""

__all__ = ["DataBase"]
__author__ = "Wiered"

import logging
from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from ruz_server.settings import settings

logger = logging.getLogger(__name__)


class DataBase:
    """
    DataBase class for managing PostgreSQL database operations using SQLModel.

    This class provides methods to initialize the database engine, manage sessions,
    and create or drop all tables defined in the SQLModel models.

    Args:
        postgresql_uri (str): The URI string for connecting to the PostgreSQL database.

    Methods:
        getSession() -> Session:
            Returns a new SQLModel Session instance for database transactions.

        get_session() -> Generator[Session, None, None]:
            Provides a context-managed SQLModel Session generator for use in dependency injection.

        createAllTables() -> None:
            Creates all tables defined in the SQLModel metadata within the connected database.

        dropAllTables() -> None:
            Drops all tables defined in the SQLModel metadata from the connected database.
    """

    def __init__(self, postgresql_uri):
        self._sqlalchemy_url = postgresql_uri
        self.engine = create_engine(self._sqlalchemy_url, echo=True)
        logger.info("Started database engine")

    def getSession(self) -> Session:
        """
        Returns a new SQLModel Session instance.

        This method creates and returns a new Session object using the database engine,
        which can be used to perform database operations.

        Returns:
            Session: The newly created SQLModel Session object.
        """
        return Session(self.engine)

    def get_session(self) -> Generator[Session, None, None]:
        """
        Provides a generator for a context-managed SQLModel Session.

        This method is typically used for dependency injection in FastAPI routes.
        It yields a database Session instance and ensures that the session is closed after use.

        Yields:
            Session: A context-managed SQLModel Session object for interacting with the database.

        Example:
            @app.get("/items/")
            def read_items(db: Session = Depends(db.get_session)):
                # use db to interact with the database
        """
        session = Session(self.engine)
        try:
            logger.info("Started session")
            yield session
        finally:
            session.close()

    def createAllTables(self) -> None:
        """
        Creates all tables defined in the SQLModel models in the connected database.

        This method creates the database schema by generating all tables specified in the
        SQLModel models' metadata if they do not already exist.

        Args:
            None

        Returns:
            None
        """
        logger.info("Creating all tables")

        SQLModel.metadata.create_all(self.engine)

    def dropAllTables(self) -> None:
        """
        Drops all tables defined in the SQLModel models from the connected database.

        This method removes the entire database schema by dropping all tables specified
        in the SQLModel models' metadata.

        Args:
            None

        Returns:
            None
        """
        logger.warning("Dropping all tables")

        SQLModel.metadata.drop_all(self.engine)


db = DataBase(settings.postgresql_uri)
