from datetime import datetime
from typing import Generator, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security, status
from pydantic import BaseModel, ConfigDict
from sqlmodel import Session

from api.security import require_api_key
from database import db
from helpers.api_helpers import (ensure_entity_doesnot_exist,
                                 ensure_entity_exists)
from models import Group, User
from repositories import GroupRepository, UserRepository


# Setup logging
import logging
from logging.config import dictConfig
from logging_config import LOGGING_CONFIG, ColoredFormatter

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

root_logger = logging.getLogger()
for handler in root_logger.handlers:
    if type(handler) is logging.StreamHandler:
        handler.setFormatter(ColoredFormatter('%(levelname)s:     %(asctime)s %(name)s - %(message)s'))

router = APIRouter(prefix="/user", tags=["user"])

def get_db() -> Generator[Session, None, None]:
    yield from db.get_session()

class UserRead(BaseModel):
    """Read schema for User entity. Mirrors persisted fields for API responses."""
    id: int
    group_oid: Optional[int] = None
    subgroup: int
    username: str
    created_at: datetime
    last_used_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    """Create schema for User entity. Used to create a new user record."""
    id: int  # Telegram ID
    username: str
    group_oid: int
    subgroup: int = 0
    group_guid: Optional[UUID] | None = None
    group_name: Optional[str] | None = None
    faculty_name: Optional[str] | None = None

class UserUpdate(BaseModel):
    """Update schema for User entity. All fields are optional for partial updates."""
    username: Optional[str] | None = None
    group_oid: Optional[int] | None = None
    subgroup: Optional[int] | None = None
    last_used_at: Optional[datetime] | None = None
    group_guid: Optional[UUID] | None = None
    group_name: Optional[str] | None = None
    faculty_name: Optional[str] | None = None

def _check_payload(payload: UserCreate | UserUpdate) -> None:
    """Validates the given payload and raises a 400 error if any of the essential group
    fields are missing.

    Args:
        payload (UserCreate | UserUpdate): The create or update payload containing
            the group GUID, name, and faculty name.
    """
    if payload.group_guid is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid group GUID"
        )
    if payload.group_name is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid group name"
        )
    if payload.faculty_name is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid faculty name"
        )

def _ensure_group_exists(payload: UserCreate | UserUpdate, session: Session) -> None:
    """Ensures that the group with the given OID exists in the database.

    If the group does not exist, it is created with the given GUID, name, and
    faculty name. If any of the essential group fields are missing (i.e., GUID,
    name, or faculty name), a 400 error is raised. Note that this function does
    not update the group if it already exists; it only creates it if it does not
    exist.

    Args:
        payload (UserCreate | UserUpdate): The create or update payload containing
            the group OID andassociated fields.
        session (Session): The database session to use for the operation.
    """
    group_repo = GroupRepository(session)
    if not group_repo.GetById(payload.group_oid):
        _check_payload(payload)
        group = group_repo.GetOrCreate(
            Group(
                id=payload.group_oid,
                guid=payload.group_guid,
                name=payload.group_name,
                faculty_name=payload.faculty_name
            )
        )

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    session: Session =  Depends(get_db)
):
    repo = UserRepository(session)
    _ensure_group_exists(payload, session)
    ensure_entity_doesnot_exist(payload.id, repo.GetById)

    return repo.Create(
        User(
            id=payload.id,
            username=payload.username,
            group_oid=payload.group_oid,
            subgroup=payload.subgroup
        )
    )

@router.get("/", response_model=List[UserRead])
def list_users(
    session: Session = Depends(get_db)
):
    repo = UserRepository(session)
    return repo.ListAll()

@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    session: Session = Depends(get_db)
):
    repo = UserRepository(session)
    return ensure_entity_exists(user_id, repo.GetById)

@router.get("/guid/{user_guid}", response_model=UserRead)
def get_user_by_username(
    username: str,
    session: Session = Depends(get_db)
):
    repo = UserRepository(session)
    return ensure_entity_exists(username, repo.GetByUsername)

@router.put("/{user_id}")
def update_user(
    user_id: int,
    payload: UserUpdate,
    session: Session = Depends(get_db)
):
    repo = UserRepository(session)
    ensure_entity_exists(user_id, repo.GetById)
    if payload.group_oid:
        _ensure_group_exists(payload, session)

    return repo.Update(
        user_id,
        payload.username,
        payload.group_oid,
        payload.subgroup
    )

@router.put("/last_used_at/{user_guid}")
def update_user_last_used_at(
    user_id: int,
    session: Session = Depends(get_db)
):
    repo = UserRepository(session)
    ensure_entity_exists(user_id, repo.GetById)

    return repo.UpdateLastUsedAt(user_id)

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    session: Session = Depends(get_db)
):
    repo = UserRepository(session)
    ensure_entity_exists(user_id, repo.GetById)

    return repo.Delete(user_id)
