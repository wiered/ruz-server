from fastapi import HTTPException, status

def ensure_entity_exists(value, function):
    """Ensures that the object with the given value exists in the database.

    Args:
        value: The value to search for a corresponding entity by.
        function: A function that takes in a value and returns an entity object,
            or None if the entity does not exist.

    Returns:
        The entity object if it exists, or raises a 404 error if it does not.
    """
    entity = function(value)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Error: Not Found"
        )

    return entity

def ensure_entity_doesnot_exist(value, function) -> None:
    """Ensures that the kind of work with the given ID does not exist in the database.

    If the kind of work with the given ID already exists, a 409 error is raised.
    Otherwise, the function does nothing.

    Args:
        kind_of_work_id (int): The ID of the kind of work to check for existence.
        session (Session): The database session to use for the operation.
    """
    entity = function(value)
    if entity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Error: Conflict"
        )
