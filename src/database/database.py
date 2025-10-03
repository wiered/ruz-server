
"""This is db module.

This module handles dealing with postgre database.
"""

__all__ = ["DataBase"]
__version__ = "1.0"
__author__ = "Wiered"

import logging
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

import models as models
from settings import settings

logger = logging.getLogger(__name__)

class DataBase:
    def __init__(self, postgresql_uri):
        self._sqlalchemy_url = postgresql_uri
        self.engine = create_engine(self._sqlalchemy_url, echo=True)
        logger.info(f"Started database engine")

    def getSession(self) -> Session:
        """
        Возвращает новый объект Session для работы с моделями SQLModel.
        """
        return Session(self.engine)

    def get_session(self) -> Generator[Session, None, None]:
        session = Session(self.engine)
        try:
            logger.info(f"Started session")
            yield session
        finally:
            session.close()

    def createAllTables(self) -> None:
        """
        Создаёт в базе все таблицы, описанные в SQLModel-моделях.
        """
        logger.info(f"Creating all tables")

        SQLModel.metadata.create_all(self.engine)

    def dropAllTables(self) -> None:
        """
        Удаляет из базы все таблицы, описанные в SQLModel-моделях.
        """
        logger.warning(f"Dropping all tables")

        SQLModel.metadata.drop_all(self.engine)

db = DataBase(settings.postgresql_uri)
