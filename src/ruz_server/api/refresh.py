import asyncio
import logging
from pickletools import int4
import random
from datetime import time, date
from datetime import date as datetime_date
from datetime import datetime as dt
from typing import Any, Generator, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Security, status
from pydantic import BaseModel, ConfigDict, ValidationError
from sqlmodel import Session

from ruz_server.api.security import require_api_key
from ruz_server.database import db
from ruz_server.helpers.api_helpers import (
    create_if_not_exists,
    ensure_entity_doesnot_exist,
    ensure_entity_exists,
)
from ruz_server.helpers.ruz_mapper import map_ruz_lessons_to_payloads
from ruz_server.models import *
from ruz_server.repositories import *
from ruz_server.ruz_api import RuzAPI

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/lesson", tags=["lesson"])


def get_db() -> Generator[Session, None, None]:
    yield from db.get_session()


EXAM_TYPES = ["Зачёт", "Экзамен"]


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


def _upsert_lecturer(payload: LessonCreate, session: Session) -> None:
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


def _upsert_kind_of_work(payload: LessonCreate, session: Session) -> None:
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


def _upsert_discipline(payload: LessonCreate, session: Session) -> None:
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


def _upsert_auditorium(payload: LessonCreate, session: Session) -> None:
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


def _upsert_discipline(payload: LessonCreate, session: Session) -> None:
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


def _upsert_reference_entities(payload: LessonCreate, session: Session) -> None:
    """
    Upserts (inserts or updates) reference entities (Lecturer, KindOfWork, Discipline, Auditorium) as required by the LessonCreate payload.

    This helper checks for the existence of related entities required by a new lesson. If any referenced entity
    does not exist in the database, it inserts it with the supplied attributes. If it already exists,
    it updates its fields with the information from the payload. This ensures all references are present
    and up-to-date before lesson creation.

    Args:
        payload (LessonCreate): The information needed to create the lesson, including attributes for related entities.
        session (Session): The active database session used for upsert operations.

    Returns:
        None
    """
    _upsert_lecturer(payload, session)
    _upsert_kind_of_work(payload, session)
    _upsert_discipline(payload, session)
    _upsert_auditorium(payload, session)
    _upsert_discipline(payload, session)


def _get_payload(raw_lesson: dict[str, Any], group_id: int4) -> LessonCreate:
    try:
        mapped_payload = map_ruz_lessons_to_payloads([raw_lesson], group_id)[0]
    except Exception as exc:
        raise Exception(exc)
    try:
        payload = LessonCreate(**mapped_payload)
    except ValidationError as exc:
        raise ValidationError(exc)

    return payload


def _upsert(values: list[LessonCreate], session: Session) -> tuple[int, int, int]:
    lessons_upserted = 0
    lessons_created = 0
    lessons_updated = 0
    lesson_repository = LessonRepository(session)
    for payload in values:
        _upsert_reference_entities(payload, session)
        lesson_model = Lesson(
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
        _, created = lesson_repository.Upsert(lesson_model)
        lessons_upserted += 1
        if created:
            lessons_created += 1
        else:
            lessons_updated += 1
    return lessons_upserted, lessons_created, lessons_updated


async def _get_incoming_lessons(
    groups: list[Group], start_str: str, end_str: str, stats: dict[str, Any]
) -> tuple[dict[int, LessonCreate], set[tuple[int, int]]]:
    ruz_api = RuzAPI()
    incoming_lessons: dict[int, LessonCreate] = {}
    incoming_pairs: set[tuple[int, int]] = set()
    tmp_stats: dict[str, Any] = {
        "groups_processed": 0,
        "lessons_received": 0,
        "lessons_skipped": 0,
        "errors": [],
    }

    for i, group in enumerate(groups):
        if i > 0:
            await asyncio.sleep(random.uniform(7, 10))
        try:
            raw_lessons = await ruz_api.get(str(group.id), start_str, end_str)
            tmp_stats["groups_processed"] += 1
            tmp_stats["lessons_received"] += len(raw_lessons)
        except Exception as exc:
            tmp_stats["errors"].append(
                {
                    "group_id": group.id,
                    "stage": "fetch",
                    "message": str(exc),
                }
            )
            continue

        for raw_lesson in raw_lessons:
            try:
                payload = _get_payload(raw_lesson, group.id)
            except Exception as exc:
                tmp_stats["lessons_skipped"] += 1
                tmp_stats["errors"].append(
                    {
                        "group_id": group.id,
                        "lesson_id": raw_lesson.get("lessonOid")
                        if isinstance(exc, ValidationError)
                        else None,
                        "stage": "get_payload"
                        if isinstance(exc, ValidationError)
                        else "map",
                        "message": str(exc),
                    }
                )
                continue

            incoming_lessons[payload.id] = payload
            incoming_pairs.add((payload.id, group.id))

    return incoming_lessons, incoming_pairs, tmp_stats


async def parse_lessons_core(session: Session) -> dict[str, Any]:
    """
    Initialize repositories and load all groups for lesson parsing.

    Args:
        session (Session): The database session used for repository operations.

    Returns:
        tuple: (group_repository, lesson_group_repository, lesson_repository, ruz_api, groups)
            group_repository (GroupRepository): Handles Group entity operations.
            lesson_group_repository (LessonGroupRepository): Handles LessonGroup entity operations.
            lesson_repository (LessonRepository): Handles Lesson entity operations.
            ruz_api (RuzAPI): API client for fetching schedule data from external service.
            groups (list): List of all group entities loaded from the database.
    """
    group_repository = GroupRepository(session)
    lesson_group_repository = LessonGroupRepository(session)
    lesson_repository = LessonRepository(session)
    ruz_api = RuzAPI()
    groups = group_repository.ListAll()

    stats: dict[str, Any] = {
        "groups_total": len(groups),
        "groups_processed": 0,
        "lessons_received": 0,
        "lessons_upserted": 0,
        "lessons_created": 0,
        "lessons_updated": 0,
        "links_created": 0,
        "links_pruned": 0,
        "lessons_pruned": 0,
        "lessons_skipped": 0,
        "errors": [],
    }

    start_str, end_str = await ruz_api._get_borders_for_schedule()
    range_start = dt.strptime(start_str, "%Y.%m.%d").date()
    range_end = dt.strptime(end_str, "%Y.%m.%d").date()
    incoming_lessons, incoming_pairs, tmp_stats = await _get_incoming_lessons(
        groups, start_str, end_str, stats
    )

    stats["groups_processed"] += tmp_stats["groups_processed"]
    stats["lessons_received"] += tmp_stats["lessons_received"]
    stats["lessons_skipped"] += tmp_stats["lessons_skipped"]
    stats["errors"].extend(tmp_stats["errors"])

    if not incoming_lessons:
        logger.warning("Parse completed with empty snapshot; prune is skipped.")
        return stats

    try:
        lessons_upserted, lessons_created, lessons_updated = _upsert(
            incoming_lessons.values(), session
        )
        stats["lessons_upserted"] += lessons_upserted
        stats["lessons_created"] += lessons_created
        stats["lessons_updated"] += lessons_updated

        links = [
            LessonGroup(lesson_id=lesson_id, group_id=group_id)
            for lesson_id, group_id in incoming_pairs
        ]
        stats["links_created"] = lesson_group_repository.BulkGetOrCreate(links)
        stats["links_pruned"] = lesson_group_repository.DeleteMissingPairsInDateRange(
            incoming_pairs=incoming_pairs,
            start=range_start,
            end=range_end,
        )

        existing_ids = set(lesson_repository.ListIdsInDateRange(range_start, range_end))
        stale_ids = existing_ids - set(incoming_lessons.keys())
        if stale_ids:
            stats["lessons_pruned"] = lesson_repository.DeleteByIds(stale_ids)

        session.commit()
    except Exception as exc:
        session.rollback()
        stats["errors"].append(
            {
                "stage": "transaction",
                "message": str(exc),
            }
        )
        raise

    return stats
