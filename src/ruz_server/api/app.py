import os
import logging
import asyncio
from contextlib import asynccontextmanager
from logging.config import dictConfig
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Request, Security
from fastapi.responses import JSONResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from ruz_server.api.security import require_api_key
from ruz_server.api import api_router
from ruz_server.database.database import db
from ruz_server.services.refresh_scheduler import get_last_refresh_state, run_refresh_job
from ruz_server.settings import settings

from ruz_server.logging_config import LOGGING_CONFIG, ColoredFormatter

# Setup logging
dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.to_thread(db.createAllTables)

    tz = ZoneInfo(settings.refresh_timezone)
    scheduler = AsyncIOScheduler(timezone=tz)
    scheduler.add_job(
        run_refresh_job,
        trigger=CronTrigger(
            hour=settings.refresh_hour,
            minute=settings.refresh_minute,
            timezone=tz,
        ),
        kwargs={"source": "scheduler"},
        id="daily_refresh",
        replace_existing=True,
    )
    scheduler.start()
    app.state.refresh_scheduler = scheduler

    if settings.doupdate:
        asyncio.create_task(run_refresh_job(source="startup_doupdate"))

    try:
        yield
    finally:
        scheduler.shutdown(wait=False)


app = FastAPI(lifespan=lifespan)
app.include_router(api_router, prefix="/api", dependencies=[Security(require_api_key)])

@app.get("/")
async def root(request: Request):
    return {"message": "Hello World"}

@app.get("/public")
async def public():
    logger.info("public ok")
    return {"message": "public ok"}

@app.get("/protected")
async def protected(_: None = Security(require_api_key)):
    logger.info("protected ok")
    return {"message": "protected ok"}

@app.get("/healthz")
async def healthz():
    state = get_last_refresh_state()
    last_refresh_at = state["last_refresh_at"]
    last_refresh_status = state["last_refresh_status"]

    if last_refresh_status in ("never", "error"):
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "last_refresh_at": last_refresh_at.isoformat() if last_refresh_at else None,
                "last_refresh_status": last_refresh_status,
            },
        )

    return {
        "status": "ok",
        "last_refresh_at": last_refresh_at.isoformat() if last_refresh_at else None,
        "last_refresh_status": last_refresh_status,
    }
