import datetime
from typing import Generator, List, Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from ruz_server.api.schedule import (
    UserScheduleLessonRead,
    get_week_range,
    map_lesson_to_schedule_dto,
)
from ruz_server.database import db
from ruz_server.repositories import LessonRepository

router = APIRouter(prefix="/search", tags=["search"])


def get_db() -> Generator[Session, None, None]:
    yield from db.get_session()


@router.get("/lecturer/day", response_model=List[UserScheduleLessonRead])
def search_lecturer_day(
    lecturer_id: int = Query(...),
    date: datetime.date = Query(...),
    group_id: Optional[int] = Query(None),
    sub_group: Optional[int] = Query(None),
    session: Session = Depends(get_db),
):
    """
    Search for lessons scheduled for a specific lecturer on a given day.

    Args:
        lecturer_id (int): The unique identifier of the lecturer.
        date (datetime.date): The specific date to search lessons for.
        group_id (Optional[int]): The optional group identifier to filter lessons (default: None).
        sub_group (Optional[int]): The optional subgroup identifier to filter lessons (default: None).
        session (Session): The database session dependency.

    Returns:
        List[UserScheduleLessonRead]: List of lessons matching the criteria, formatted for user schedule output.
    """
    repo = LessonRepository(session)
    lessons = repo.ListByLecturerAndDate(
        lecturer_id=lecturer_id,
        value=date,
        group_id=group_id,
        sub_group=sub_group,
    )
    return [map_lesson_to_schedule_dto(lesson, group_id) for lesson in lessons]


@router.get("/lecturer/week", response_model=List[UserScheduleLessonRead])
def search_lecturer_week(
    lecturer_id: int = Query(...),
    date: datetime.date = Query(...),
    group_id: Optional[int] = Query(None),
    sub_group: Optional[int] = Query(None),
    session: Session = Depends(get_db),
):
    """
    Search for lessons scheduled for a specific lecturer during a given week.

    Args:
        lecturer_id (int): The unique identifier of the lecturer.
        date (datetime.date): The specific date for which to determine the week range.
        group_id (Optional[int]): The optional group identifier to filter lessons (default: None).
        sub_group (Optional[int]): The optional subgroup identifier to filter lessons (default: None).
        session (Session): The database session dependency.

    Returns:
        List[UserScheduleLessonRead]: List of lessons matching the criteria, formatted for user schedule output.
    """
    start, end = get_week_range(date)
    repo = LessonRepository(session)
    lessons = repo.ListByLecturerAndDateRange(
        lecturer_id=lecturer_id,
        start=start,
        end=end,
        group_id=group_id,
        sub_group=sub_group,
    )
    return [map_lesson_to_schedule_dto(lesson, group_id) for lesson in lessons]


@router.get("/discipline/day", response_model=List[UserScheduleLessonRead])
def search_discipline_day(
    discipline_id: int = Query(...),
    date: datetime.date = Query(...),
    group_id: Optional[int] = Query(None),
    sub_group: Optional[int] = Query(None),
    session: Session = Depends(get_db),
):
    """
    Search for lessons scheduled for a specific discipline on a particular day.

    Args:
        discipline_id (int): The unique identifier of the discipline.
        date (datetime.date): The specific day to filter lessons.
        group_id (Optional[int]): The optional group identifier to filter lessons (default: None).
        sub_group (Optional[int]): The optional subgroup identifier to filter lessons (default: None).
        session (Session): The database session dependency.

    Returns:
        List[UserScheduleLessonRead]: List of lessons matching the criteria, formatted for user schedule output.
    """
    repo = LessonRepository(session)
    lessons = repo.ListByDisciplineAndDate(
        discipline_id=discipline_id,
        value=date,
        group_id=group_id,
        sub_group=sub_group,
    )
    return [map_lesson_to_schedule_dto(lesson, group_id) for lesson in lessons]


@router.get("/discipline/week", response_model=List[UserScheduleLessonRead])
def search_discipline_week(
    discipline_id: int = Query(...),
    date: datetime.date = Query(...),
    group_id: Optional[int] = Query(None),
    sub_group: Optional[int] = Query(None),
    session: Session = Depends(get_db),
):
    """
    Search for lessons scheduled for a specific discipline during the week of the given date.

    Args:
        discipline_id (int): The unique identifier of the discipline.
        date (datetime.date): The date for which the week is calculated.
        group_id (Optional[int]): The optional group identifier to filter lessons (default: None).
        sub_group (Optional[int]): The optional subgroup identifier to filter lessons (default: None).
        session (Session): The database session dependency.

    Returns:
        List[UserScheduleLessonRead]: List of lessons matching the criteria, formatted for user schedule output.
    """
    start, end = get_week_range(date)
    repo = LessonRepository(session)
    lessons = repo.ListByDisciplineAndDateRange(
        discipline_id=discipline_id,
        start=start,
        end=end,
        group_id=group_id,
        sub_group=sub_group,
    )
    return [map_lesson_to_schedule_dto(lesson, group_id) for lesson in lessons]
