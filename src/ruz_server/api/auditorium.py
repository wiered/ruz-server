from typing import Generator, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Security, status
from pydantic import BaseModel, ConfigDict
from sqlmodel import Session

from ruz_server.api.security import require_api_key
from ruz_server.database import db
from ruz_server.helpers.api_helpers import (ensure_entity_doesnot_exist,
                                 ensure_entity_exists)
from ruz_server.models import Auditorium
from ruz_server.repositories import AuditoriumRepository

router = APIRouter(prefix="/auditorium", tags=["auditorium"])

def get_db() -> Generator[Session, None, None]:
    yield from db.get_session()


class AuditoriumRead(BaseModel):
    id: int
    guid: UUID
    name: str
    building: str

    model_config = ConfigDict(from_attributes=True)


class AuditoriumCreate(BaseModel):
    id: int
    guid: UUID
    name: str
    building: str


class AuditoriumUpdate(BaseModel):
    name: Optional[str] | None = None
    building: Optional[str] | None = None


@router.post("/", response_model=AuditoriumRead, status_code=status.HTTP_201_CREATED)
def create_auditorium(
    payload: AuditoriumCreate,
    session: Session = Depends(get_db)
):
    """Create a new Auditorium entity and return the persisted record."""
    repo = AuditoriumRepository(session)
    ensure_entity_doesnot_exist(payload.id, repo.GetById)

    return repo.Create(
        Auditorium(
            id=payload.id,
            guid=payload.guid,
            name=payload.name,
            building=payload.building
        )
    )


@router.get("/", response_model=List[AuditoriumRead])
def list_auditoriums(
    session: Session = Depends(get_db)
):
    """List all Auditorium entities."""
    repo = AuditoriumRepository(session)
    return repo.ListAll()


@router.get("/{auditorium_id}", response_model=AuditoriumRead)
def get_auditorium(
    auditorium_id: int,
    session: Session = Depends(get_db)
):
    """Retrieve a single Auditorium by its numeric identifier."""
    repo = AuditoriumRepository(session)
    return ensure_entity_exists(auditorium_id, repo.GetById)


@router.get("/guid/{auditorium_guid}", response_model=AuditoriumRead)
def get_auditorium_by_guid(
    auditorium_guid: UUID,
    session: Session = Depends(get_db)
):
    """Retrieve a single Auditorium by its GUID."""
    repo = AuditoriumRepository(session)
    return ensure_entity_exists(auditorium_guid, repo.GetByGuid)


@router.put("/{auditorium_id}")
def update_auditorium(
    auditorium_id: int,
    payload: AuditoriumUpdate,
    session: Session = Depends(get_db)
):
    """Update mutable fields of an Auditorium and return the updated entity."""
    repo = AuditoriumRepository(session)
    ensure_entity_exists(auditorium_id, repo.GetById)

    return repo.Update(
        auditorium_id,
        payload.name,
        payload.building
    )


@router.delete("/{auditorium_id}")
def delete_auditorium(
    auditorium_id: int,
    session: Session = Depends(get_db)
):
    """Delete an Auditorium by its identifier."""
    repo = AuditoriumRepository(session)
    ensure_entity_exists(auditorium_id, repo.GetById)

    return repo.Delete(auditorium_id)
