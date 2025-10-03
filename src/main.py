import os
import uvicorn

from api.app import app
from settings import settings

if __name__ == "__main__":
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
        log_level=os.getenv("LOG_LEVEL", "info"),
    )