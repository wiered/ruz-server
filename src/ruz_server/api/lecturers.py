from collections.abc import Generator
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
from ruz_server.models import Lecturer
from ruz_server.repositories import LecturerRepository

router = APIRouter(prefix="/lecturer", tags=["lecturer"])


def get_db() -> Generator[Session, None, None]:
    yield from db.get_session()


class LecturerRead(BaseModel):
    """
    Schema for reading Lecturer information.

    Attributes:
        id (int): Unique identifier for the lecturer.
        guid (UUID): Universally unique identifier for the lecturer.
        full_name (str): Full name of the lecturer.
        short_name (str): Shortened or preferred name of the lecturer.
        rank (str): Academic or professional rank of the lecturer.
    """

    id: int
    guid: UUID
    full_name: str
    short_name: str
    rank: str

    model_config = ConfigDict(from_attributes=True)


class LecturerCreate(BaseModel):
    """
    Schema for creating a new Lecturer entity.

    Args:
        id (int): Unique identifier for the lecturer.
        guid (UUID): Universally unique identifier for the lecturer.
        full_name (str): Full name of the lecturer.
        short_name (str): Shortened or preferred name of the lecturer.
        rank (str): Academic or professional rank of the lecturer.

    Returns:
        LecturerCreate: Instance representing the new lecturer to be created.
    """

    id: int
    guid: UUID
    full_name: str
    short_name: str
    rank: str


class LecturerUpdate(BaseModel):
    """
    Schema for updating Lecturer information.

    Args:
        full_name (Optional[str] | None): Full name of the lecturer.
            If not provided, it will not be updated.

        short_name (Optional[str] | None): Shortened or preferred name of the lecturer.
            If not provided, it will not be updated.

        rank (Optional[str] | None): Academic or professional rank of the lecturer.
            If not provided, it will not be updated.

    Returns:
        LecturerUpdate: An instance containing the fields to update for the lecturer.
    """

    full_name: str | None | None = None
    short_name: str | None | None = None
    rank: str | None | None = None


@router.post("/", response_model=LecturerRead, status_code=status.HTTP_201_CREATED)
def create_lecturer(
    payload: LecturerCreate,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key),
):
    """
    Create a new lecturer entity in the system.

    Args:
        payload (LecturerCreate): Data required for creating a new lecturer.
        session (Session): Database session dependency.
        _api_key (str): API key for authorization (injected by Security dependency).

    Returns:
        LecturerRead: The created lecturer's data.
    """
    repo = LecturerRepository(session)
    ensure_entity_doesnot_exist(payload.id, repo.GetById)

    return repo.Create(
        Lecturer(
            id=payload.id,
            guid=payload.guid,
            full_name=payload.full_name,
            short_name=payload.short_name,
            rank=payload.rank,
        )
    )


@router.get("/", response_model=list[LecturerRead])
def list_lecturers(
    session: Session = Depends(get_db), _api_key: str = Security(require_api_key)
):
    """
    Retrieve a list of all lecturers.

    Args:
        session (Session): Database session dependency.
        _api_key (str): API key for authorization (injected by Security dependency).

    Returns:
        List[LecturerRead]: A list containing the data for all lecturers.
    """
    repo = LecturerRepository(session)
    return repo.ListAll()


@router.get("/{lecturer_id}", response_model=LecturerRead)
def get_lecturer(
    lecturer_id: int,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key),
):
    """
    Retrieve a lecturer by their ID.

    Args:
        lecturer_id (int): The unique identifier of the lecturer.

    Returns:
        LecturerRead: The data of the lecturer with the specified ID.
    """
    repo = LecturerRepository(session)
    return ensure_entity_exists(lecturer_id, repo.GetById)


@router.get("/guid/{lecturer_guid}", response_model=LecturerRead)
def get_lecturer_by_guid(
    lecturer_guid: UUID,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key),
):
    """
    Retrieve a lecturer by their GUID.

    Args:
        lecturer_guid (UUID): The unique GUID of the lecturer.
        session (Session): Database session dependency.
        _api_key (str): API key for authorization (injected by Security dependency).

    Returns:
        LecturerRead: The data of the lecturer with the specified GUID.
    """
    repo = LecturerRepository(session)
    return ensure_entity_exists(lecturer_guid, repo.GetByGUID)


@router.put("/{lecturer_id}")
def update_lecturer(
    lecturer_id: int,
    payload: LecturerUpdate,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key),
):
    """
    Update an existing lecturer.

    Args:
        lecturer_id (int): The unique identifier of the lecturer to update.
        payload (LecturerUpdate): The updated data for the lecturer.
        session (Session): Database session dependency.
        _api_key (str): API key for authorization (injected by Security dependency).

    Returns:
        LecturerRead: The updated lecturer data.
    """
    repo = LecturerRepository(session)
    ensure_entity_exists(lecturer_id, repo.GetById)

    return repo.Update(lecturer_id, payload.full_name, payload.short_name, payload.rank)


@router.delete("/{lecturer_id}")
def delete_lecturer(
    lecturer_id: int,
    session: Session = Depends(get_db),
    _api_key: str = Security(require_api_key),
):
    """
    Delete an existing lecturer.

    Args:
        lecturer_id (int): The unique identifier of the lecturer to delete.
        session (Session): Database session dependency.
        _api_key (str): API key for authorization (injected by Security dependency).

    Returns:
        Any: The result of the delete operation.
    """
    repo = LecturerRepository(session)
    ensure_entity_exists(lecturer_id, repo.GetById)

    return repo.Delete(lecturer_id)
