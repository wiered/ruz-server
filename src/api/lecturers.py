from typing import Generator, List, Optional
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security, status
from pydantic import BaseModel
from sqlmodel import Session

from api.security import require_api_key
from database import db
from models import Lecturer
from repositories import LecturerRepository
from helpers.api_helpers import ensure_entity_exists, ensure_entity_doesnot_exist

router = APIRouter(prefix="/lecturer", tags=["lecturer"])

def get_db() -> Generator[Session, None, None]:
    yield from db.get_session()


class LecturerRead(BaseModel):
    """Read schema for Lecturer entity. Mirrors persisted fields for API responses."""
    id: int
    guid: UUID
    full_name: str
    short_name: str
    rank: str

    class Config:
        orm_mode = True


class LecturerCreate(BaseModel):
    """Create schema for Lecturer entity. Used to create a new lecturer record."""
    id: int
    guid: UUID
    full_name: str
    short_name: str
    rank: str


class LecturerUpdate(BaseModel):
    """Update schema for Lecturer entity. All fields are optional for partial updates."""
    full_name: Optional[str] | None = None
    short_name: Optional[str] | None = None
    rank: Optional[str] | None = None


@router.post("/", response_model=LecturerRead, status_code=status.HTTP_201_CREATED)
def create_lecturer(
    payload: LecturerCreate,
    session: Session =  Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """
    Создать нового лектора.
    """
    repo = LecturerRepository(session)
    ensure_entity_doesnot_exist(payload.id, repo.GetById)

    return repo.Create(
        Lecturer(
            id=payload.id,
            guid=payload.guid,
            full_name=payload.full_name,
            short_name=payload.short_name,
            rank=payload.rank
        )
    )

@router.get("/", response_model=List[LecturerRead])
def list_lecturers(
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """
    Список всех лекторов.
    """
    repo = LecturerRepository(session)
    return repo.ListAll()

@router.get("/{lecturer_id}", response_model=LecturerRead)
def get_lecturer(
    lecturer_id: int,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """
    Получить лектора по ID.
    """
    repo = LecturerRepository(session)
    return ensure_entity_exists(lecturer_id, repo.GetById)

@router.get("/guid/{lecturer_guid}", response_model=LecturerRead)
def get_lecturer_by_guid(
    lecturer_guid: UUID,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """
    Получить лектора по GUID.
    """
    repo = LecturerRepository(session)
    return ensure_entity_exists(lecturer_guid, repo.GetByGUID)

@router.put("/{lecturer_id}")
def update_lecturer(
    lecturer_id: int,
    payload: LecturerUpdate,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """
    Обновить существующего лектора.
    """
    repo = LecturerRepository(session)
    ensure_entity_exists(lecturer_id, repo.GetById)

    return repo.Update(
        lecturer_id,
        payload.full_name,
        payload.short_name,
        payload.rank
        )

@router.delete("/{lecturer_id}")
def delete_lecturer(
    lecturer_id: int,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """
    Удалить существующего лектора.
    """
    repo = LecturerRepository(session)
    ensure_entity_exists(lecturer_id, repo.GetById)

    return repo.Delete(lecturer_id)
