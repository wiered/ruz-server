"""API tests for /api/lesson/parse endpoint."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, select



from ruz_server.api.app import app
from ruz_server.api import lesson
from ruz_server.api.security import require_api_key
from ruz_server.models.models import (
    Auditorium,
    Discipline,
    Group,
    KindOfWork,
    Lecturer,
    Lesson,
    LessonGroup,
)


def _raw_lesson(lesson_oid: int, discipline_oid: int) -> dict:
    return {
        "lessonOid": lesson_oid,
        "lecturerOid": 9100,
        "lecturerCustomUID": str(uuid.uuid4()),
        "listOfLecturers": [{"lecturer_title": "Ivan Ivanov"}],
        "lecturer": "I. Ivanov",
        "lecturer_rank": "Professor",
        "kindOfWorkOid": 8100,
        "typeOfWork": "Лекция",
        "kindOfWorkComplexity": 1,
        "disciplineOid": discipline_oid,
        "discipline": f"Discipline-{discipline_oid}",
        "auditoriumOid": 6100,
        "auditoriumGUID": str(uuid.uuid4()),
        "auditorium": "A-100",
        "building": "Main",
        "date": "2025.01.10",
        "beginLesson": "09:00",
        "endLesson": "10:30",
        "listSubGroups": [{"subgroup": "Подгруппа 1"}],
    }


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
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        test_client.engine = engine
        yield test_client

    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(autouse=True)
def _no_inter_group_sleep(monkeypatch):
    """parse_lessons_core sleeps 7–10s between group fetches; keep API tests fast."""

    async def _noop_sleep(_seconds: float) -> None:
        return None

    monkeypatch.setattr("ruz_server.api.lesson.asyncio.sleep", _noop_sleep)


def _seed_groups(engine):
    with Session(engine) as session:
        session.add(
            Group(
                id=5001,
                guid=uuid.uuid4(),
                name="IU8-31",
                faculty_name="Informatics",
            )
        )
        session.add(
            Group(
                id=5002,
                guid=uuid.uuid4(),
                name="IU8-32",
                faculty_name="Informatics",
            )
        )
        session.commit()


@pytest.mark.api
@pytest.mark.asyncio
async def test_parse_lessons_success_and_idempotent(client, monkeypatch):
    _seed_groups(client.engine)

    async def fake_borders(self):
        return "2025.01.01", "2025.03.31"

    async def fake_get(self, group, start, end):
        if int(group) == 5001:
            return [_raw_lesson(10001, 7001), _raw_lesson(10002, 7002)]
        return [_raw_lesson(20001, 7003)]

    monkeypatch.setattr("ruz_server.api.lesson.RuzAPI._get_borders_for_schedule", fake_borders)
    monkeypatch.setattr("ruz_server.api.lesson.RuzAPI.get", fake_get)

    first = await client.put("/api/lesson/parse")
    assert first.status_code == 200
    first_body = first.json()
    assert first_body["groups_total"] == 2
    assert first_body["groups_processed"] == 2
    assert first_body["lessons_received"] == 3
    assert first_body["lessons_upserted"] == 3
    assert first_body["lessons_created"] == 3
    assert first_body["lessons_updated"] == 0
    assert first_body["links_created"] == 3
    assert first_body["links_pruned"] == 0
    assert first_body["lessons_pruned"] == 0
    assert first_body["lessons_skipped"] == 0
    assert first_body["errors"] == []

    second = await client.put("/api/lesson/parse")
    assert second.status_code == 200
    second_body = second.json()
    assert second_body["lessons_upserted"] == 3
    assert second_body["lessons_created"] == 0
    assert second_body["lessons_updated"] == 3
    assert second_body["lessons_skipped"] == 0

    with Session(client.engine) as session:
        assert len(session.exec(select(Lesson)).all()) == 3
        assert len(session.exec(select(LessonGroup)).all()) == 3
        assert len(session.exec(select(Lecturer)).all()) == 1
        assert len(session.exec(select(KindOfWork)).all()) == 1
        assert len(session.exec(select(Discipline)).all()) == 3
        assert len(session.exec(select(Auditorium)).all()) == 1


@pytest.mark.api
@pytest.mark.asyncio
async def test_parse_lessons_skips_invalid_payload_and_continues(client, monkeypatch):
    _seed_groups(client.engine)

    async def fake_borders(self):
        return "2025.01.01", "2025.03.31"

    async def fake_get(self, group, start, end):
        if int(group) == 5001:
            broken = _raw_lesson(30002, 7005)
            broken.pop("disciplineOid")
            return [_raw_lesson(30001, 7004), broken]
        return []

    monkeypatch.setattr("ruz_server.api.lesson.RuzAPI._get_borders_for_schedule", fake_borders)
    monkeypatch.setattr("ruz_server.api.lesson.RuzAPI.get", fake_get)

    response = await client.put("/api/lesson/parse")
    assert response.status_code == 200
    body = response.json()

    assert body["groups_processed"] == 2
    assert body["lessons_received"] == 2
    assert body["lessons_upserted"] == 1
    assert body["lessons_created"] == 1
    assert body["lessons_skipped"] == 1
    assert any(error["stage"] == "map" for error in body["errors"])

    with Session(client.engine) as session:
        assert len(session.exec(select(Lesson)).all()) == 1
        assert len(session.exec(select(LessonGroup)).all()) == 1


@pytest.mark.api
@pytest.mark.asyncio
async def test_parse_lessons_fetch_error_in_one_group_does_not_stop_others(client, monkeypatch):
    _seed_groups(client.engine)

    async def fake_borders(self):
        return "2025.01.01", "2025.03.31"

    async def fake_get(self, group, start, end):
        if int(group) == 5001:
            raise RuntimeError("RUZ unavailable")
        return [_raw_lesson(40001, 7006)]

    monkeypatch.setattr("ruz_server.api.lesson.RuzAPI._get_borders_for_schedule", fake_borders)
    monkeypatch.setattr("ruz_server.api.lesson.RuzAPI.get", fake_get)

    response = await client.put("/api/lesson/parse")
    assert response.status_code == 200
    body = response.json()

    assert body["groups_total"] == 2
    assert body["groups_processed"] == 1
    assert body["lessons_upserted"] == 1
    assert body["lessons_created"] == 1
    assert body["lessons_skipped"] == 0
    assert any(error["stage"] == "fetch" for error in body["errors"])

    with Session(client.engine) as session:
        lessons = session.exec(select(Lesson)).all()
        lesson_groups = session.exec(select(LessonGroup)).all()
        assert len(lessons) == 1
        assert lessons[0].id == 40001
        assert len(lesson_groups) == 1
        assert lesson_groups[0].group_id == 5002
        assert len(session.exec(select(Group)).all()) == 2


@pytest.mark.api
@pytest.mark.asyncio
async def test_parse_lessons_prunes_removed_lessons(client, monkeypatch):
    _seed_groups(client.engine)

    async def fake_borders(self):
        return "2025.01.01", "2025.03.31"

    async def fake_get_first(self, group, start, end):
        if int(group) == 5001:
            return [_raw_lesson(50001, 7101)]
        return [_raw_lesson(50002, 7102)]

    monkeypatch.setattr("ruz_server.api.lesson.RuzAPI._get_borders_for_schedule", fake_borders)
    monkeypatch.setattr("ruz_server.api.lesson.RuzAPI.get", fake_get_first)
    first = await client.put("/api/lesson/parse")
    assert first.status_code == 200

    async def fake_get_second(self, group, start, end):
        if int(group) == 5001:
            return [_raw_lesson(50001, 7101)]
        return []

    monkeypatch.setattr("ruz_server.api.lesson.RuzAPI.get", fake_get_second)
    second = await client.put("/api/lesson/parse")
    assert second.status_code == 200
    body = second.json()
    assert body["lessons_pruned"] == 1
    assert body["links_pruned"] == 1

    with Session(client.engine) as session:
        lessons = session.exec(select(Lesson)).all()
        assert len(lessons) == 1
        assert lessons[0].id == 50001


@pytest.mark.api
@pytest.mark.asyncio
async def test_parse_lessons_rolls_back_on_transaction_error(client, monkeypatch):
    _seed_groups(client.engine)

    async def fake_borders(self):
        return "2025.01.01", "2025.03.31"

    async def fake_get(self, group, start, end):
        return [_raw_lesson(60001, 7201)]

    monkeypatch.setattr("ruz_server.api.lesson.RuzAPI._get_borders_for_schedule", fake_borders)
    monkeypatch.setattr("ruz_server.api.lesson.RuzAPI.get", fake_get)

    def explode(*args, **kwargs):
        raise RuntimeError("forced transaction failure")

    monkeypatch.setattr("ruz_server.api.lesson._upsert_reference_entities", explode)

    with pytest.raises(RuntimeError, match="forced transaction failure"):
        await client.put("/api/lesson/parse")

    with Session(client.engine) as session:
        assert len(session.exec(select(Lesson)).all()) == 0
        assert len(session.exec(select(LessonGroup)).all()) == 0
        assert len(session.exec(select(Group)).all()) == 2


@pytest.mark.api
@pytest.mark.asyncio
async def test_parse_lessons_rolls_back_when_failure_happens_mid_transaction(client, monkeypatch):
    _seed_groups(client.engine)

    async def fake_borders(self):
        return "2025.01.01", "2025.03.31"

    async def fake_get(self, group, start, end):
        if int(group) == 5001:
            return [_raw_lesson(70001, 7301)]
        return [_raw_lesson(70002, 7302)]

    monkeypatch.setattr("ruz_server.api.lesson.RuzAPI._get_borders_for_schedule", fake_borders)
    monkeypatch.setattr("ruz_server.api.lesson.RuzAPI.get", fake_get)

    original_upsert = lesson.LessonRepository.Upsert
    calls = {"count": 0}

    def explode_on_second(self, lesson_model):
        calls["count"] += 1
        if calls["count"] == 2:
            raise RuntimeError("mid-transaction failure")
        return original_upsert(self, lesson_model)

    monkeypatch.setattr("ruz_server.api.lesson.LessonRepository.Upsert", explode_on_second)

    with pytest.raises(RuntimeError, match="mid-transaction failure"):
        await client.put("/api/lesson/parse")

    with Session(client.engine) as session:
        assert len(session.exec(select(Lesson)).all()) == 0
        assert len(session.exec(select(LessonGroup)).all()) == 0
