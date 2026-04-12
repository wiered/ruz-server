from typing import Generator, List, Optional

from fastapi import APIRouter, Depends, Security
from pydantic import BaseModel, ConfigDict
from sqlmodel import Session

from ruz_server.api.security import require_api_key
from ruz_server.database import db
from ruz_server.helpers.api_helpers import (
    ensure_entity_doesnot_exist,
    ensure_entity_exists,
)
from ruz_server.models import KindOfWork
from ruz_server.repositories import KindOfWorkRepository

router = APIRouter(prefix="/kind_of_work", tags=["kind_of_work"])


def get_db() -> Generator[Session, None, None]:
    yield from db.get_session()


class KindOfWorkRead(BaseModel):
    """
    Read schema for KindOfWork entity. Used to represent a kind of work record.

    Args:
        id (int): Unique identifier of the kind of work.
        type_of_work (str): The type or description of work.
        complexity (int): Complexity level of the work.

    Returns:
        KindOfWorkRead: Instance representing the kind of work record.
    """

    id: int
    type_of_work: str
    complexity: int

    model_config = ConfigDict(from_attributes=True)


class KindOfWorkCreate(BaseModel):
    """
    Create schema for KindOfWork entity. Used for creating a new kind of work record.

    Args:
        id (int): Unique identifier for the kind of work.
        type_of_work (str): The type or description of work.
        complexity (int): Complexity level of the work.

    Returns:
        KindOfWorkCreate: Instance representing the kind of work to be created.
    """

    id: int
    type_of_work: str
    complexity: int


class KindOfWorkUpdate(BaseModel):
    """
    Update schema for KindOfWork entity. Used for partial updates of a kind of work record.

    Args:
        type_of_work (Optional[str] | None): The new type or description of work, or None to leave unchanged.
        complexity (Optional[int] | None): The new complexity level, or None to leave unchanged.

    Returns:
        KindOfWorkUpdate: Instance representing the requested changes for the kind of work record.
    """

    type_of_work: Optional[str] | None = None
    complexity: Optional[int] | None = None


@router.post("/", response_model=KindOfWorkRead)
def create_kind_of_work(
    payload: KindOfWorkCreate,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key),
):
    """
    Creates a new KindOfWork object in the database.

    Args:
        payload (KindOfWorkCreate): The data for the new KindOfWork entity to be created.
        session (Session, optional): The database session dependency.
        _api_key (str, optional): The API key for authentication.

    Returns:
        KindOfWorkRead: The created KindOfWork object.
    """
    repo = KindOfWorkRepository(session)
    ensure_entity_doesnot_exist(payload.id, repo.GetById)

    return repo.Create(
        KindOfWork(
            id=payload.id,
            type_of_work=payload.type_of_work,
            complexity=payload.complexity,
        )
    )


@router.get("/", response_model=List[KindOfWorkRead])
def list_kind_of_works(
    session: Session = Depends(get_db), _api_key: str = Security(require_api_key)
):
    """
    Gets all KindOfWork objects from the database.

    Returns:
        List[KindOfWorkRead]: List of all KindOfWork objects.
    """
    repo = KindOfWorkRepository(session)
    return repo.ListAll()


@router.get("/{id}", response_model=KindOfWorkRead)
def get_kind_of_work(
    id: int,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key),
):
    """
    Gets a KindOfWork object from the database by ID.

    Args:
        id (int): ID of the KindOfWork object to retrieve.

    Returns:
        KindOfWorkRead: The retrieved KindOfWork object.
    """
    repo = KindOfWorkRepository(session)
    return ensure_entity_exists(id, repo.GetById)


@router.put("/{id}")
def update_kind_of_work(
    id: int,
    payload: KindOfWorkUpdate,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key),
):
    """
    Updates a KindOfWork object in the database.

    Args:
        id (int): ID of the KindOfWork object to update.
        payload (KindOfWorkUpdate): Updated values for the KindOfWork object.

    Returns:
        KindOfWorkRead: The updated KindOfWork object.
    """
    repo = KindOfWorkRepository(session)
    ensure_entity_exists(id, repo.GetById)

    return repo.Update(id, payload.type_of_work, payload.complexity)


@router.delete("/{id}")
def delete_kind_of_work(
    id: int,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key),
):
    """
    Deletes a KindOfWork object from the database.

    Args:
        id (int): ID of the KindOfWork object to delete.

    Returns:
        None
    """
    repo = KindOfWorkRepository(session)
    ensure_entity_exists(id, repo.GetById)

    return repo.Delete(id)
