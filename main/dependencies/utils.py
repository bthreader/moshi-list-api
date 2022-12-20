"""Utilities shared across the app"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

# Core
from typing import Dict, Union

# Fast
from fastapi import HTTPException

# Module
from main.dependencies.models import User

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


def validate_document_owner(
    user: User, mongo_result: Dict
) -> Union[HTTPException, None]:
    """Compares the user with the document which the request would operate on

    * Ensures there is a document returned by the mongo query
    * Ensures that the requesting user is the owner of that document

    Args:
        user (User): the User requesting the document operation
        mongo_result (Dict): the result from the DB when using the users request

    Returns:
        HTTPException | None: An expection to raise in the route if required
    """
    invalid_id = HTTPException(
        status_code=400,
        detail="Invalid document, ensure the document exists and you are the owner",
    )

    if mongo_result is None:
        return invalid_id

    if mongo_result["username"] != user.username:
        return invalid_id
