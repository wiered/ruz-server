"""Парсинг ответа поиска групп RUZ (`/api/search?type=group`)."""

import logging
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RuzGroupSearchItem(BaseModel):
    """Одна группа из ответа ruz.mstuca.ru (`/api/search?type=group`)."""

    oid: int = Field(description="Идентификатор группы в RUZ (groupOid)")
    name: str = Field(description="Отображаемое имя группы")
    guid: UUID = Field(description="GUID группы в RUZ")


def parse_ruz_group_search_response(raw: Any) -> list[RuzGroupSearchItem]:
    """
    Разбирает JSON-массив ответа поиска групп RUZ в список моделей.

    Ожидается уже проверенный тип (список); иначе вернётся пустой список.
    """
    if not isinstance(raw, list):
        return []

    items: list[RuzGroupSearchItem] = []
    for row in raw:
        if not isinstance(row, dict):
            continue
        try:
            items.append(
                RuzGroupSearchItem(
                    oid=int(row["id"]),
                    name=str(row["label"]),
                    guid=UUID(str(row["guid"])),
                )
            )
        except (KeyError, TypeError, ValueError):
            logger.debug("Skipping malformed RUZ search row: %r", row)
            continue
    return items
