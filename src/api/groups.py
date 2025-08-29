from typing import Generator, List, Optional
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security, status
from pydantic import BaseModel
from sqlmodel import Session

from api.security import require_api_key
from database import db
from models import Group
from repositories import GroupRepository
from helpers.api_helpers import ensure_entity_exists, ensure_entity_doesnot_exist

router = APIRouter(prefix="/group", tags=["group"])

def get_db() -> Generator[Session, None, None]:
    yield from db.get_session()

# Pydantic-схемы

class GroupRead(BaseModel):
    """
    Read-only schema for Group entity.

    This schema is intended for outbound responses (serialization) that expose
    the essential, non-relational fields of the Group table. It mirrors the
    core attributes from the ORM model:
      - id (int): primary key, also known as groupOid.
      - guid (UUID): stable UUID identifier, also known as groupGUID.
      - name (str): unique group name.
      - faculty_name (str): name of the faculty the group belongs to.

    Notes:
    - Relationships (users, lesson_groups, lessons) are intentionally omitted to
      keep the schema lightweight and avoid recursive/n+1 serialization concerns.
    - Enable orm_mode to support constructing this schema directly from ORM/SQLModel instances.
    """

    id: int
    guid: UUID
    name: str
    faculty_name: str

    class Config:
        orm_mode = True

class GroupCreate(BaseModel):
    """
    Create schema for Group entity.

    This schema is intended for inbound requests (deserialization) that expose
    the essential, non-relational fields of the Group table. It mirrors the
    core attributes from the ORM model:
      - id (int): primary key, also known as groupOid.
      - guid (UUID): stable UUID identifier, also known as groupGUID.
      - name (str): unique group name.
      - faculty_name (str): name of the faculty the group belongs to.

    Notes:
    - Relationships (users, lesson_groups, lessons) are intentionally omitted to
      keep the schema lightweight and avoid recursive/n+1 serialization concerns.
    - Enable orm_mode to support constructing this schema directly from ORM/SQLModel instances.
    """

    id: int
    guid: UUID
    name: str
    faculty_name: str

class GroupUpdate(BaseModel):
    """
    Update schema for Group entity.

    This schema is intended for inbound requests (deserialization) that expose
    the essential, non-relational fields of the Group table. It mirrors the
    core attributes from the ORM model:
      - name (str): unique group name.
      - faculty_name (str): name of the faculty the group belongs to.

    Notes:
    - Relationships (users, lesson_groups, lessons) are intentionally omitted to
      keep the schema lightweight and avoid recursive/n+1 serialization concerns.
    - Enable orm_mode to support constructing this schema directly from ORM/SQLModel instances.
    """

    name: str
    faculty_name: str


@router.post("/", response_model=GroupRead, status_code=status.HTTP_201_CREATED)
def create_group(
    payload: GroupCreate,
    session: Session =  Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """
    Создать новую статью.
    """
    repo = GroupRepository(session)
    ensure_entity_doesnot_exist(payload.id, repo.GetById)
    ensure_entity_doesnot_exist(payload.name, repo.GetByName)

    return repo.Create(
        Group(
            id=payload.id,
            guid=payload.guid,
            name=payload.name,
            faculty_name=payload.faculty_name
        )
    )

@router.get("/", response_model=List[GroupRead])
def list_groups(
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """
    Список всех статей.
    """
    repo = GroupRepository(session)
    return repo.ListAll()

@router.get("/{group_id}", response_model=GroupRead)
def get_group(
    group_id: int,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """
    Получить статью по ID.
    """
    repo = GroupRepository(session)
    return ensure_entity_exists(group_id, repo.GetById)

@router.get("/guid/{group_guid}", response_model=GroupRead)
def get_group_by_guid(
    group_guid: UUID,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """
    Получить статью по GUID.
    """
    repo = GroupRepository(session)
    return ensure_entity_exists(group_guid, repo.GetByGUID)

@router.put("/{group_id}")
def update_group(
    group_id: int,
    payload: GroupUpdate,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """
    Обновить существующую статью.
    """
    repo = GroupRepository(session)
    group = ensure_entity_exists(group_id, repo.GetById)
    if payload.name != group.name:
        ensure_entity_doesnot_exist(payload.name, repo.GetByName)

    return repo.Update(group_id, payload.name, payload.faculty_name)

@router.delete("/{group_id}")
def delete_group(
    group_id: int,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key)
):
    """
    Удалить статью по ID.
    """
    repo = GroupRepository(session)
    ensure_entity_exists(group_id, repo.GetById)

    return repo.Delete(group_id)
