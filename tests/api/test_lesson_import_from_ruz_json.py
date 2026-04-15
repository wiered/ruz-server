"""Integration test for importing lessons from RUZ JSON examples."""

import json
import re
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, select

from ruz_server.api import lesson
from ruz_server.api.app import app
from ruz_server.api.security import require_api_key
from ruz_server.helpers.ruz_mapper import map_ruz_lessons_to_payloads
from ruz_server.models.models import (
    Auditorium,
    Discipline,
    KindOfWork,
    Lecturer,
    Lesson,
)


def _load_relaxed_json(file_path: Path) -> dict:
    """
    Load JSON-like fixtures that may contain JS-style // comments.
    """
    content = file_path.read_text(encoding="utf-8-sig")
    content = re.sub(r"//.*", "", content)
    return json.loads(content)


@pytest_asyncio.fixture
async def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def override_get_db():
        session = Session(engine)
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[require_api_key] = lambda: None
    app.dependency_overrides[lesson.get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as test_client:
        test_client.engine = engine
        yield test_client
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.mark.api
@pytest.mark.asyncio
async def test_import_lessons_from_example_multiple_json(client):
    file_path = (
        Path(__file__).resolve().parents[2]
        / "tests"
        / "fixtures"
        / "ruz"
        / "example.multiple.json"
    )
    data = json.loads(file_path.read_text(encoding="utf-8-sig"))

    payloads = map_ruz_lessons_to_payloads(data, group_id=841)

    # Manual expectation for source lesson identifiers from JSON
    expected_source_lesson_ids = {
        94673,
        94775,
        95739,
        95740,
        96549,
        96561,
        96546,
        95756,
        95743,
        95912,
        95916,
        95772,
        95773,
    }
    assert {payload["id"] for payload in payloads} == expected_source_lesson_ids

    for payload in payloads:
        response = await client.post("/api/lesson/", json=payload)
        assert response.status_code == 201, response.text

    with Session(client.engine) as session:
        lessons = session.exec(select(Lesson)).all()
        lecturers = session.exec(select(Lecturer)).all()
        kinds = session.exec(select(KindOfWork)).all()
        disciplines = session.exec(select(Discipline)).all()
        auditoriums = session.exec(select(Auditorium)).all()

        # Manual, fixed expectations based on trash/example.multiple.json
        assert len(lessons) == 13
        assert len(lecturers) == 6
        assert len(kinds) == 1
        assert len(disciplines) == 9
        assert len(auditoriums) == 2

        # Lesson.id is persisted as source lessonOid.
        assert {lesson.id for lesson in lessons} == expected_source_lesson_ids

        expected_lecturer_ids = {1157, 1066, 1150, 1077, 1119, 1160}
        actual_lecturer_ids = {lecturer.id for lecturer in lecturers}
        assert actual_lecturer_ids == expected_lecturer_ids

        expected_discipline_ids = {3087, 3758, 3013, 3251, 3148, 3225, 3759, 3755, 3187}
        actual_discipline_ids = {discipline.id for discipline in disciplines}
        assert actual_discipline_ids == expected_discipline_ids

        expected_auditorium_ids = {81, 99}
        actual_auditorium_ids = {auditorium.id for auditorium in auditoriums}
        assert actual_auditorium_ids == expected_auditorium_ids

        # In this fixture all lessons are lectures with the same kind_of_work
        expected_kind_ids = {95}
        actual_kind_ids = {kind.id for kind in kinds}
        assert actual_kind_ids == expected_kind_ids
        assert {kind.type_of_work for kind in kinds} == {"Лекции"}
        assert {kind.complexity for kind in kinds} == {1}

        # Spot-check mapped fields for several known lessons
        lesson_signatures = {
            (
                lesson.discipline_id,
                lesson.lecturer_id,
                lesson.auditorium_id,
                str(lesson.date),
                str(lesson.begin_lesson),
                str(lesson.end_lesson),
                lesson.sub_group,
            )
            for lesson in lessons
        }
        expected_signatures = {
            (3087, 1157, 81, "2025-09-01", "12:40:00", "14:10:00", 0),
            (3758, 1157, 99, "2025-09-01", "14:20:00", "15:50:00", 0),
            (3013, 1066, 99, "2025-09-02", "08:30:00", "10:00:00", 0),
            (3251, 1066, 99, "2025-09-02", "10:10:00", "11:40:00", 0),
            (3148, 1150, 81, "2025-09-03", "08:30:00", "10:00:00", 0),
            (3225, 1077, 81, "2025-09-03", "10:10:00", "11:40:00", 0),
            (3759, 1119, 81, "2025-09-03", "12:40:00", "14:10:00", 0),
            (3013, 1066, 99, "2025-09-05", "12:40:00", "14:10:00", 0),
            (3251, 1066, 99, "2025-09-05", "14:20:00", "15:50:00", 0),
            (3755, 1160, 99, "2025-09-05", "16:00:00", "17:30:00", 0),
            (3187, 1160, 99, "2025-09-05", "18:00:00", "19:30:00", 0),
            (3755, 1160, 99, "2025-09-06", "08:30:00", "10:00:00", 0),
            (3187, 1160, 99, "2025-09-06", "10:10:00", "11:40:00", 0),
        }
        assert lesson_signatures == expected_signatures


@pytest.mark.api
@pytest.mark.asyncio
async def test_import_lesson_from_example_practice_json(client):
    file_path = (
        Path(__file__).resolve().parents[2]
        / "tests"
        / "fixtures"
        / "ruz"
        / "example.practice.json"
    )
    raw = _load_relaxed_json(file_path)
    payload = map_ruz_lessons_to_payloads([raw], group_id=841)[0]

    # Manual expectations from example.practice.json
    assert payload["id"] == 95780
    assert payload["lecturer_id"] == 1160
    assert payload["lecturer_short_name"] == "Терентьев А.И."
    assert payload["lecturer_full_name"] == "Терентьев Андрей Иванович"
    assert payload["kind_of_work_id"] == 102
    assert payload["type_of_work"] == "Практические (семинарские) занятия"
    assert payload["complexity"] == 1
    assert payload["discipline_id"] == 3755
    assert payload["discipline_name"] == "Безопасность в цифровом пространстве"
    assert payload["auditorium_id"] == 177
    assert payload["auditorium_name"] == "5 корпус/5-409"
    assert payload["auditorium_building"] == "Пулковская улица, дом 10 "
    assert payload["date"] == "2025-09-13"
    assert payload["begin_lesson"] == "12:40:00"
    assert payload["end_lesson"] == "14:10:00"
    assert payload["group_id"] == 841
    assert payload["sub_group"] == 0

    response = await client.post("/api/lesson/", json=payload)
    assert response.status_code == 201, response.text

    with Session(client.engine) as session:
        lessons = session.exec(select(Lesson)).all()
        lecturers = session.exec(select(Lecturer)).all()
        kinds = session.exec(select(KindOfWork)).all()
        disciplines = session.exec(select(Discipline)).all()
        auditoriums = session.exec(select(Auditorium)).all()

        assert len(lessons) == 1
        assert len(lecturers) == 1
        assert len(kinds) == 1
        assert len(disciplines) == 1
        assert len(auditoriums) == 1

        lesson_row = lessons[0]
        assert lesson_row.discipline_id == 3755
        assert lesson_row.lecturer_id == 1160
        assert lesson_row.auditorium_id == 177
        assert str(lesson_row.date) == "2025-09-13"
        assert str(lesson_row.begin_lesson) == "12:40:00"
        assert str(lesson_row.end_lesson) == "14:10:00"
        assert lesson_row.sub_group == 0

        assert lecturers[0].id == 1160
        assert lecturers[0].short_name == "Терентьев А.И."
        assert kinds[0].id == 102
        assert kinds[0].type_of_work == "Практические (семинарские) занятия"
        assert disciplines[0].id == 3755
        assert disciplines[0].name == "Безопасность в цифровом пространстве"
        assert auditoriums[0].id == 177
        assert auditoriums[0].name == "5 корпус/5-409"


@pytest.mark.api
@pytest.mark.asyncio
async def test_import_lesson_from_example_lab_json(client):
    file_path = (
        Path(__file__).resolve().parents[2]
        / "tests"
        / "fixtures"
        / "ruz"
        / "example.lab.json"
    )
    raw = _load_relaxed_json(file_path)
    # Manual fix for known fixture: disciplineOid is absent in example.lab.json
    raw["disciplineOid"] = 3251
    payload = map_ruz_lessons_to_payloads([raw], group_id=841)[0]
    assert raw.get("disciplineOid") == 3251
    assert payload["discipline_id"] == 3251

    # Manual expectations from example.lab.json
    assert payload["id"] == 97017
    assert payload["lecturer_id"] == 1069
    assert payload["lecturer_short_name"] == "Дровосеков И.В."
    assert payload["lecturer_full_name"] == "Дровосеков Иван Владимирович"
    assert payload["kind_of_work_id"] == 94
    assert payload["type_of_work"] == "Лабораторные работы"
    assert payload["complexity"] == 1
    assert payload["discipline_name"] == "Сети и телекоммуникации"
    assert payload["auditorium_id"] == 175
    assert payload["auditorium_name"] == "5 корпус/5-403"
    assert payload["auditorium_building"] == "Пулковская улица, дом 10 "
    assert payload["date"] == "2025-09-18"
    assert payload["begin_lesson"] == "14:20:00"
    assert payload["end_lesson"] == "15:50:00"
    assert payload["group_id"] == 841
    assert payload["sub_group"] == 2

    response = await client.post("/api/lesson/", json=payload)
    assert response.status_code == 201, response.text

    with Session(client.engine) as session:
        lessons = session.exec(select(Lesson)).all()
        lecturers = session.exec(select(Lecturer)).all()
        kinds = session.exec(select(KindOfWork)).all()
        disciplines = session.exec(select(Discipline)).all()
        auditoriums = session.exec(select(Auditorium)).all()

        assert len(lessons) == 1
        assert len(lecturers) == 1
        assert len(kinds) == 1
        assert len(disciplines) == 1
        assert len(auditoriums) == 1

        lesson_row = lessons[0]
        assert lesson_row.lecturer_id == 1069
        assert lesson_row.auditorium_id == 175
        assert str(lesson_row.date) == "2025-09-18"
        assert str(lesson_row.begin_lesson) == "14:20:00"
        assert str(lesson_row.end_lesson) == "15:50:00"
        assert lesson_row.sub_group == 2

        assert lecturers[0].id == 1069
        assert kinds[0].id == 94
        assert kinds[0].type_of_work == "Лабораторные работы"
        assert disciplines[0].name == "Сети и телекоммуникации"
        assert disciplines[0].has_labs is False
        assert auditoriums[0].name == "5 корпус/5-403"


@pytest.mark.api
@pytest.mark.asyncio
async def test_import_lesson_from_example_lection_json(client):
    file_path = (
        Path(__file__).resolve().parents[2]
        / "tests"
        / "fixtures"
        / "ruz"
        / "example.lection.json"
    )
    raw = _load_relaxed_json(file_path)
    payload = map_ruz_lessons_to_payloads([raw], group_id=841)[0]

    # Manual expectations from example.lection.json
    assert payload["id"] == 94673
    assert payload["lecturer_id"] == 1157
    assert payload["lecturer_short_name"] == "Романчева Н.И."
    assert payload["lecturer_full_name"] == "Романчева Нина Ивановна"
    assert payload["kind_of_work_id"] == 95
    assert payload["type_of_work"] == "Лекции"
    assert payload["complexity"] == 1
    assert payload["discipline_id"] == 3087
    assert payload["discipline_name"] == "Интернет-технологии"
    assert payload["auditorium_id"] == 81
    assert payload["auditorium_name"] == "1-4 корпус/1-205"
    assert payload["auditorium_building"] == "Пулковская улица, дом 6"
    assert payload["date"] == "2025-09-01"
    assert payload["begin_lesson"] == "12:40:00"
    assert payload["end_lesson"] == "14:10:00"
    assert payload["group_id"] == 841
    assert payload["sub_group"] == 0

    response = await client.post("/api/lesson/", json=payload)
    assert response.status_code == 201, response.text

    with Session(client.engine) as session:
        lessons = session.exec(select(Lesson)).all()
        lecturers = session.exec(select(Lecturer)).all()
        kinds = session.exec(select(KindOfWork)).all()
        disciplines = session.exec(select(Discipline)).all()
        auditoriums = session.exec(select(Auditorium)).all()

        assert len(lessons) == 1
        assert len(lecturers) == 1
        assert len(kinds) == 1
        assert len(disciplines) == 1
        assert len(auditoriums) == 1

        lesson_row = lessons[0]
        assert lesson_row.discipline_id == 3087
        assert lesson_row.lecturer_id == 1157
        assert lesson_row.auditorium_id == 81
        assert str(lesson_row.date) == "2025-09-01"
        assert str(lesson_row.begin_lesson) == "12:40:00"
        assert str(lesson_row.end_lesson) == "14:10:00"
        assert lesson_row.sub_group == 0

        assert lecturers[0].full_name == "Романчева Нина Ивановна"
        assert kinds[0].type_of_work == "Лекции"
        assert disciplines[0].name == "Интернет-технологии"
        assert auditoriums[0].building == "Пулковская улица, дом 6"
