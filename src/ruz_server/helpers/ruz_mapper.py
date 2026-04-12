from __future__ import annotations

from datetime import datetime
from typing import Any


def _normalize_date(value: str) -> str:
    """
    Normalize date string to ISO format (YYYY-MM-DD).

    Args:
        value (str): Input date string in either 'YYYY.MM.DD' or 'YYYY-MM-DD' format.

    Returns:
        str: Date in ISO format ('YYYY-MM-DD').
    """
    if "." in value:
        return datetime.strptime(value, "%Y.%m.%d").date().isoformat()
    return datetime.strptime(value, "%Y-%m-%d").date().isoformat()


def _normalize_time(value: str) -> str:
    """
    Normalize time string to HH:MM:SS format.

    Args:
        value (str): Input time string in 'HH:MM' or 'HH:MM:SS' format.

    Returns:
        str: Time in 'HH:MM:SS' format.
    """
    if len(value) == 5:
        return f"{value}:00"
    return value


def _extract_subgroup(raw: dict[str, Any]) -> int:
    """
    Extracts the subgroup value from the raw lesson dictionary.

    This function searches for subgroup information within the "listSubGroups" key (preferred),
    falling back to the "subGroup" key if necessary, and parses the last digit found
    to return it as an integer. If no subgroup is present, returns 0.

    Args:
        raw (dict[str, Any]): The raw lesson dictionary containing subgroup information.

    Returns:
        int: The extracted subgroup number. Returns 0 if no subgroup is found.
    """
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
    """
    Extract the full name of the lecturer from the given raw lesson dictionary.

    This function checks for the lecturer's full name in the "listOfLecturers" field (using "lecturer_title" key if available),
    then falls back to "lecturer_title", and if neither is available, uses the "lecturer" field.

    Args:
        raw (dict[str, Any]): The raw lesson dictionary possibly containing lecturer information.

    Returns:
        str: The extracted lecturer's full name, or an empty string if not found.
    """
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
    Maps a raw RUZ lesson dictionary to a lesson creation payload dictionary.

    This function extracts and normalizes all relevant lesson information from the raw RUZ lesson data,
    preparing it for use in lesson creation or update. It processes fields such as lecturer, auditorium,
    discipline, date, times, and group/subgroup associations.

    Args:
        raw (dict[str, Any]): The raw lesson dictionary from RUZ containing all lesson properties.
        group_id (int): The ID of the group to associate with this lesson.

    Returns:
        dict[str, Any]: A dictionary payload suitable for lesson creation, containing standardized and
        normalized lesson information.
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
    """
    Maps a list of raw RUZ lessons to a list of lesson creation payloads.

    This function processes each raw lesson dictionary in the input list, normalizes its fields,
    and returns a list of standardized lesson payload dictionaries ready for creation.

    Args:
        raw_lessons (list[dict[str, Any]]): The list of raw lesson dictionaries from RUZ.
        group_id (int): The ID of the group to associate with these lessons.

    Returns:
        list[dict[str, Any]]: A list of dictionaries, each containing normalized lesson information.
    """
    return [
        map_ruz_lesson_to_lesson_create_payload(raw, group_id) for raw in raw_lessons
    ]
