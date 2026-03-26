import asyncio
import json
import logging
import os
from pathlib import Path
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

from sqlmodel import Session

from ruz_server.database import db
from ruz_server.settings import settings

logger = logging.getLogger(__name__)

RefreshRunner = Callable[[Session], Awaitable[dict[str, Any]]]

_refresh_lock = asyncio.Lock()

# Последняя завершенная попытка refresh (для health endpoint).
# Поля обновляются только когда refresh реально стартовал и завершился
# (success/error). В случае skip состояние не трогаем, чтобы `healthz`
# отражал свежесть фактически примененных данных.
LAST_REFRESH_AT: datetime | None = None
LAST_REFRESH_STATUS: str = "never"  # never|success|error|skipped


def _acquire_file_lock(lock_path: str) -> int | None:
    path = Path(lock_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    try:
        return os.open(str(path), flags)
    except FileExistsError:
        return None


def _release_file_lock(lock_path: str, fd: int | None) -> None:
    if fd is None:
        return
    try:
        os.close(fd)
    finally:
        Path(lock_path).unlink(missing_ok=True)


def get_last_refresh_state() -> dict[str, Any]:
    """Expose current refresh freshness state for /healthz."""
    return {
        "last_refresh_at": LAST_REFRESH_AT,
        "last_refresh_status": LAST_REFRESH_STATUS,
    }


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or isinstance(value, bool):
            return default
        return int(value)
    except Exception:
        return default


def _aggregate_errors_by_group(result: dict[str, Any]) -> dict[str, int]:
    """Convert parsed refresh errors into counts per group_id."""
    errors = result.get("errors", [])
    if not isinstance(errors, list):
        return {}

    by_group: dict[str, int] = {}
    for err in errors:
        if not isinstance(err, dict):
            continue
        group_id = err.get("group_id")
        if group_id is None:
            continue
        group_key = str(group_id)
        by_group[group_key] = by_group.get(group_key, 0) + 1
    return by_group


async def run_refresh_with_session(
    session: Session,
    source: str,
    refresh_runner: RefreshRunner | None = None,
) -> dict[str, Any]:
    """Run refresh with lock protection; skip when another run is active."""
    run_id = uuid.uuid4().hex
    skip_at = datetime.now(timezone.utc)

    if _refresh_lock.locked():
        logger.info(
            "refresh_event=%s",
            json.dumps(
                {
                    "event": "refresh_skipped",
                    "run_id": run_id,
                    "source": source,
                    "reason": "in-process lock is busy",
                    "at": skip_at.isoformat(),
                },
                ensure_ascii=True,
            ),
        )
        return {"status": "skipped", "reason": "refresh already running"}

    await _refresh_lock.acquire()
    file_fd = None
    try:
        file_fd = _acquire_file_lock(settings.refresh_lock_file)
        if file_fd is None:
            logger.info(
                "refresh_event=%s",
                json.dumps(
                    {
                        "event": "refresh_skipped",
                        "run_id": run_id,
                        "source": source,
                        "reason": "file lock is busy",
                        "at": skip_at.isoformat(),
                    },
                    ensure_ascii=True,
                ),
            )
            return {"status": "skipped", "reason": "refresh already running"}

        if refresh_runner is None:
            from ruz_server.api.lesson import parse_lessons_core

            refresh_runner = parse_lessons_core

        global LAST_REFRESH_AT, LAST_REFRESH_STATUS
        start = time.perf_counter()
        try:
            result = await refresh_runner(session)
        except Exception as exc:
            duration_ms = int((time.perf_counter() - start) * 1000)
            LAST_REFRESH_AT = datetime.now(timezone.utc)
            LAST_REFRESH_STATUS = "error"

            logger.error(
                "refresh_event=%s",
                json.dumps(
                    {
                        "event": "refresh_failed",
                        "run_id": run_id,
                        "source": source,
                        "duration_ms": duration_ms,
                        "error": {"type": type(exc).__name__, "message": str(exc)},
                        "at": LAST_REFRESH_AT.isoformat(),
                    },
                    ensure_ascii=True,
                ),
            )
            raise

        duration_ms = int((time.perf_counter() - start) * 1000)
        LAST_REFRESH_AT = datetime.now(timezone.utc)
        LAST_REFRESH_STATUS = "success"

        lessons_pruned = _safe_int(result.get("lessons_pruned"))
        links_pruned = _safe_int(result.get("links_pruned"))
        errors_by_group = _aggregate_errors_by_group(result)

        logger.info(
            "refresh_event=%s",
            json.dumps(
                {
                    "event": "refresh_completed",
                    "run_id": run_id,
                    "source": source,
                    "duration_ms": duration_ms,
                    "prune": {
                        "lessons_pruned": lessons_pruned,
                        "links_pruned": links_pruned,
                    },
                    "errors_by_group": errors_by_group,
                    "at": LAST_REFRESH_AT.isoformat(),
                },
                ensure_ascii=True,
            ),
        )
        return result
    finally:
        _release_file_lock(settings.refresh_lock_file, file_fd)
        _refresh_lock.release()


async def run_refresh_job(source: str = "scheduler") -> dict[str, Any]:
    """Create DB session and run refresh through shared orchestrator."""
    session_gen = db.get_session()
    session = next(session_gen)
    try:
        return await run_refresh_with_session(session=session, source=source)
    finally:
        session.close()
