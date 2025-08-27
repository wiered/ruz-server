from typing import Generator, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Security, status
from pydantic import BaseModel
from sqlmodel import Session

from api.security import require_api_key
from database import db
from models import User
from repositories import UserRepository

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

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    """Create schema for User entity. Used to create a new user record."""
    id: int  # Telegram ID
    username: str
    group_oid: Optional[int] = None
    subgroup: int = 0


class UserUpdate(BaseModel):
    """Update schema for User entity. All fields are optional for partial updates."""
    username: Optional[str] = None
    group_oid: Optional[int] = None
    subgroup: Optional[int] = None
    last_used_at: Optional[datetime] = None

@router.get("/", response_model=List[UserRead])
def list_users(
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """
    Список всех статей.
    """
    repo = UserRepository(session)
    return repo.ListAll()

@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """
    Получить статью по ID.
    """
    repo = UserRepository(session)
    user = repo.GetById(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/guid/{user_guid}", response_model=UserRead)
def get_user_by_username(
    username: str,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """
    Получить статью по GUID.
    """
    repo = UserRepository(session)
    user = repo.GetByUsername(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    session: Session =  Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """
    Создать новую статью.
    """
    repo = UserRepository(session)
    return repo.GetOrCreate(
        User(
            id=payload.id,
            username=payload.username,
            group_oid=payload.group_oid,
            subgroup=payload.subgroup
        )
    )

@router.put("/{user_id}")
def update_user(
    user_id: int,
    payload: UserUpdate,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """
    Обновить существующую статью.
    """
    repo = UserRepository(session)
    user = repo.GetById(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return repo.Update(
        user_id,
        payload.username,
        payload.group_oid,
        payload.subgroup
    )

@router.put("/last_used_at/{user_guid}")
def update_user_last_used_at(
    user_id: int,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """
    Обновить существующую статью.
    """
    repo = UserRepository(session)
    user = repo.GetById(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return repo.UpdateLastUsedAt(user_id)
