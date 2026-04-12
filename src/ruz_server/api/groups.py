import logging
from typing import Generator, List, Optional
from uuid import UUID

import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from pydantic import BaseModel, ConfigDict, Field
from sqlmodel import Session

from ruz_server.ruz_api.api import RuzAPI
from ruz_server.ruz_api.group_search import parse_ruz_group_search_response

logger = logging.getLogger(__name__)

from ruz_server.api.security import require_api_key
from ruz_server.database import db
from ruz_server.helpers.api_helpers import (
    ensure_entity_doesnot_exist,
    ensure_entity_exists,
)
from ruz_server.models import Group
from ruz_server.repositories import GroupRepository

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

    model_config = ConfigDict(from_attributes=True)


class GroupCreate(BaseModel):
    """
    Schema for creating a new Group entity.

    This model is used to validate the payload for creating a new group.

    Args:
        id (int): Unique integer identifier for the group (groupOid).
        guid (UUID): Stable UUID identifier for the group (groupGUID).
        name (str): Name of the group (must be unique).
        faculty_name (str): Name of the faculty the group belongs to.
    """

    id: int
    guid: UUID
    name: str
    faculty_name: str


class GroupUpdate(BaseModel):
    """
    Schema for updating an existing Group entity.

    This model is used to validate the payload for updating group information.

    Args:
        name (str): The new name of the group.
        faculty_name (str): The new name of the faculty the group belongs to.
    """

    name: str
    faculty_name: str


class GroupSearchHit(BaseModel):
    """Результат объединённого поиска группы в локальной БД и на ruz.mstuca.ru."""

    oid: int = Field(
        description="Идентификатор группы в RUZ (groupOid), совпадает с Group.id в БД"
    )
    name: str
    guid: UUID
    faculty_name: Optional[str] = Field(
        default=None,
        description="Факультет из локальной БД; для строк только из RUZ — null",
    )


@router.get("/search", response_model=List[GroupSearchHit])
async def search_groups_by_name_db_and_ruz(
    q: str = Query(
        ...,
        min_length=1,
        description="Строка поиска: точное имя группы для выборки из БД (GetByName), подстрока для поиска на ruz.mstuca.ru",
    ),
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key),
):
    """
    Поиск групп по имени одновременно в БД и на ruz.mstuca.ru.

    Сначала возвращаются совпадения из БД (`GetByName` по точному имени), затем дополняются
    уникальные по `oid` результаты из API RUZ (как в `/api/search?type=group`).
    """
    term = q.strip()
    if not term:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Query must not be empty or whitespace-only",
        )

    repo = GroupRepository(session)
    db_groups = repo.GetByName(term)

    seen: set[int] = set()
    out: List[GroupSearchHit] = []

    for g in db_groups:
        seen.add(g.id)
        out.append(
            GroupSearchHit(
                oid=g.id,
                name=g.name,
                guid=g.guid,
                faculty_name=g.faculty_name,
            )
        )

    try:
        raw = await RuzAPI().getGroup(term)
    except aiohttp.ClientError as exc:
        logger.warning("RUZ group search failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to reach ruz.mstuca.ru",
        ) from exc

    if not isinstance(raw, list):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unexpected response from RUZ search",
        )

    for item in parse_ruz_group_search_response(raw):
        if item.oid in seen:
            continue
        seen.add(item.oid)
        out.append(
            GroupSearchHit(
                oid=item.oid,
                name=item.name,
                guid=item.guid,
                faculty_name=None,
            )
        )
    return out


@router.post("/", response_model=GroupRead, status_code=status.HTTP_201_CREATED)
def create_group(
    payload: GroupCreate,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key),
):
    """
    Create a new Group entity.

    This endpoint creates a new group entry in the database with the specified attributes.

    Args:
        payload (GroupCreate): The incoming group data containing id, guid, name, and faculty_name.
        session (Session, optional): The database session dependency.
        _api_key (str, optional): The validated API key for authorization.

    Returns:
        GroupRead: The created group, as read from the database after creation.
    """
    repo = GroupRepository(session)
    ensure_entity_doesnot_exist(payload.id, repo.GetById)
    ensure_entity_doesnot_exist(payload.name, repo.GetByName)

    return repo.Create(
        Group(
            id=payload.id,
            guid=payload.guid,
            name=payload.name,
            faculty_name=payload.faculty_name,
        )
    )


@router.get("/", response_model=List[GroupRead])
def list_groups(
    session: Session = Depends(get_db), _api_key: str = Security(require_api_key)
):
    """
    Retrieves all group entities from the database.

    This endpoint returns a list of all groups available in the database.

    Args:
        session (Session, optional): The database session dependency.
        _api_key (str, optional): The API key for authentication.

    Returns:
        List[GroupRead]: A list containing all groups as GroupRead objects.
    """
    repo = GroupRepository(session)
    return repo.ListAll()


@router.get("/{group_id}", response_model=GroupRead)
def get_group(
    group_id: int,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key),
):
    """
    Retrieve a group entity by its ID.

    Args:
        group_id (int): The unique identifier of the group.
        session (Session, optional): The database session dependency.
        _api_key (str, optional): The API key for authentication.

    Returns:
        GroupRead: The group entity corresponding to the provided group_id.
    """
    repo = GroupRepository(session)
    return ensure_entity_exists(group_id, repo.GetById)


@router.get("/guid/{group_guid}", response_model=GroupRead)
def get_group_by_guid(
    group_guid: UUID,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key),
):
    """
    Retrieve a group entity by its GUID.

    Args:
        group_guid (UUID): The unique GUID of the group.
        session (Session, optional): The database session dependency.
        _api_key (str, optional): The API key for authentication.

    Returns:
        GroupRead: The group entity corresponding to the provided group_guid.
    """
    repo = GroupRepository(session)
    return ensure_entity_exists(group_guid, repo.GetByGUID)


@router.put("/{group_id}")
def update_group(
    group_id: int,
    payload: GroupUpdate,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key),
):
    """
    Update a group entity by its ID.

    Args:
        group_id (int): The unique identifier of the group to update.
        payload (GroupUpdate): The data to update the group with.
        session (Session, optional): The database session dependency.
        _api_key (str, optional): The API key for authentication.

    Returns:
        GroupRead: The updated group entity.
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
    _api_key: str = Security(require_api_key),
):
    """
    Delete a group entity by its ID.

    Args:
        group_id (int): The unique identifier of the group to delete.
        session (Session, optional): The database session dependency.
        _api_key (str, optional): The API key for authentication.

    Returns:
        bool: True if the group was successfully deleted, otherwise raises an error.
    """
    repo = GroupRepository(session)
    ensure_entity_exists(group_id, repo.GetById)

    return repo.Delete(group_id)
