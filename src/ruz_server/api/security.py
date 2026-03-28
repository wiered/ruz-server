from secrets import compare_digest

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from ruz_server.settings import settings

API_KEY_HEADER_NAME = "X-API-Key"

api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)

async def require_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Dependency to require and validate the API key from the request header.

    Args:
        api_key (str): The API key provided in the 'X-API-Key' header.

    Returns:
        str: Returns None if the API key is valid. Raises HTTPException otherwise.
    """

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": 'ApiKey realm="api"'}
        )

    if compare_digest(api_key, settings.valid_api_key):
        return None

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
        headers={"WWW-Authenticate": 'ApiKey realm="api"'}
    )
