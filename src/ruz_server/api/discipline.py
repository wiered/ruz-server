from typing import Generator, List, Optional

from fastapi import APIRouter, Depends, Security, status
from pydantic import BaseModel, ConfigDict
from sqlmodel import Session

from ruz_server.api.security import require_api_key
from ruz_server.database import db
from ruz_server.helpers.api_helpers import (ensure_entity_doesnot_exist,
                                 ensure_entity_exists)
from ruz_server.models import Discipline
from ruz_server.repositories import DisciplineRepository

router = APIRouter(prefix="/discipline", tags=["discipline"])

def get_db() -> Generator[Session, None, None]:
    yield from db.get_session()


class DisciplineRead(BaseModel):
    """
    Response model for reading Discipline entity data.

    Attributes:
        id (int): The unique identifier of the discipline.
        name (str): The name of the discipline.
        examtype (Optional[str]): The exam type associated with the discipline.
        has_labs (bool): Indicates whether this discipline includes laboratory work.
    """
    id: int
    name: str
    examtype: Optional[str] = None
    has_labs: bool = False

    model_config = ConfigDict(from_attributes=True)


class DisciplineCreate(BaseModel):
    """
    Request model for creating a new Discipline entity.

    Args:
        id (int): The unique identifier for the discipline.
        name (str): The name of the discipline.
        examtype (Optional[str], optional): The exam type associated with the discipline. Defaults to None.
        has_labs (Optional[bool], optional): Indicates if the discipline includes laboratory work. Defaults to False.
    """
    id: int
    name: str
    examtype: Optional[str] | None = None
    has_labs: bool | None = False


class DisciplineUpdate(BaseModel):
    """
    Request model for updating an existing Discipline entity.

    Args:
        name (Optional[str], optional): The updated name of the discipline. Defaults to None.
        examtype (Optional[str], optional): The updated exam type associated with the discipline. Defaults to None.
        has_labs (Optional[bool], optional): Indicates if the discipline includes laboratory work. Defaults to None.
    """
    name: Optional[str] | None = None
    examtype: Optional[str] | None = None
    has_labs: Optional[bool] | None = None


@router.post("/", response_model=DisciplineRead, status_code=status.HTTP_201_CREATED)
def create_discipline(
    payload: DisciplineCreate,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """
    Creates a new discipline entity based on the provided payload.

    Args:
        payload (DisciplineCreate): The payload containing the details of the discipline to be created.
        session (Session, optional): The database session dependency.
        _api_key (str, optional): The API key for authentication.

    Returns:
        DisciplineRead: The created discipline entity.
    """
    repo = DisciplineRepository(session)
    ensure_entity_doesnot_exist(payload.id, repo.GetById)

    return repo.Create(
        Discipline(
            id=payload.id,
            name=payload.name,
            examtype=payload.examtype,
            has_labs=bool(payload.has_labs) if payload.has_labs is not None else False,
        )
    )


@router.get("/", response_model=List[DisciplineRead])
def list_disciplines(
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """
    Retrieves a list of all discipline entities.

    Args:
        session (Session, optional): The database session dependency.
        _api_key (str, optional): The API key for authentication.

    Returns:
        List[DisciplineRead]: A list of all discipline entities.
    """
    repo = DisciplineRepository(session)
    return repo.ListAll()


@router.get("/{discipline_id}", response_model=DisciplineRead)
def get_discipline(
    discipline_id: int,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """
    Retrieves a discipline entity by its unique identifier.

    Args:
        discipline_id (int): The unique identifier of the discipline.
        session (Session, optional): The database session dependency.
        _api_key (str, optional): The API key for authentication.

    Returns:
        DisciplineRead: The requested discipline entity if found.
    """
    repo = DisciplineRepository(session)
    return ensure_entity_exists(discipline_id, repo.GetById)


@router.put("/{discipline_id}")
def update_discipline(
    discipline_id: int,
    payload: DisciplineUpdate,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """
    Updates an existing discipline entity by its unique identifier.

    Args:
        discipline_id (int): The unique identifier of the discipline to update.
        payload (DisciplineUpdate): The data to update the discipline with.
        session (Session, optional): The database session dependency.
        _api_key (str, optional): The API key for authentication.

    Returns:
        dict: The updated discipline entity.
    """
    repo = DisciplineRepository(session)
    ensure_entity_exists(discipline_id, repo.GetById)
    return repo.Update(
        discipline_id,
        payload.name,
        payload.examtype,
        payload.has_labs
    )


@router.delete("/{discipline_id}")
def delete_discipline(
    discipline_id: int,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """
    Deletes a discipline entity by its unique identifier.

    Args:
        discipline_id (int): The unique identifier of the discipline to delete.
        session (Session, optional): The database session dependency.
        _api_key (str, optional): The API key for authentication.

    Returns:
        dict: The result of the deletion operation.
    """
    repo = DisciplineRepository(session)
    ensure_entity_exists(discipline_id, repo.GetById)
    return repo.Delete(discipline_id)
