from secrets import compare_digest

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from settings import settings

API_KEY_HEADER_NAME = "X-API-Key"

api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)

async def require_api_key(api_key: str = Security(api_key_header)) -> str:
    # если заголовка нет — вернуть 401/403
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": 'ApiKey realm="api"'}
        )
    # проверяем на совпадение с любым из допустимых ключей

    if compare_digest(api_key, settings.valid_api_key):
        return None

    # неверный ключ
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
        headers={"WWW-Authenticate": 'ApiKey realm="api"'}
    )
