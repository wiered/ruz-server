# main.py
import os
from secrets import compare_digest

from dotenv import load_dotenv
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

load_dotenv()

API_KEY_HEADER_NAME = "X-API-Key"
VALID_API_KEY = os.environ.get("VALID_API_KEY")

api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)

async def require_api_key(api_key: str = Security(api_key_header)) -> str:
    # если заголовка нет — вернуть 401/403
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )
    # проверяем на совпадение с любым из допустимых ключей

    if compare_digest(api_key, VALID_API_KEY):
        return api_key

    # неверный ключ
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid API key",
    )
