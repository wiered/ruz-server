from typing import Generator, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Security, status
from pydantic import BaseModel, ConfigDict
from sqlmodel import Session

from ruz_server.api.security import require_api_key
from ruz_server.database import db
from ruz_server.helpers.api_helpers import (
    ensure_entity_doesnot_exist,
    ensure_entity_exists,
)
from ruz_server.models import Auditorium
from ruz_server.repositories import AuditoriumRepository

router = APIRouter(prefix="/auditorium", tags=["auditorium"])


def get_db() -> Generator[Session, None, None]:
    yield from db.get_session()


class AuditoriumRead(BaseModel):
    """
    Response model for reading Auditorium entity data.

    Attributes:
        id (int): The unique identifier of the auditorium.
        guid (UUID): The global unique identifier for the auditorium.
        name (str): The name of the auditorium.
        building (str): The building where the auditorium is located.
    """

    id: int
    guid: UUID
    name: str
    building: str

    model_config = ConfigDict(from_attributes=True)


class AuditoriumCreate(BaseModel):
    """
    Request model for creating a new Auditorium entity.

    This schema is used when posting data to create an Auditorium.

    Args:
        id (int): The unique integer identifier for the auditorium.
        guid (UUID): The global unique identifier for the auditorium.
        name (str): The name of the auditorium.
        building (str): The building in which the auditorium is located.

    Returns:
        AuditoriumCreate: Instance representing the new auditorium to be created.
    """

    id: int
    guid: UUID
    name: str
    building: str


class AuditoriumUpdate(BaseModel):
    """
    Request model for updating an existing Auditorium entity.

    This schema is used when submitting data to update an Auditorium's details.

    Args:
        name (Optional[str] | None): The new name of the auditorium, or None to leave unchanged.
        building (Optional[str] | None): The new building of the auditorium, or None to leave unchanged.

    Returns:
        AuditoriumUpdate: Instance representing the requested changes to the auditorium.
    """

    name: Optional[str] | None = None
    building: Optional[str] | None = None


@router.post("/", response_model=AuditoriumRead, status_code=status.HTTP_201_CREATED)
def create_auditorium(payload: AuditoriumCreate, session: Session = Depends(get_db)):
    """
    Create a new Auditorium entity in the database.

    This endpoint accepts an AuditoriumCreate payload and creates a new Auditorium record
    with the provided id, guid, name, and building fields. If an Auditorium with the same id
    already exists, an error is raised.

    Args:
        payload (AuditoriumCreate): The data required to create a new auditorium.
        session (Session): SQLModel database session (dependency-injected).

    Returns:
        Auditorium: The created Auditorium instance.
    """
    repo = AuditoriumRepository(session)
    ensure_entity_doesnot_exist(payload.id, repo.GetById)

    return repo.Create(
        Auditorium(
            id=payload.id,
            guid=payload.guid,
            name=payload.name,
            building=payload.building,
        )
    )


@router.get("/", response_model=List[AuditoriumRead])
def list_auditoriums(session: Session = Depends(get_db)):
    """
    Retrieve a list of all Auditorium entities.

    This endpoint returns a list containing all existing Auditorium records from the database.

    Args:
        session (Session): SQLModel database session (dependency-injected).

    Returns:
        List[AuditoriumRead]: A list of Auditorium entities.
    """
    repo = AuditoriumRepository(session)
    return repo.ListAll()


@router.get("/{auditorium_id}", response_model=AuditoriumRead)
def get_auditorium(auditorium_id: int, session: Session = Depends(get_db)):
    """
    Retrieve a single Auditorium entity by its ID.

    This endpoint fetches an Auditorium record from the database using the specified unique identifier.
    If the auditorium does not exist, a 404 error is raised.

    Args:
        auditorium_id (int): The unique identifier of the auditorium to retrieve.
        session (Session): SQLModel database session (dependency-injected).

    Returns:
        AuditoriumRead: The Auditorium entity matching the given ID.
    """
    repo = AuditoriumRepository(session)
    return ensure_entity_exists(auditorium_id, repo.GetById)


@router.get("/guid/{auditorium_guid}", response_model=AuditoriumRead)
def get_auditorium_by_guid(auditorium_guid: UUID, session: Session = Depends(get_db)):
    """
    Retrieve a single Auditorium entity by its GUID.

    This endpoint fetches an Auditorium record from the database using the specified unique GUID.
    If the auditorium does not exist, a 404 error is raised.

    Args:
        auditorium_guid (UUID): The unique GUID of the auditorium to retrieve.
        session (Session): SQLModel database session (dependency-injected).

    Returns:
        AuditoriumRead: The Auditorium entity matching the given GUID.
    """
    repo = AuditoriumRepository(session)
    return ensure_entity_exists(auditorium_guid, repo.GetByGuid)


@router.put("/{auditorium_id}")
def update_auditorium(
    auditorium_id: int, payload: AuditoriumUpdate, session: Session = Depends(get_db)
):
    """
    Update an Auditorium entity by its ID.

    This endpoint updates the name and/or building of the specified Auditorium record
    in the database. If the auditorium does not exist, a 404 error is raised.

    Args:
        auditorium_id (int): The unique identifier of the auditorium to update.
        payload (AuditoriumUpdate): The payload containing updated auditorium fields (name, building).
        session (Session): SQLModel database session (dependency-injected).

    Returns:
        AuditoriumRead: The updated Auditorium entity.
    """
    repo = AuditoriumRepository(session)
    ensure_entity_exists(auditorium_id, repo.GetById)

    return repo.Update(auditorium_id, payload.name, payload.building)


@router.delete("/{auditorium_id}")
def delete_auditorium(auditorium_id: int, session: Session = Depends(get_db)):
    """
    Delete an Auditorium by its identifier.

    Args:
        auditorium_id (int): The unique identifier of the auditorium to delete.

    Returns:
        Any: The result of the deletion operation.
    """
    repo = AuditoriumRepository(session)
    ensure_entity_exists(auditorium_id, repo.GetById)

    return repo.Delete(auditorium_id)
