"""Handles routes related to lists of tasks"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

# Core
from typing import List, Dict
from uuid import UUID

# Fast
from fastapi import APIRouter, Depends, Request
from fastapi.encoders import jsonable_encoder

# Module
from main.dependencies.models import User, TaskList, TaskListInDB
from main.dependencies.user import get_current_user
from main.dependencies.utils import validate_document_owner

# ----------------------------------------------------------------------------
# Set-up
# ----------------------------------------------------------------------------

router = APIRouter()

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


@router.post(
    path="/api/v1/lists",
    response_description="Create a new task list",
    response_model=TaskListInDB,
)
async def create_task_list(
    task_list: TaskList,
    request: Request,
    current_user: User = Depends(get_current_user),
) -> TaskListInDB:
    """Creates a task list

    Args:
        task_list (TaskList): task list in the request
        request (Request): request object to get the database client
        current_user (User, optional): the signed in user

    Returns:
        TaskListInDB: the newly created database entry
    """
    new_task_list = task_list.dict()
    new_task_list["username"] = current_user.username
    new_task_list = TaskListInDB(**new_task_list)
    new_task_list_json = jsonable_encoder(new_task_list)

    # Add to DB
    request.app.database["lists"].insert_one(new_task_list_json)

    result = request.app.database["lists"].find_one(
        filter={"_id": str(new_task_list.dict()["id"])}
    )

    # Return the DB instance
    return TaskListInDB(**result)


@router.delete(path="/api/v1/lists", response_description="Delete a new task list")
async def delete_task_list(
    _id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
) -> None:
    """Deletes a task list

    Args:
        _id (UUID): PK of the task list to delete
        request (Request): request object to get the database client
        current_user (User, optional): the signed in user
    """
    task_mongo: Dict = request.app.database["lists"].find_one(filter={"_id": str(_id)})

    result = validate_document_owner(user=current_user, mongo_result=task_mongo)
    if result is not None:
        raise result

    # Delete the list and the tasks that were in that list
    request.app.database["lists"].delete_one(filter={"_id": str(_id)})
    request.app.database["tasks"].delete_many(filter={"list_id": str(_id)})

    return


@router.get(
    path="/api/v1/lists",
    response_description="Return lists for a current user",
    response_model=List[TaskListInDB],
)
async def get_task_lists(
    request: Request, current_user: User = Depends(get_current_user)
) -> List[TaskListInDB]:
    """Returns all task lists of a user

    Args:
        request (Request): request object to get the database client
        current_user (User, optional): the signed in user

    Returns:
        List[TaskListInDB]: the users task lists
    """
    task_lists_mongo: List[Dict] = list(
        request.app.database["lists"].find(filter={"username": current_user.username})
    )
    return list(map(lambda x: TaskListInDB(**x), task_lists_mongo))
