import asyncio

import pytest

from ruz_server.services.refresh_scheduler import run_refresh_with_session


@pytest.mark.unit
@pytest.mark.asyncio
async def test_run_refresh_with_session_skips_parallel_run(monkeypatch, tmp_path):
    lock_path = tmp_path / "refresh.lock"
    monkeypatch.setattr(
        "ruz_server.services.refresh_scheduler.settings.refresh_lock_file",
        str(lock_path),
    )

    async def slow_runner(_session):
        await asyncio.sleep(0.1)
        return {"status": "ok"}

    first_task = asyncio.create_task(
        run_refresh_with_session(
            session=None, source="test_first", refresh_runner=slow_runner
        )
    )
    await asyncio.sleep(0.01)

    second_result = await run_refresh_with_session(
        session=None,
        source="test_second",
        refresh_runner=slow_runner,
    )
    first_result = await first_task

    assert first_result["status"] == "ok"
    assert second_result == {"status": "skipped", "reason": "refresh already running"}
    assert not lock_path.exists()
