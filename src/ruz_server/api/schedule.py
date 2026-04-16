import datetime
from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlmodel import Session

from ruz_server.database import db
from ruz_server.helpers.api_helpers import ensure_entity_exists
from ruz_server.models import Lesson
from ruz_server.repositories import GroupRepository, LessonRepository, UserRepository

router = APIRouter(prefix="/schedule", tags=["schedule"])


def get_db() -> Generator[Session, None, None]:
    yield from db.get_session()


class UserScheduleLessonRead(BaseModel):
    """
    Data model for a user's schedule lesson.

    Represents the relevant lesson information in a user's schedule.

    Attributes:
        lesson_id (int): The unique identifier of the lesson.
        date (datetime.date): The date the lesson takes place.
        begin_lesson (datetime.time): Time when the lesson begins.
        end_lesson (datetime.time): Time when the lesson ends.
        sub_group (int): The subgroup associated with the lesson.
        discipline_name (str): Name of the discipline.
        kind_of_work (str): Type of work or lesson (e.g., lecture, practice).
        lecturer_short_name (str): Short name of the lecturer.
        lecturer_id (int): ID преподавателя.
        discipline_id (int): ID дисциплины.
        auditorium_name (str): Name of the auditorium.
        building (str): Building where the lesson is held.
        group_id (int): Group identifier associated with the lesson.
    """

    lesson_id: int
    date: datetime.date
    begin_lesson: datetime.time
    end_lesson: datetime.time
    sub_group: int
    discipline_name: str
    kind_of_work: str
    lecturer_short_name: str
    lecturer_id: int
    discipline_id: int
    auditorium_name: str
    building: str
    group_id: int


def get_week_range(anchor_date: datetime.date) -> tuple[datetime.date, datetime.date]:
    """
    Calculate the start (Monday) and end (Sunday) dates of the week for a given date.

    Args:
        anchor_date (datetime.date): The reference date
            for which the week range is calculated.

    Returns:
        tuple[datetime.date, datetime.date]: A tuple containing the Monday (start)
            and Sunday (end) dates of the week.
    """
    start = anchor_date - datetime.timedelta(days=anchor_date.weekday())
    end = start + datetime.timedelta(days=6)
    return start, end


def map_lesson_to_schedule_dto(
    lesson: Lesson,
    group_id: int | None = None,
) -> UserScheduleLessonRead:
    """
    Resolves the group ID for the lesson mapping.

    Args:
        group_id (int | None): The group identifier to use,
            or None if it should be determined.

    Returns:
        int | None: The resolved group identifier value.
    """
    resolved_group_id = group_id
    if resolved_group_id is None:
        resolved_group_id = (
            lesson.lesson_groups[0].group_id if lesson.lesson_groups else 0
        )

    return UserScheduleLessonRead(
        lesson_id=lesson.id,
        date=lesson.date,
        begin_lesson=lesson.begin_lesson,
        end_lesson=lesson.end_lesson,
        sub_group=lesson.sub_group,
        discipline_name=(lesson.discipline.name if lesson.discipline else ""),
        kind_of_work=(lesson.kind_of_work.type_of_work if lesson.kind_of_work else ""),
        lecturer_short_name=(lesson.lecturer.short_name if lesson.lecturer else ""),
        lecturer_id=lesson.lecturer_id,
        discipline_id=lesson.discipline_id,
        auditorium_name=(lesson.auditorium.name if lesson.auditorium else ""),
        building=(lesson.auditorium.building if lesson.auditorium else ""),
        group_id=resolved_group_id,
    )


def _get_user_group_and_subgroup(user_id: int, session: Session) -> tuple[int, int]:
    """
    Retrieves the user's group and subgroup by user ID.

    Args:
        user_id (int): The ID of the user.
        session (Session): The database session.

    Returns:
        tuple[int, int]: The group ID and the subgroup number of the user.

    Raises:
        HTTPException: If user is not found or user has no group assigned.
    """
    user_repo = UserRepository(session)
    user = user_repo.GetById(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error: Not Found",
        )
    if user.group_oid is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no group assigned",
        )
    if user.subgroup is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no subgroup assigned",
        )
    return user.group_oid, user.subgroup


@router.get("/user/{user_id}/day", response_model=list[UserScheduleLessonRead])
def get_user_schedule_day(
    user_id: int,
    date: datetime.date = Query(...),
    session: Session = Depends(get_db),
):
    """
    Retrieves the lesson schedule for a specific user on a given day.

    Args:
        user_id (int): The ID of the user whose schedule is requested.
        date (datetime.date): The date for which the schedule is requested.
        session (Session): The database session dependency.

    Returns:
        List[UserScheduleLessonRead]: A list of schedule lesson data
            for the user on the specified day.
    """
    group_id, subgroup = _get_user_group_and_subgroup(user_id, session)
    lesson_repo = LessonRepository(session)
    lessons = lesson_repo.ListForUserByDateRange(
        group_id=group_id,
        subgroup=subgroup,
        start=date,
        end=date,
    )
    return [map_lesson_to_schedule_dto(lesson, group_id) for lesson in lessons]


@router.get("/user/{user_id}/week", response_model=list[UserScheduleLessonRead])
def get_user_schedule_week(
    user_id: int,
    date: datetime.date = Query(...),
    session: Session = Depends(get_db),
):
    """
    Retrieves the weekly lesson schedule for a specific user.

    Args:
        user_id (int): The ID of the user whose schedule is requested.
        date (datetime.date): The date used to determine the week range.
        session (Session): The database session dependency.

    Returns:
        List[UserScheduleLessonRead]: A list of schedule lesson data for
            the user for the specified week.
    """
    group_id, subgroup = _get_user_group_and_subgroup(user_id, session)
    start, end = get_week_range(date)
    lesson_repo = LessonRepository(session)
    lessons = lesson_repo.ListForUserByDateRange(
        group_id=group_id,
        subgroup=subgroup,
        start=start,
        end=end,
    )
    return [map_lesson_to_schedule_dto(lesson, group_id) for lesson in lessons]


@router.get("/group/{group_id}/week", response_model=list[UserScheduleLessonRead])
def get_group_schedule_week(
    group_id: int,
    date: datetime.date = Query(...),
    session: Session = Depends(get_db),
):
    """
    Weekly schedule for a student group, including every lesson subgroup.

    Uses the same week bounds as ``/schedule/user/{user_id}/week`` (Mon–Sun).
    ``subgroup=0`` semantics from ``ListForUserByDateRange``: all ``Lesson.sub_group``
    values linked to this group are returned.

    Args:
        group_id (int): Group identifier (``Group.id`` / RUZ groupOid).
        date (datetime.date): Anchor date inside the target week.
        session (Session): Database session.

    Returns:
        list[UserScheduleLessonRead]: Lessons for the group for that week.

    Raises:
        HTTPException: 404 if the group does not exist.
    """
    group_repo = GroupRepository(session)
    ensure_entity_exists(group_id, group_repo.GetById)
    start, end = get_week_range(date)
    lesson_repo = LessonRepository(session)
    lessons = lesson_repo.ListForUserByDateRange(
        group_id=group_id,
        subgroup=0,
        start=start,
        end=end,
    )
    return [map_lesson_to_schedule_dto(lesson, group_id) for lesson in lessons]
