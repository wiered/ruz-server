import uvicorn

from ruz_server.api.app import app
from ruz_server.settings import settings

if __name__ == "__main__":
    """
    Runs the FastAPI application using uvicorn server.

    Args:
        None

    Returns:
        None
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
        log_level=settings.logging_level,
    )
