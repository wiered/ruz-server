from secrets import compare_digest

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from settings import settings

API_KEY_HEADER_NAME = "X-API-Key"

api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)

async def require_api_key(api_key: str = Security(api_key_header)) -> str:
    # если заголовка нет — вернуть 401/403
    if not api_key:
        headers = {"WWW-Authenticate": 'ApiKey realm="api"'}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers=headers
        )
    # проверяем на совпадение с любым из допустимых ключей

    if compare_digest(api_key, settings.valid_api_key):
        return api_key

    # неверный ключ
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid API key",
    )
