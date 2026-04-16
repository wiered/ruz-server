"""Defaults for persisting group ``faculty_name``."""

NO_FACULTY_DB_VALUE = "no_faculty"


def persisted_faculty_name(faculty_name: str | None) -> str:
    """Return the string stored in ``Group.faculty_name`` for API input."""
    if faculty_name is None:
        return NO_FACULTY_DB_VALUE
    stripped = faculty_name.strip()
    if not stripped:
        return NO_FACULTY_DB_VALUE
    return stripped
