import datetime
import logging
from typing import Generator, List, Optional
from uuid import UUID

import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlmodel import Session

from ruz_server.ruz_api.api import RuzAPI

logger = logging.getLogger(__name__)

from ruz_server.api.schedule import (
    UserScheduleLessonRead,
    get_week_range,
    map_lesson_to_schedule_dto,
)
from ruz_server.database import db
from ruz_server.repositories import LessonRepository

router = APIRouter(prefix="/search", tags=["search"])


class RuzGroupSearchItem(BaseModel):
    """Одна группа из ответа поиска ruz.mstuca.ru (`/api/search?type=group`)."""

    id: int = Field(description="Идентификатор группы в RUZ (groupOid)")
    name: str = Field(description="Отображаемое имя группы")
    guid: UUID = Field(description="GUID группы в RUZ")


def get_db() -> Generator[Session, None, None]:
    yield from db.get_session()


@router.get("/group", response_model=List[RuzGroupSearchItem])
async def search_groups_by_name_ruz(
    q: str = Query(
        ...,
        min_length=1,
        description="Подстрока имени группы, например «ИС22»",
    ),
):
    """
    Поиск групп по имени через API ruz.mstuca.ru (прокси к `/api/search?type=group`).

    Клиент передаёт строку запроса; сервер обращается к расписанию МГТУ СТА и возвращает
    подходящие группы с id и guid для дальнейших запросов расписания.
    """
    term = q.strip()
    if not term:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Query must not be empty or whitespace-only",
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

    items: List[RuzGroupSearchItem] = []
    for row in raw:
        if not isinstance(row, dict):
            continue
        try:
            items.append(
                RuzGroupSearchItem(
                    id=int(row["id"]),
                    name=str(row["label"]),
                    guid=UUID(str(row["guid"])),
                )
            )
        except (KeyError, TypeError, ValueError):
            logger.debug("Skipping malformed RUZ search row: %r", row)
            continue
    return items


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
