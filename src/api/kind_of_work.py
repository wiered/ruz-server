from typing import Generator, List, Optional
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security, status
from pydantic import BaseModel
from sqlmodel import Session

from api.security import require_api_key
from database import db
from models import KindOfWork
from repositories import KindOfWorkRepository
from helpers.api_helpers import ensure_entity_exists, ensure_entity_doesnot_exist

router = APIRouter(prefix="/kind_of_work", tags=["kind_of_work"])

def get_db() -> Generator[Session, None, None]:
    yield from db.get_session()

class KindOfWorkRead(BaseModel):
    """Read schema for KindOfWork entity. Mirrors persisted fields for API responses."""
    id: int
    type_of_work: str
    complexity: int

    class Config:
        orm_mode = True


class KindOfWorkCreate(BaseModel):
    """Create schema for KindOfWork entity. Used to create a new kind of work record."""
    id: int
    type_of_work: str
    complexity: int


class KindOfWorkUpdate(BaseModel):
    """Update schema for KindOfWork entity. All fields are optional for partial updates."""
    type_of_work: Optional[str] | None = None
    complexity: Optional[int] | None = None


@router.post("/", response_model=KindOfWorkRead)
def create_kind_of_work(
    payload: KindOfWorkCreate,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """
    Creates a new KindOfWork if it doesn't exist, otherwise it retrieves the existing one.

    Args:
        payload (KindOfWorkCreate): Kind of work to be created or retrieved.

    Returns:
        KindOfWorkRead: Created or retrieved KindOfWork.
    """
    repo = KindOfWorkRepository(session)
    ensure_entity_doesnot_exist(payload.id, repo.GetById)

    return repo.Create(
        KindOfWork(
            id=payload.id,
            type_of_work=payload.type_of_work,
            complexity=payload.complexity
        )
    )


@router.get("/", response_model=List[KindOfWorkRead])
def list_kind_of_works(
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key)
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
    _api_key: str = Security(require_api_key)
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
    _api_key: str = Security(require_api_key)
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

    return repo.Update(
        id,
        payload.type_of_work,
        payload.complexity
    )

@router.delete("/{id}")
def delete_kind_of_work(
    id: int,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key)
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


