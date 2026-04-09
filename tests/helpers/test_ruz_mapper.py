"""Unit tests for RUZ payload mapper helpers."""

import pytest

from ruz_server.helpers.ruz_mapper import (
    _extract_subgroup,
    _normalize_date,
    _normalize_time,
    map_ruz_lesson_to_lesson_create_payload,
)


def _raw_lesson() -> dict:
    return {
        "lessonOid": 101,
        "lecturerOid": 1001,
        "lecturerCustomUID": "f04b73e5-a908-4984-9d57-8fbe49e9b7ec",
        "listOfLecturers": [{"lecturer_title": "Ivan Ivanov"}],
        "lecturer": "I. Ivanov",
        "lecturer_rank": "Professor",
        "kindOfWorkOid": 2001,
        "typeOfWork": "Лекция",
        "kindOfWorkComplexity": 2,
        "disciplineOid": 3001,
        "discipline": "Math",
        "auditoriumOid": 4001,
        "auditoriumGUID": "0e4fdd10-0f17-4f17-87bc-626d3f711099",
        "auditorium": "A-101",
        "building": "Main",
        "date": "2025.01.15",
        "beginLesson": "09:00",
        "endLesson": "10:30",
        "listSubGroups": [{"subgroup": "Подгруппа 2"}],
    }


@pytest.mark.unit
def test_normalize_date_supports_ruz_and_iso_format():
    assert _normalize_date("2025.01.15") == "2025-01-15"
    assert _normalize_date("2025-01-15") == "2025-01-15"


@pytest.mark.unit
def test_normalize_time_appends_seconds_for_short_value():
    assert _normalize_time("09:00") == "09:00:00"
    assert _normalize_time("09:00:15") == "09:00:15"


@pytest.mark.unit
def test_extract_subgroup_prefers_list_subgroups():
    raw = _raw_lesson()
    raw["subGroup"] = "Подгруппа 1"
    assert _extract_subgroup(raw) == 2


@pytest.mark.unit
def test_extract_subgroup_uses_subgroup_fallback_and_default_zero():
    assert _extract_subgroup({"subGroup": "Подгруппа 3"}) == 3
    assert _extract_subgroup({"subGroup": "unknown"}) == 0
    assert _extract_subgroup({}) == 0


@pytest.mark.unit
def test_map_ruz_lesson_to_payload_maps_required_fields():
    payload = map_ruz_lesson_to_lesson_create_payload(_raw_lesson(), group_id=5001)

    assert payload["id"] == 101
    assert payload["lecturer_id"] == 1001
    assert payload["discipline_id"] == 3001
    assert payload["auditorium_id"] == 4001
    assert payload["date"] == "2025-01-15"
    assert payload["begin_lesson"] == "09:00:00"
    assert payload["end_lesson"] == "10:30:00"
    assert payload["group_id"] == 5001
    assert payload["sub_group"] == 2


@pytest.mark.unit
def test_map_ruz_lesson_to_payload_raises_for_invalid_date():
    raw = _raw_lesson()
    raw["date"] = "2025/01/15"

    with pytest.raises(ValueError):
        map_ruz_lesson_to_lesson_create_payload(raw, group_id=5001)
