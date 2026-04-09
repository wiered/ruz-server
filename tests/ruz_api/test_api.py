"""Unit tests for RuzAPI client."""

import datetime
import uuid
import pytest
import aiohttp



from ruz_server.ruz_api.api import RuzAPI, LessonCreate


class FakeResponse:
    def __init__(self, status=200, headers=None, json_data=None):
        self.status = status
        self.headers = headers or {}
        self._json_data = json_data if json_data is not None else {}

    async def json(self, encoding=None):
        return self._json_data

    def raise_for_status(self):
        raise aiohttp.ClientResponseError(
            request_info=None,
            history=(),
            status=self.status,
            message="error",
            headers=None,
        )


class FakeGetCtx:
    def __init__(self, response):
        self.response = response

    async def __aenter__(self):
        return self.response

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def get(self, url=None, ssl=True):
        response = self.responses[self.calls]
        self.calls += 1
        return FakeGetCtx(response)


@pytest.mark.unit
@pytest.mark.ruzapi
class TestRuzApi:
    @pytest.mark.asyncio
    async def test_sleep_uses_retry_after_header(self, monkeypatch):
        api = RuzAPI()
        delays = []

        async def fake_sleep(value):
            delays.append(value)

        monkeypatch.setattr("ruz_server.ruz_api.api.asyncio.sleep", fake_sleep)
        response = FakeResponse(status=429, headers={"Retry-After": "3"})

        backoff = await api._sleep(response, 1)

        assert delays == [3]
        assert backoff == 2

    @pytest.mark.asyncio
    async def test_sleep_uses_backoff_without_retry_after(self, monkeypatch):
        api = RuzAPI()
        delays = []

        async def fake_sleep(value):
            delays.append(value)

        monkeypatch.setattr("ruz_server.ruz_api.api.asyncio.sleep", fake_sleep)
        response = FakeResponse(status=429, headers={})

        backoff = await api._sleep(response, 4)

        assert delays == [4]
        assert backoff == 8

    @pytest.mark.asyncio
    async def test_get_borders_for_schedule_format(self):
        api = RuzAPI()
        start_str, end_str = await api._get_borders_for_schedule()

        datetime.datetime.strptime(start_str, "%Y.%m.%d")
        datetime.datetime.strptime(end_str, "%Y.%m.%d")
        assert start_str <= end_str

    @pytest.mark.asyncio
    async def test_get_borders_for_schedule_january_edge(self, monkeypatch):
        class FixedDateTime(datetime.datetime):
            @classmethod
            def today(cls):
                return cls(2025, 1, 10)

        monkeypatch.setattr("ruz_server.ruz_api.api.datetime", FixedDateTime)
        api = RuzAPI()
        start_str, end_str = await api._get_borders_for_schedule()

        assert start_str == "2024.12.01"
        assert end_str == "2025.02.28"

    @pytest.mark.asyncio
    async def test_get_borders_for_schedule_leap_year_february_edge(self, monkeypatch):
        class FixedDateTime(datetime.datetime):
            @classmethod
            def today(cls):
                return cls(2024, 2, 15)

        monkeypatch.setattr("ruz_server.ruz_api.api.datetime", FixedDateTime)
        api = RuzAPI()
        start_str, end_str = await api._get_borders_for_schedule()

        assert start_str == "2024.01.01"
        assert end_str == "2024.03.31"

    @pytest.mark.asyncio
    async def test_parse_lessons_success(self):
        api = RuzAPI()
        raw = [{
            "lessonOid": 1,
            "lecturerOid": 100,
            "lecturerCustomUID": str(uuid.uuid4()),
            "listOfLecturers": [{"lecturer_title": "John Smith"}],
            "lecturer": "J. Smith",
            "lecturer_rank": "Professor",
            "kindOfWorkOid": 10,
            "typeOfWork": "Лекция",
            "kindOfWorkComplexity": 2,
            "disciplineOid": 20,
            "discipline": "Math",
            "auditoriumOid": 30,
            "auditoriumGUID": str(uuid.uuid4()),
            "auditorium": "A-101",
            "building": "Main",
            "date": "2025.01.15",
            "beginLesson": "09:00",
            "endLesson": "10:30",
            "listSubGroups": [{"subgroup": "Подгруппа 2"}],
        }]

        result = await api._parse_lessons(raw, "500", "2025-01-15T10:00:00")

        assert len(result) == 1
        assert isinstance(result[0], LessonCreate)
        assert result[0].group_id == 500
        assert result[0].sub_group == 2
        assert result[0].discipline_name == "Math"

    @pytest.mark.asyncio
    async def test_fetch_success(self):
        api = RuzAPI()
        client = FakeClient([FakeResponse(status=200, json_data={"ok": True})])

        data = await api._fetch(client, "http://test")

        assert data == {"ok": True}
        assert client.calls == 1

    @pytest.mark.asyncio
    async def test_fetch_retries_after_429(self, monkeypatch):
        api = RuzAPI()
        client = FakeClient([
            FakeResponse(status=429, headers={"Retry-After": "1"}),
            FakeResponse(status=200, json_data={"ok": True}),
        ])
        sleeps = []

        async def fake_sleep(value):
            sleeps.append(value)

        monkeypatch.setattr("ruz_server.ruz_api.api.asyncio.sleep", fake_sleep)

        data = await api._fetch(client, "http://test")

        assert data == {"ok": True}
        assert client.calls == 2
        assert sleeps == [1]

    @pytest.mark.asyncio
    async def test_fetch_raises_after_max_retries(self, monkeypatch):
        api = RuzAPI()
        client = FakeClient([FakeResponse(status=429) for _ in range(5)])

        async def fake_sleep(value):
            return None

        monkeypatch.setattr("ruz_server.ruz_api.api.asyncio.sleep", fake_sleep)

        with pytest.raises(aiohttp.ClientError):
            await api._fetch(client, "http://test")

    @pytest.mark.asyncio
    async def test_get_day_calls_get_with_same_date(self, monkeypatch):
        api = RuzAPI()

        async def fake_get(group, start, end):
            return {"group": group, "start": start, "end": end}

        monkeypatch.setattr(api, "get", fake_get)
        target_date = datetime.datetime(2025, 1, 20)

        result = await api.getDay("IU8-31", target_date)

        assert result["start"] == "2025.01.20"
        assert result["end"] == "2025.01.20"

    @pytest.mark.asyncio
    async def test_get_week_calls_get_for_week_range(self, monkeypatch):
        api = RuzAPI()

        async def fake_get(group, start, end):
            return {"group": group, "start": start, "end": end}

        monkeypatch.setattr(api, "get", fake_get)
        target_date = datetime.datetime(2025, 1, 22)  # Wednesday

        result = await api.getWeek("IU8-31", target_date)

        assert result["start"] == "2025.01.20"
        assert result["end"] == "2025.01.26"

    @pytest.mark.asyncio
    async def test_get_schedule_empty_result(self, monkeypatch):
        api = RuzAPI()

        async def fake_borders():
            return "2025.01.01", "2025.03.31"

        async def fake_get(group_id, start, end):
            return []

        async def fake_parse(raw, group_id, update_time):
            return []

        monkeypatch.setattr(api, "_get_borders_for_schedule", fake_borders)
        monkeypatch.setattr(api, "get", fake_get)
        monkeypatch.setattr(api, "_parse_lessons", fake_parse)

        result = await api.getSchedule("500")

        assert result == []

