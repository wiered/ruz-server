import asyncio
import logging
import os
from pathlib import Path
from typing import Any, Awaitable, Callable

from sqlmodel import Session

from ruz_server.database import db
from ruz_server.settings import settings

logger = logging.getLogger(__name__)

RefreshRunner = Callable[[Session], Awaitable[dict[str, Any]]]

_refresh_lock = asyncio.Lock()


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


async def run_refresh_with_session(
    session: Session,
    source: str,
    refresh_runner: RefreshRunner | None = None,
) -> dict[str, Any]:
    """Run refresh with lock protection; skip when another run is active."""
    if _refresh_lock.locked():
        logger.info("Skipping refresh (%s): in-process lock is busy", source)
        return {"status": "skipped", "reason": "refresh already running"}

    await _refresh_lock.acquire()
    file_fd = None
    try:
        file_fd = _acquire_file_lock(settings.refresh_lock_file)
        if file_fd is None:
            logger.info("Skipping refresh (%s): file lock is busy", source)
            return {"status": "skipped", "reason": "refresh already running"}

        if refresh_runner is None:
            from ruz_server.api.lesson import parse_lessons_core

            refresh_runner = parse_lessons_core
        return await refresh_runner(session)
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
