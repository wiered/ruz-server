"""Import all SQLModel tables for Alembic metadata registration."""

from sqlmodel import SQLModel

from ruz_server.models import (
    Auditorium,
    Discipline,
    Group,
    KindOfWork,
    Lecturer,
    Lesson,
    LessonGroup,
    User,
)

__all__ = ["load_models", "SQLModel"]


def load_models() -> tuple[type[SQLModel], ...]:
    """Import and return every model class registered in SQLModel metadata."""

    return (
        Auditorium,
        Discipline,
        Group,
        KindOfWork,
        Lecturer,
        Lesson,
        LessonGroup,
        User,
    )
