from typing import Generator, List, Optional

from fastapi import APIRouter, Depends, Security, status
from pydantic import BaseModel
from sqlmodel import Session

from api.security import require_api_key
from database import db
from helpers.api_helpers import (ensure_entity_doesnot_exist,
                                 ensure_entity_exists)
from models import Discipline
from repositories import DisciplineRepository

router = APIRouter(prefix="/discipline", tags=["discipline"])

def get_db() -> Generator[Session, None, None]:
    yield from db.get_session()


class DisciplineRead(BaseModel):
    """Read schema for Discipline entity. Mirrors persisted fields for API responses."""
    id: int
    name: str
    examtype: Optional[str] = None
    has_labs: bool = False

    class Config:
        orm_mode = True


class DisciplineCreate(BaseModel):
    """Create schema for Discipline entity. Used to create a new discipline record."""
    id: int
    name: str
    examtype: Optional[str] | None = None
    has_labs: bool | None = False


class DisciplineUpdate(BaseModel):
    """Update schema for Discipline entity. All fields are optional for partial updates."""
    name: Optional[str] | None = None
    examtype: Optional[str] | None = None
    has_labs: Optional[bool] | None = None


@router.post("/", response_model=DisciplineRead, status_code=status.HTTP_201_CREATED)
def create_discipline(
    payload: DisciplineCreate,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """Creates a new discipline using provided payload."""
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
    """Returns a list of all disciplines."""
    repo = DisciplineRepository(session)
    return repo.ListAll()


@router.get("/{discipline_id}", response_model=DisciplineRead)
def get_discipline(
    discipline_id: int,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """Gets a discipline by its identifier."""
    repo = DisciplineRepository(session)
    return ensure_entity_exists(discipline_id, repo.GetById)


@router.put("/{discipline_id}")
def update_discipline(
    discipline_id: int,
    payload: DisciplineUpdate,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """Updates a discipline with provided fields; missing fields remain unchanged."""
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
    """Deletes a discipline by identifier."""
    repo = DisciplineRepository(session)
    ensure_entity_exists(discipline_id, repo.GetById)
    return repo.Delete(discipline_id)
