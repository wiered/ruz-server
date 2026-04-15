import uvicorn

from ruz_server.api.app import app
from ruz_server.settings import settings


def run() -> None:
    """
    Runs the FastAPI application using uvicorn server.

    Kept as a callable so tests can assert uvicorn.run kwargs without
    subprocess / __main__ execution.
    """
    host = settings.host
    port = settings.port

    # Для разработки можно включить hot-reload через переменную окружения
    reload_enabled = settings.reload in ("1", "true", "yes")
    # В проде можно скейлить воркеры (игнорируется, если включён reload)
    workers = settings.workers

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload_enabled,
        workers=(1 if reload_enabled else workers),
        proxy_headers=True,
        forwarded_allow_ips="*",
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    run()
