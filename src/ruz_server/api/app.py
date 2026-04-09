import os
import logging
import asyncio
from contextlib import asynccontextmanager
from logging.config import dictConfig
from zoneinfo import ZoneInfo
from importlib.metadata import version, PackageNotFoundError

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

try:
    __version__ = version("ruz-server")
except PackageNotFoundError:
    __version__ = "0.0.0"

# Setup logging
dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app.

    This function manages application startup and shutdown events. It initializes database tables,
    configures and starts the APScheduler for periodic background jobs (such as the daily refresh job),
    and performs any necessary startup actions like triggering an update if specified in settings.
    On app shutdown, it ensures that the scheduler is properly shut down.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None: Used for FastAPI's lifespan event handling.
    """
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


app = FastAPI(
    lifespan=lifespan,
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url="/redoc" if settings.enable_docs else None,
    openapi_url="/openapi.json" if settings.enable_docs else None,
    title="RUZ Server API",
    description="API for the RUZ Server",
    version=__version__,
    license_info={
        "name": "MIT License",
        "url": "https://github.com/ruz-server/LICENSE",
    }
    )
app.include_router(api_router, prefix="/api", dependencies=[Security(require_api_key)])

@app.get("/")
async def root(request: Request):
    """
    Root endpoint for the API.

    This endpoint returns a simple greeting message. It can be used to check that the API is up and responding.

    Args:
        request (Request): The incoming HTTP request object.

    Returns:
        dict: A JSON object containing a greeting message.
    """
    return {"message": "Hello World"}

@app.get("/public")
async def public():
    """
    Public endpoint that returns a simple message.

    This endpoint can be accessed without authentication and is useful for verifying the service is running.

    Returns:
        dict: A JSON object indicating public access is successful.
    """
    logger.info("public ok")
    return {"message": "public ok"}

@app.get("/protected")
async def protected(_: None = Security(require_api_key)):
    """
    Protected endpoint that requires API key authentication.

    This endpoint can only be accessed if a valid API key is provided.
    It is commonly used to verify that protected routes and API key validation are functioning.

    Args:
        _ (None): Dependency-injected placeholder to enforce API key security.

    Returns:
        dict: A JSON object indicating protected access is successful.
    """
    logger.info("protected ok")
    return {"message": "protected ok"}

@app.get("/healthz")
async def healthz():
    """
    Health check endpoint for the API.

    This endpoint is used to determine whether the service is running and able to respond to requests.
    It examines the last refresh state of the backend to report the status.

    Returns:
        JSONResponse or dict: Returns a JSON response with status "degraded" and 503 code if
            the last refresh failed or was never performed, or a status "ok" if healthy.
    """
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

@app.get("/version")
async def version():
    """
    Version endpoint for the API.

    Returns:
        dict: A JSON object containing the version of the API.
    """
    return {"version": __version__}