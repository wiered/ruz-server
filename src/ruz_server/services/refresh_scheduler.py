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
    """
    Attempt to acquire a file-based lock for the refresh process.

    Args:
        lock_path (str): The file path to the lock file.

    Returns:
        int | None: File descriptor if the lock was acquired successfully, or None if the lock already exists.
    """
    path = Path(lock_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    try:
        return os.open(str(path), flags)
    except FileExistsError:
        return None


def _release_file_lock(lock_path: str, fd: int | None) -> None:
    """
    Release the file-based lock for the refresh process.

    Args:
        lock_path (str): The file path to the lock file.
        fd (int | None): File descriptor of the lock file, or None if lock was not acquired.

    Returns:
        None
    """
    if fd is None:
        return
    try:
        os.close(fd)
    finally:
        Path(lock_path).unlink(missing_ok=True)


def get_last_refresh_state() -> dict[str, Any]:
    """
    Get the last completed refresh state.
    This function provides the current refresh status and timestamp,
    which is used by the `/healthz` endpoint to report the freshness
    and outcome (success, error, or never) of the last attempted data refresh.

    Args:
        None

    Returns:
        dict[str, Any]: Dictionary containing:
            - last_refresh_at (datetime | None): Timestamp of the last completed refresh attempt.
            - last_refresh_status (str): Status string indicating the outcome of the last refresh
              ("never", "success", "error", or "skipped").
    """
    return {
        "last_refresh_at": LAST_REFRESH_AT,
        "last_refresh_status": LAST_REFRESH_STATUS,
    }


def _safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert a value to an integer, returning a default if conversion fails
    or if the value is None or a boolean. Used for robust type coercion in contexts
    where a value is expected to be an integer but may be missing or invalid.

    Args:
        value (Any): The value to be converted to int.
        default (int, optional): The value to return if conversion fails. Defaults to 0.

    Returns:
        int: The converted integer value, or the default if conversion was not possible.
    """
    try:
        if value is None or isinstance(value, bool):
            return default
        return int(value)
    except Exception:
        return default


def _aggregate_errors_by_group(result: dict[str, Any]) -> dict[str, int]:
    """
    About:
        Convert parsed refresh errors into counts per group_id.

    Args:
        result (dict[str, Any]): The result of the refresh attempt.

    Returns:
        dict[str, int]: Dictionary containing the count of errors by group_id.
    """
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
    """
    About:
        Runs the refresh procedure using the provided database session and optional refresh runner.
        Ensures that only one refresh can run at a time by using in-process and file locks.
        Handles logging and lock management, and returns a status dictionary describing the outcome.
        If no refresh runner is provided, uses the default lesson parser.

    Args:
        session (Session): The database session for database operations during refresh.
        source (str): A descriptive source string which triggered the refresh.
        refresh_runner (RefreshRunner | None, optional): A coroutine or callable performing the refresh logic.
            If None, uses the default lessons refresh routine.

    Returns:
        dict[str, Any]: A dictionary indicating the status of the refresh (e.g., "skipped", "completed", or error details).
    """
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
    """
    Create DB session and run refresh through shared orchestrator.

    Args:
        source (str): The source of the refresh (e.g., "scheduler" or "startup_doupdate"). Defaults to "scheduler".

    Returns:
        dict[str, Any]: Dictionary containing the result of the refresh.
    """
    session_gen = db.get_session()
    session = next(session_gen)
    try:
        return await run_refresh_with_session(session=session, source=source)
    finally:
        session.close()
