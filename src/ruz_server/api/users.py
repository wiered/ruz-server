# Setup logging
import logging
from collections.abc import Generator
from datetime import datetime
from logging.config import dictConfig
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlmodel import Session

from ruz_server.database import db
from ruz_server.helpers.api_helpers import (
    ensure_entity_doesnot_exist,
    ensure_entity_exists,
)
from ruz_server.logging_config import LOGGING_CONFIG, ColoredFormatter
from ruz_server.models import Group, User
from ruz_server.repositories import GroupRepository, UserRepository

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

root_logger = logging.getLogger()
for handler in root_logger.handlers:
    if type(handler) is logging.StreamHandler:
        handler.setFormatter(
            ColoredFormatter("%(levelname)s:     %(asctime)s %(name)s - %(message)s")
        )

router = APIRouter(prefix="/user", tags=["user"])


def get_db() -> Generator[Session, None, None]:
    yield from db.get_session()


class UserRead(BaseModel):
    """
    Schema for reading User entity data, representing persisted user fields
    used in API responses.

    Args:
        id (int): Unique identifier for the user (typically Telegram ID).
        group_oid (Optional[int]): Identifier for the user's group. Can be None.
        subgroup (Optional[int]): Subgroup number the user belongs to.
        username (str): The username of the user.
        created_at (datetime): Timestamp of when the user record was created.
        last_used_at (datetime): Timestamp of the user's most recent activity.

    Returns:
        UserRead: An instance containing user data for API output.
    """

    id: int
    group_oid: int | None = None
    subgroup: int | None = None
    username: str
    created_at: datetime
    last_used_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    Schema for creating a new user.

    Args:
        id (int): Telegram ID of the user.
        username (str): Username of the user.
        group_oid (int): ID of the user's group.
        subgroup (Optional[int], optional): Subgroup number.
        group_guid (Optional[UUID], optional): Unique identifier for the group.
        group_name (Optional[str], optional): Name of the group.
        faculty_name (Optional[str], optional): Name of the faculty.

    Returns:
        UserCreate: User creation schema instance.
    """

    id: int  # Telegram ID
    username: str
    group_oid: int
    subgroup: int | None = None
    group_guid: UUID | None | None = None
    group_name: str | None | None = None
    faculty_name: str | None | None = None


class UserUpdate(BaseModel):
    """
    Schema for updating User entity. All fields are optional, allowing partial updates.

    Args:
        username (Optional[str]): The username of the user.
        group_oid (Optional[int]): The user's group ID.
        subgroup (Optional[int]): The user's subgroup number.
        last_used_at (Optional[datetime]): The timestamp of last user activity.
        group_guid (Optional[UUID]): Unique group identifier.
        group_name (Optional[str]): Name of the group.
        faculty_name (Optional[str]): Name of the faculty.

    Returns:
        UserUpdate: An instance containing fields to update in the user entity.
    """

    username: str | None | None = None
    group_oid: int | None | None = None
    subgroup: int | None | None = None
    last_used_at: datetime | None | None = None
    group_guid: UUID | None | None = None
    group_name: str | None | None = None
    faculty_name: str | None | None = None


def _validate_subgroup(subgroup: int | None) -> None:
    """
    Validates the subgroup value.

    Args:
        subgroup (Optional[int]): The subgroup number to validate.

    Returns:
        None: Returns nothing if the subgroup is valid.
            Raises an HTTPException if invalid.
    """
    if subgroup is None:
        return
    if subgroup not in {0, 1, 2}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid subgroup"
        )


def _validate_nullable_subgroup_transition(payload: UserUpdate) -> None:
    """Allow ``subgroup=null`` only when the same request also clears ``group_oid``."""
    fields_set = payload.model_fields_set
    if "subgroup" not in fields_set or payload.subgroup is not None:
        return
    if "group_oid" in fields_set and payload.group_oid is None:
        return
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="subgroup can be null only when group_oid is null",
    )


def _check_payload(payload: UserCreate | UserUpdate) -> None:
    """
    Validates essential fields in the payload to ensure data integrity.

    Checks that group_guid, group_name, and faculty_name are not None.
    Raises HTTPException if any of these fields are missing.

    Args:
        payload (UserCreate | UserUpdate): The payload containing user/group information

    Returns:
        None: Returns nothing if all required fields are present.
            Raises an HTTPException if not.
    """
    if payload.group_guid is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid group GUID"
        )
    if payload.group_name is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid group name"
        )
    if payload.faculty_name is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid faculty name"
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
        group_repo.GetOrCreate(
            Group(
                id=payload.group_oid,
                guid=payload.group_guid,
                name=payload.group_name,
                faculty_name=payload.faculty_name,
            )
        )


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, session: Session = Depends(get_db)):
    """
    Create a new user in the system.

    This endpoint allows you to create a user by providing the required user details.
    The function ensures that the user's group exists (creating it if needed) and that
    the user does not already exist before saving the new user to the database.

    Args:
        payload (UserCreate): The data required to create the new user.
        session (Session, optional): The database session dependency.

    Returns:
        UserRead: The created user object as a response model.
    """
    repo = UserRepository(session)
    _validate_subgroup(payload.subgroup)
    _ensure_group_exists(payload, session)
    ensure_entity_doesnot_exist(payload.id, repo.GetById)

    return repo.Create(
        User(
            id=payload.id,
            username=payload.username,
            group_oid=payload.group_oid,
            subgroup=payload.subgroup,
        )
    )


@router.get("/", response_model=list[UserRead])
def list_users(session: Session = Depends(get_db)):
    """
    Retrieve a list of all users in the system.

    Args:
        session (Session): The database session dependency.

    Returns:
        List[UserRead]: A list of user objects in the response model.
    """
    repo = UserRepository(session)
    return repo.ListAll()


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, session: Session = Depends(get_db)):
    """
    Retrieve a user by their unique ID.

    Args:
        user_id (int): The unique identifier of the user to retrieve.
        session (Session): The database session dependency.

    Returns:
        UserRead: The user object corresponding to the given user ID.

    Raises:
        HTTPException: If the user with the specified ID does not exist.
    """
    repo = UserRepository(session)
    return ensure_entity_exists(user_id, repo.GetById)


@router.get("/guid/{user_guid}", response_model=UserRead)
def get_user_by_username(username: str, session: Session = Depends(get_db)):
    """
    Retrieve a user by their unique username.

    Args:
        username (str): The username of the user to retrieve.
        session (Session): The database session dependency.

    Returns:
        UserRead: The user object corresponding to the given username.

    Raises:
        HTTPException: If the user with the specified username does not exist.
    """
    repo = UserRepository(session)
    return ensure_entity_exists(username, repo.GetByUsername)


@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: int, payload: UserUpdate, session: Session = Depends(get_db)):
    """
    Update user information by user ID.

    Args:
        user_id (int): The unique identifier of the user to update.
        payload (UserUpdate): The updated user information.
        session (Session): The database session dependency.

    Returns:
        UserRead: The updated user object if the update is successful.

    Raises:
        HTTPException: If the user does not exist or the update fails.
    """
    repo = UserRepository(session)
    ensure_entity_exists(user_id, repo.GetById)
    _validate_subgroup(payload.subgroup)
    _validate_nullable_subgroup_transition(payload)
    if payload.group_oid is not None:
        _ensure_group_exists(payload, session)

    updated = repo.Update(
        user_id,
        **payload.model_dump(
            exclude_unset=True,
            exclude={"last_used_at", "group_guid", "group_name", "faculty_name"},
        ),
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error: Update Failed",
        )
    return ensure_entity_exists(user_id, repo.GetById)


@router.put("/last_used_at/{user_guid}")
def update_user_last_used_at(user_id: int, session: Session = Depends(get_db)):
    """
    Update the 'last_used_at' timestamp for a user by user ID.

    Args:
        user_id (int): The unique identifier of the user.
        session (Session): The database session dependency.

    Returns:
        Any: The result of updating the 'last_used_at' field for the specified user.
    """
    repo = UserRepository(session)
    ensure_entity_exists(user_id, repo.GetById)

    return repo.UpdateLastUsedAt(user_id)


@router.delete("/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_db)):
    """
    Delete a user entity by its unique identifier.

    Args:
        user_id (int): The unique identifier of the user to delete.
        session (Session): The database session dependency.

    Returns:
        Any: The result of the deletion operation.
    """
    repo = UserRepository(session)
    ensure_entity_exists(user_id, repo.GetById)

    return repo.Delete(user_id)
