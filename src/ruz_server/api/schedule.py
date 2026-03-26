import datetime
from typing import Generator, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlmodel import Session

from ruz_server.database import db
from ruz_server.models import Lesson
from ruz_server.repositories import LessonRepository, UserRepository

router = APIRouter(prefix="/schedule", tags=["schedule"])


def get_db() -> Generator[Session, None, None]:
    yield from db.get_session()


class UserScheduleLessonRead(BaseModel):
    lesson_id: int
    date: datetime.date
    begin_lesson: datetime.time
    end_lesson: datetime.time
    sub_group: int
    discipline_name: str
    kind_of_work: str
    lecturer_short_name: str
    auditorium_name: str
    building: str
    group_id: int


def get_week_range(anchor_date: datetime.date) -> tuple[datetime.date, datetime.date]:
    start = anchor_date - datetime.timedelta(days=anchor_date.weekday())
    end = start + datetime.timedelta(days=6)
    return start, end


def map_lesson_to_schedule_dto(
    lesson: Lesson,
    group_id: int | None = None,
) -> UserScheduleLessonRead:
    resolved_group_id = group_id
    if resolved_group_id is None:
        resolved_group_id = lesson.lesson_groups[0].group_id if lesson.lesson_groups else 0

    return UserScheduleLessonRead(
        lesson_id=lesson.id,
        date=lesson.date,
        begin_lesson=lesson.begin_lesson,
        end_lesson=lesson.end_lesson,
        sub_group=lesson.sub_group,
        discipline_name=(lesson.discipline.name if lesson.discipline else ""),
        kind_of_work=(lesson.kind_of_work.type_of_work if lesson.kind_of_work else ""),
        lecturer_short_name=(lesson.lecturer.short_name if lesson.lecturer else ""),
        auditorium_name=(lesson.auditorium.name if lesson.auditorium else ""),
        building=(lesson.auditorium.building if lesson.auditorium else ""),
        group_id=resolved_group_id,
    )


def _get_user_group_and_subgroup(user_id: int, session: Session) -> tuple[int, int]:
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
    return user.group_oid, user.subgroup


@router.get("/user/{user_id}/day", response_model=List[UserScheduleLessonRead])
def get_user_schedule_day(
    user_id: int,
    date: datetime.date = Query(...),
    session: Session = Depends(get_db),
):
    group_id, subgroup = _get_user_group_and_subgroup(user_id, session)
    lesson_repo = LessonRepository(session)
    lessons = lesson_repo.ListForUserByDateRange(
        group_id=group_id,
        subgroup=subgroup,
        start=date,
        end=date,
    )
    return [map_lesson_to_schedule_dto(lesson, group_id) for lesson in lessons]


@router.get("/user/{user_id}/week", response_model=List[UserScheduleLessonRead])
def get_user_schedule_week(
    user_id: int,
    date: datetime.date = Query(...),
    session: Session = Depends(get_db),
):
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
