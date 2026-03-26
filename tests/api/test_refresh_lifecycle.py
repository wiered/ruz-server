import asyncio

import pytest

from ruz_server.api.app import app


@pytest.mark.api
@pytest.mark.asyncio
async def test_refresh_scheduler_daily_job_config(monkeypatch):
    monkeypatch.setattr("ruz_server.api.app.settings.doupdate", False)
    monkeypatch.setattr("ruz_server.api.app.settings.refresh_hour", 2)
    monkeypatch.setattr("ruz_server.api.app.settings.refresh_minute", 0)
    monkeypatch.setattr("ruz_server.api.app.settings.refresh_timezone", "Europe/Moscow")

    async with app.router.lifespan_context(app):
        scheduler = app.state.refresh_scheduler
        job = scheduler.get_job("daily_refresh")
        assert job is not None
        assert str(job.trigger.timezone) == "Europe/Moscow"
        assert str(job.trigger.fields[5]) == "2"
        assert str(job.trigger.fields[6]) == "0"


@pytest.mark.api
@pytest.mark.asyncio
async def test_refresh_doupdate_startup_triggers_job(monkeypatch):
    called = {"source": None}

    async def fake_run_refresh_job(source: str = "scheduler"):
        called["source"] = source
        return {"status": "ok"}

    monkeypatch.setattr("ruz_server.api.app.settings.doupdate", True)
    monkeypatch.setattr("ruz_server.api.app.run_refresh_job", fake_run_refresh_job)

    async with app.router.lifespan_context(app):
        await asyncio.sleep(0)

    assert called["source"] == "startup_doupdate"
