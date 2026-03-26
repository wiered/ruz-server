from __future__ import annotations

from datetime import datetime
from typing import Any


def _normalize_date(value: str) -> str:
    """Convert RUZ date to ISO YYYY-MM-DD."""
    if "." in value:
        return datetime.strptime(value, "%Y.%m.%d").date().isoformat()
    return datetime.strptime(value, "%Y-%m-%d").date().isoformat()


def _normalize_time(value: str) -> str:
    """Convert HH:MM to HH:MM:SS if needed."""
    if len(value) == 5:
        return f"{value}:00"
    return value


def _extract_subgroup(raw: dict[str, Any]) -> int:
    list_subgroups = raw.get("listSubGroups") or []
    if list_subgroups:
        subgroup_value = str(list_subgroups[0].get("subgroup", ""))
        digits = "".join(ch for ch in subgroup_value if ch.isdigit())
        if digits:
            return int(digits[-1])

    subgroup_value = str(raw.get("subGroup") or "")
    digits = "".join(ch for ch in subgroup_value if ch.isdigit())
    if digits:
        return int(digits[-1])

    return 0


def _extract_lecturer_full_name(raw: dict[str, Any]) -> str:
    list_lecturers = raw.get("listOfLecturers") or []
    if list_lecturers and list_lecturers[0].get("lecturer_title"):
        return str(list_lecturers[0]["lecturer_title"])
    if raw.get("lecturer_title"):
        return str(raw["lecturer_title"])
    return str(raw.get("lecturer", ""))


def map_ruz_lesson_to_lesson_create_payload(
    raw: dict[str, Any],
    group_id: int,
) -> dict[str, Any]:
    """
    Map one RUZ lesson JSON object to payload for POST /api/lesson/.
    """
    return {
        "id": int(raw["lessonOid"]),
        "lecturer_id": int(raw["lecturerOid"]),
        "lecturer_guid": str(raw["lecturerCustomUID"]),
        "lecturer_full_name": _extract_lecturer_full_name(raw),
        "lecturer_short_name": str(raw["lecturer"]),
        "lecturer_rank": str(raw.get("lecturer_rank") or ""),
        "kind_of_work_id": int(raw["kindOfWorkOid"]),
        "type_of_work": str(raw.get("typeOfWork") or raw.get("kindOfWork") or ""),
        "complexity": int(raw.get("kindOfWorkComplexity") or 1),
        "discipline_id": int(raw["disciplineOid"]),
        "discipline_name": str(raw["discipline"]),
        "auditorium_id": int(raw["auditoriumOid"]),
        "auditorium_guid": str(raw["auditoriumGUID"]),
        "auditorium_name": str(raw["auditorium"]),
        "auditorium_building": str(raw.get("building") or ""),
        "date": _normalize_date(str(raw["date"])),
        "begin_lesson": _normalize_time(str(raw["beginLesson"])),
        "end_lesson": _normalize_time(str(raw["endLesson"])),
        "group_id": int(group_id),
        "sub_group": _extract_subgroup(raw),
    }


def map_ruz_lessons_to_payloads(
    raw_lessons: list[dict[str, Any]],
    group_id: int,
) -> list[dict[str, Any]]:
    """Map a list of RUZ lessons to payloads for POST /api/lesson/."""
    return [
        map_ruz_lesson_to_lesson_create_payload(raw, group_id)
        for raw in raw_lessons
    ]
