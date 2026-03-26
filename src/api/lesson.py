import logging
from datetime import time, date
from datetime import date as datetime_date
from datetime import datetime as dt
from typing import Generator, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Security, status
from pydantic import BaseModel, ConfigDict
from sqlmodel import Session

from api.security import require_api_key
from database import db
from helpers.api_helpers import (create_if_not_exists,
                                 ensure_entity_doesnot_exist,
                                 ensure_entity_exists, is_entity_exists)
from models import *
from repositories import *
from ruz_api import RuzAPI

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/lesson", tags=["lesson"])

def get_db() -> Generator[Session, None, None]:
    yield from db.get_session()

EXAM_TYPES = ["Зачёт", "Экзамен"]


class LessonRead(BaseModel):
    """Read schema for Lesson entity. Mirrors persisted fields for API responses."""
    id: int
    kind_of_work_id: int
    discipline_id: int
    auditorium_id: int
    lecturer_id: int
    date: date
    begin_lesson: time
    end_lesson: time
    updated_at: dt
    sub_group: int

    model_config = ConfigDict(from_attributes=True)


class LessonCreate(BaseModel):
    """Create schema for Lesson entity. Used to create a new lesson record."""
    id: int # lessonOid
    lecturer_id: int
    lecturer_guid: UUID
    lecturer_full_name: str
    lecturer_short_name: str
    lecturer_rank: str

    kind_of_work_id: int
    type_of_work: str
    complexity: int

    discipline_id: int # disciplineOid
    discipline_name: str

    auditorium_id: int
    auditorium_guid: UUID
    auditorium_name: str
    auditorium_building: str

    date: date
    begin_lesson: time
    end_lesson: time

    group_id: int
    sub_group: int = 0


class LessonUpdate(BaseModel):
    """Update schema for Lesson entity. All fields are optional for partial updates."""
    kind_of_work_id: Optional[int] | None = None
    discipline_id: Optional[int] | None = None
    auditorium_id: Optional[int] | None = None
    lecturer_id: Optional[int] | None = None
    date: Optional[datetime_date] | None = None
    begin_lesson: Optional[time] | None = None
    end_lesson: Optional[time] | None = None
    sub_group: Optional[int] | None = None
    updated_at: Optional[dt] | None = None


def _set_has_labs_and_examtype(payload: LessonCreate, session: Session):
    discipline_repository = DisciplineRepository(session)
    discipline = discipline_repository.GetById(payload.discipline_id)

    has_labs = discipline.has_labs
    examtype = discipline.examtype
    is_changed = False

    if not has_labs and payload.type_of_work == "Лабораторная работа":
        has_labs = True
        is_changed = True

    if examtype == "Неизв." and payload.type_of_work in EXAM_TYPES:
        examtype = payload.type_of_work
        is_changed = True

    if is_changed:
        discipline_repository.Update(
            payload.discipline_id,
            name=discipline.name,
            examtype=examtype,
            has_labs=has_labs
        )

@router.post("/", response_model=LessonRead, status_code=status.HTTP_201_CREATED)
def create_lesson(
    payload: LessonCreate,
    session: Session = Depends(get_db)
):
    """Create a new Lesson entity and return the persisted record."""
    repo = LessonRepository(session)
    ensure_entity_doesnot_exist(payload.id, repo.GetById)

    lecturer_repository = LecturerRepository(session)
    create_if_not_exists(
        lecturer_repository,
        payload.lecturer_id,
        lecturer_repository.GetById,
        dict(
            id=payload.lecturer_id,
            guid=payload.lecturer_guid,
            full_name=payload.lecturer_full_name,
            short_name=payload.lecturer_short_name,
            rank=payload.lecturer_rank
        )
    )

    kind_of_work_repository = KindOfWorkRepository(session)
    create_if_not_exists(
        kind_of_work_repository,
        payload.kind_of_work_id,
        kind_of_work_repository.GetById,
        dict(
            id=payload.kind_of_work_id,
            type_of_work=payload.type_of_work,
            complexity=payload.complexity
        )
    )

    discipline_repository = DisciplineRepository(session)
    create_if_not_exists(
        discipline_repository,
        payload.discipline_id,
        discipline_repository.GetById,
        dict(
            id=payload.discipline_id,
            name=payload.discipline_name,
            examtype="Неизв.",
            has_labs=False
        )
    )
    _set_has_labs_and_examtype(payload, session)

    auditorium_repository = AuditoriumRepository(session)
    create_if_not_exists(
        auditorium_repository,
        payload.auditorium_id,
        auditorium_repository.GetById,
        dict(
            id=payload.auditorium_id,
            guid=payload.auditorium_guid,
            name=payload.auditorium_name,
            building=payload.auditorium_building
        )
    )

    return repo.Create(
        Lesson(
            kind_of_work_id=payload.kind_of_work_id,
            discipline_id=payload.discipline_id,
            auditorium_id=payload.auditorium_id,
            lecturer_id=payload.lecturer_id,
            date=payload.date,
            begin_lesson=payload.begin_lesson,
            end_lesson=payload.end_lesson,
            sub_group=payload.sub_group,
        )
    )

@router.put("/parse")
def parse_lessons(
    session: Session = Depends(get_db)
):
    repo = LessonRepository(session)
    group_repository = GroupRepository(session)
    groups = group_repository.ListAll()

    for group in groups:
        lessons = RuzAPI.getSchedule(group.id)
        logger.debug(f"parsed {len(lessons)} lessons for group {group.id}")
        logger.debug(f"{lessons}")
        # repo.BulkSaveLessons(lessons)


@router.get("/", response_model=List[LessonRead])
def list_lessons(
    session: Session = Depends(get_db)
):
    """List all Lesson entities."""
    repo = LessonRepository(session)
    return repo.ListAll()


@router.get("/{lesson_id}", response_model=LessonRead)
def get_lesson(
    lesson_id: int,
    session: Session = Depends(get_db)
):
    """Retrieve a single Lesson by its numeric identifier."""
    repo = LessonRepository(session)
    return ensure_entity_exists(lesson_id, repo.GetById)


@router.put("/{lesson_id}", response_model=LessonRead)
def update_lesson(
    lesson_id: int,
    payload: LessonUpdate,
    session: Session = Depends(get_db)
):
    """Update mutable fields of a Lesson and return the updated entity."""
    repo = LessonRepository(session)
    ensure_entity_exists(lesson_id, repo.GetById)

    repo.Update(
        lesson_id,
        payload.kind_of_work_id,
        payload.discipline_id,
        payload.auditorium_id,
        payload.lecturer_id,
        payload.date,
        payload.begin_lesson,
        payload.end_lesson,
        payload.sub_group
    )
    return ensure_entity_exists(lesson_id, repo.GetById)


@router.delete("/{lesson_id}")
def delete_lesson(
    lesson_id: int,
    session: Session = Depends(get_db)
):
    """Delete a Lesson by its identifier."""
    repo = LessonRepository(session)
    ensure_entity_exists(lesson_id, repo.GetById)

    return repo.Delete(lesson_id)
