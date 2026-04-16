import logging
from collections.abc import Generator
from datetime import date, time
from datetime import date as datetime_date
from datetime import datetime as dt
from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict
from sqlmodel import Session

from ruz_server.database import db
from ruz_server.helpers.api_helpers import (
    create_if_not_exists,
    ensure_entity_doesnot_exist,
    ensure_entity_exists,
)
from ruz_server.models import (
    Auditorium,
    Discipline,
    KindOfWork,
    Lecturer,
    Lesson,
)
from ruz_server.repositories import (
    AuditoriumRepository,
    DisciplineRepository,
    KindOfWorkRepository,
    LecturerRepository,
    LessonRepository,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/lesson", tags=["lesson"])


def get_db() -> Generator[Session, None, None]:
    yield from db.get_session()


EXAM_TYPES = ["Зачёт", "Экзамен"]


class LessonRead(BaseModel):
    """
    Represents the schema for reading a Lesson entity.

    Args:
        id (int): Unique identifier for the lesson.
        kind_of_work_id (int): Identifier for the type of work (e.g., lecture, seminar).
        discipline_id (int): Identifier for the discipline.
        auditorium_id (int): Identifier for the auditorium.
        lecturer_id (int): Identifier for the lecturer.
        date (date): Date of the lesson.
        begin_lesson (time): Start time of the lesson.
        end_lesson (time): End time of the lesson.
        updated_at (datetime): Timestamp of the last update.
        sub_group (int): Subgroup number.

    Returns:
        LessonRead: Lesson data suitable for API responses.
    """

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
    """
    Schema for creating a Lesson entity.

    Args:
        id (int): Unique lesson identifier (lessonOid).
        lecturer_id (int): Identifier of the lecturer.
        lecturer_guid (UUID): GUID of the lecturer.
        lecturer_full_name (str): Full name of the lecturer.
        lecturer_short_name (str): Short name of the lecturer.
        lecturer_rank (str): Academic rank or title of the lecturer.
        kind_of_work_id (int): Identifier for the type of work (e.g., lecture, seminar).
        type_of_work (str): Description of the type of academic work.
        complexity (int): Difficulty or complexity level.
        discipline_id (int): Identifier for the discipline (disciplineOid).
        discipline_name (str): Name of the discipline.
        auditorium_id (int): Identifier for the auditorium.
        auditorium_guid (UUID): GUID of the auditorium.
        auditorium_name (str): Name of the auditorium.
        auditorium_building (str): Building location of the auditorium.
        date (date): Date of the lesson.
        begin_lesson (time): Start time of the lesson.
        end_lesson (time): End time of the lesson.
        group_id (int): Identifier for the group.
        sub_group (int, optional): Subgroup number, default is 0.

    Returns:
        LessonCreate: Data structure for creating a new lesson record.
    """

    id: int  # lessonOid
    lecturer_id: int
    lecturer_guid: UUID
    lecturer_full_name: str
    lecturer_short_name: str
    lecturer_rank: str

    kind_of_work_id: int
    type_of_work: str
    complexity: int

    discipline_id: int  # disciplineOid
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
    """
    Schema for updating the Lesson entity. All fields are optional
    to allow partial updates.

    Args:
        kind_of_work_id (Optional[int]): Identifier for the type of work .
        discipline_id (Optional[int]): Identifier for the discipline.
        auditorium_id (Optional[int]): Identifier for the auditorium.
        lecturer_id (Optional[int]): Identifier for the lecturer.
        date (Optional[datetime_date]): Date of the lesson.
        begin_lesson (Optional[time]): Start time of the lesson.
        end_lesson (Optional[time]): End time of the lesson.
        sub_group (Optional[int]): Subgroup number.
        updated_at (Optional[dt]): Timestamp when the lesson was last updated.

    Returns:
        LessonUpdate: An object containing the fields to update in the Lesson entity.
    """

    kind_of_work_id: int | None = None
    discipline_id: int | None = None
    auditorium_id: int | None = None
    lecturer_id: int | None = None
    date: datetime_date | None | None = None
    begin_lesson: time | None | None = None
    end_lesson: time | None | None = None
    sub_group: int | None = None
    updated_at: dt | None | None = None


def _set_has_labs_and_examtype(payload: LessonCreate, session: Session):
    """
    Sets the 'has_labs' and 'examtype' attributes of a Discipline entity
    based on the LessonCreate payload.

    This helper function ensures the referenced discipline's 'has_labs' and 'examtype'
    values are correctly updated if the lesson being created implies a new lab type
    or an examination type. If such changes occur,
    it persists them using the DisciplineRepository.

    Args:
        payload (LessonCreate): The data used to create the lesson,
            containing discipline and type of work info.
        session (Session): The current active database session.

    Returns:
        None
    """
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
            has_labs=has_labs,
        )


def _upsert_reference_entities(payload: LessonCreate, session: Session) -> None:
    """
    Upserts (inserts or updates) reference entities
    (Lecturer, KindOfWork, Discipline, Auditorium)
    as required by the LessonCreate payload.

    This helper checks for the existence of related entities required by a new lesson.
    If any referenced entity does not exist in the database, it inserts it with the
    supplied attributes. If it already exists, it updates its fields with the
    information from the payload. This ensures all references are present and
    up-to-date before lesson creation.

    Args:
        payload (LessonCreate): The information needed to create the lesson,
            including attributes for related entities.
        session (Session): The active database session used for upsert operations.

    Returns:
        None
    """
    lecturer = session.get(Lecturer, payload.lecturer_id)
    if lecturer is None:
        session.add(
            Lecturer(
                id=payload.lecturer_id,
                guid=payload.lecturer_guid,
                full_name=payload.lecturer_full_name,
                short_name=payload.lecturer_short_name,
                rank=payload.lecturer_rank,
            )
        )
    else:
        lecturer.guid = payload.lecturer_guid
        lecturer.full_name = payload.lecturer_full_name
        lecturer.short_name = payload.lecturer_short_name
        lecturer.rank = payload.lecturer_rank
        session.add(lecturer)

    kind_of_work = session.get(KindOfWork, payload.kind_of_work_id)
    if kind_of_work is None:
        session.add(
            KindOfWork(
                id=payload.kind_of_work_id,
                type_of_work=payload.type_of_work,
                complexity=payload.complexity,
            )
        )
    else:
        kind_of_work.type_of_work = payload.type_of_work
        kind_of_work.complexity = payload.complexity
        session.add(kind_of_work)

    discipline = session.get(Discipline, payload.discipline_id)
    if discipline is None:
        session.add(
            Discipline(
                id=payload.discipline_id,
                name=payload.discipline_name,
                examtype="Неизв.",
                has_labs=False,
            )
        )
    else:
        discipline.name = payload.discipline_name
        session.add(discipline)

    auditorium = session.get(Auditorium, payload.auditorium_id)
    if auditorium is None:
        session.add(
            Auditorium(
                id=payload.auditorium_id,
                guid=payload.auditorium_guid,
                name=payload.auditorium_name,
                building=payload.auditorium_building,
            )
        )
    else:
        auditorium.guid = payload.auditorium_guid
        auditorium.name = payload.auditorium_name
        auditorium.building = payload.auditorium_building
        session.add(auditorium)

    discipline = session.get(Discipline, payload.discipline_id)
    if discipline is not None:
        has_labs = discipline.has_labs
        examtype = discipline.examtype
        if not has_labs and payload.type_of_work == "Лабораторная работа":
            discipline.has_labs = True
        if (
            examtype == "Неизв." or examtype is None
        ) and payload.type_of_work in EXAM_TYPES:
            discipline.examtype = payload.type_of_work
        session.add(discipline)


def _create_lesson_with_relations(
    payload: LessonCreate, session: Session, skip_if_exists: bool = False
) -> tuple[Lesson, bool]:
    """
    Creates a lesson entity along with all required related entities
    if they do not exist.

    Args:
        payload (LessonCreate): The data required to create the lesson
            and its related entities.
        session (Session): The database session used for entity operations.
        skip_if_exists (bool, optional): If True and the lesson exists, skip creation.

    Returns:
        tuple[Lesson, bool]: A tuple containing the lesson instance and a bool indicating
            if creation occurred (True if created, False if already existing).
    """  # noqa: E501
    repo = LessonRepository(session)
    existing = repo.GetById(payload.id)
    if existing:
        if skip_if_exists:
            return existing, False
        ensure_entity_doesnot_exist(payload.id, repo.GetById)

    lecturer_repository = LecturerRepository(session)
    create_if_not_exists(
        lecturer_repository,
        payload.lecturer_id,
        lecturer_repository.GetById,
        Lecturer(
            id=payload.lecturer_id,
            guid=payload.lecturer_guid,
            full_name=payload.lecturer_full_name,
            short_name=payload.lecturer_short_name,
            rank=payload.lecturer_rank,
        ),
    )

    kind_of_work_repository = KindOfWorkRepository(session)
    create_if_not_exists(
        kind_of_work_repository,
        payload.kind_of_work_id,
        kind_of_work_repository.GetById,
        KindOfWork(
            id=payload.kind_of_work_id,
            type_of_work=payload.type_of_work,
            complexity=payload.complexity,
        ),
    )

    discipline_repository = DisciplineRepository(session)
    create_if_not_exists(
        discipline_repository,
        payload.discipline_id,
        discipline_repository.GetById,
        Discipline(
            id=payload.discipline_id,
            name=payload.discipline_name,
            examtype="Неизв.",
            has_labs=False,
        ),
    )
    _set_has_labs_and_examtype(payload, session)

    auditorium_repository = AuditoriumRepository(session)
    create_if_not_exists(
        auditorium_repository,
        payload.auditorium_id,
        auditorium_repository.GetById,
        Auditorium(
            id=payload.auditorium_id,
            guid=payload.auditorium_guid,
            name=payload.auditorium_name,
            building=payload.auditorium_building,
        ),
    )

    created = repo.Create(
        Lesson(
            id=payload.id,
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
    return created, True


@router.post("/", response_model=LessonRead, status_code=status.HTTP_201_CREATED)
def create_lesson(payload: LessonCreate, session: Session = Depends(get_db)):
    """
    Creates a new Lesson entity and returns the persisted record.

    Args:
        payload (LessonCreate): The data required to create the Lesson entity.
        session (Session, optional): The database session dependency.

    Returns:
        LessonRead: The created Lesson record as a response model.
    """
    lesson, _ = _create_lesson_with_relations(payload, session)
    return lesson


@router.put("/parse")
async def parse_lessons(session: Session = Depends(get_db)):
    """
    Parse lessons using the refresh scheduler.

    Args:
        session (Session): Database session dependency.

    Returns:
        Any: The result of running the refresh process
            with the provided database session.
    """
    from ruz_server.services.refresh_scheduler import run_refresh_with_session

    return await run_refresh_with_session(session=session, source="api")


@router.get("/", response_model=list[LessonRead])
def list_lessons(session: Session = Depends(get_db)):
    """
    Retrieve a list of all Lesson entities.

    Args:
        session (Session): Database session dependency.

    Returns:
        List[LessonRead]: List of all lesson entities in the database.
    """
    repo = LessonRepository(session)
    return repo.ListAll()


@router.get("/{lesson_id}", response_model=LessonRead)
def get_lesson(lesson_id: int, session: Session = Depends(get_db)):
    """
    Retrieve a single Lesson by its numeric identifier.

    Args:
        lesson_id (int): Numeric identifier of the lesson to retrieve.
        session (Session): Database session dependency.

    Returns:
        LessonRead: The requested lesson entity if it exists.

    """
    repo = LessonRepository(session)
    return ensure_entity_exists(lesson_id, repo.GetById)


@router.put("/{lesson_id}", response_model=LessonRead)
def update_lesson(
    lesson_id: int, payload: LessonUpdate, session: Session = Depends(get_db)
):
    """
    Update the mutable fields of a Lesson entity and return the updated lesson.

    Args:
        lesson_id (int): The unique identifier of the lesson to update.
        payload (LessonUpdate): Data containing updated fields for the lesson.
        session (Session): Database session dependency.

    Returns:
        LessonRead: The updated lesson entity.
    """
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
        payload.sub_group,
    )
    return ensure_entity_exists(lesson_id, repo.GetById)


@router.delete("/{lesson_id}")
def delete_lesson(lesson_id: int, session: Session = Depends(get_db)):
    """
    Delete a lesson entity by its unique identifier.

    Args:
        lesson_id (int): The unique identifier of the lesson to delete.
        session (Session): Database session dependency.

    Returns:
        Any: The result of the deletion operation.
    """
    repo = LessonRepository(session)
    ensure_entity_exists(lesson_id, repo.GetById)

    return repo.Delete(lesson_id)
