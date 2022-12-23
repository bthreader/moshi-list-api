"""Handles routes related to tasks"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

# Core
from typing import List, Dict, Optional
from uuid import UUID

# Fast
from fastapi import Depends, APIRouter, Request
from fastapi.encoders import jsonable_encoder

# Module
from main.dependencies.models import Task, TaskInDB, TaskUpdate, User
from main.dependencies.user import get_current_user
from main.dependencies.utils import validate_document_owner, repeated_entry

# ----------------------------------------------------------------------------
# Set-up
# ----------------------------------------------------------------------------

router = APIRouter(prefix="/api/v1/tasks")

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


@router.get(
    path="",
    response_description="Returns tasks relating to a certain list for a current user",
    response_model=List[TaskInDB],
)
async def read_tasks(
    list_id: UUID,
    complete: bool,
    request: Request,
    pinned: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
) -> List[TaskInDB]:
    """Returns tasks relating to a certain list (list_id) for a current user

    Args:
        list_id (UUID): PK of the list
        complete (bool): if true returns tasks that are complete
        request (Request): request object to get the database client
        current_user (User, optional): the signed in user

    Returns:
        List[TaskInDB]: the tasks for the given list
    """
    database_filter = {
        "username": current_user.username,
        "list_id": str(list_id),
        "complete": complete
    }

    if pinned is not None:
        database_filter['pinned'] = pinned

    tasks = list(
        request.app.database["tasks"].find(filter=database_filter)
    )

    return tasks


@router.post(
    path="", response_description="Creates a new task", response_model=TaskInDB
)
async def create_task(
    task: Task,
    request: Request,
    current_user: User = Depends(get_current_user),
) -> TaskInDB:
    """Creates a new task

    Args:
        task (Task): the task to be created
        request (Request): request object to get the database client
        current_user (User, optional): the signed in user

    Returns:
        TaskInDB: the newly created task database entry
    """
    new_task = task.dict()
    new_task["username"] = current_user.username
    new_task = TaskInDB(**new_task)
    new_task_json = jsonable_encoder(new_task)

    # Add to DB
    request.app.database["tasks"].insert_one(new_task_json)

    result = request.app.database["tasks"].find_one(
        filter={"_id": str(new_task.dict()["id"])}
    )

    # Return the DB instance
    return TaskInDB(**result)


@router.put(path="", response_description="Updates a task", response_model=TaskInDB)
async def update_task(
    _id: UUID,
    task_update: TaskUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
) -> TaskInDB:
    """Updates a task

    Args:
        _id (UUID): id of the task to update
        task_update (TaskUpdate): the changes to make
        request (Request): request object to get the database client
        current_user (User, optional): the signed in user

    Returns:
        TaskInDB: the newly updated task database entry
    """
    old_task_mongo: Dict = request.app.database["tasks"].find_one(
        filter={"_id": str(_id)}
    )

    result = validate_document_owner(user=current_user, mongo_result=old_task_mongo)
    if result is not None:
        raise result

    # Make the necessary adjustments to the entry
    # > Ignore empty text (for example no entry to notes)
    # > Ignore non-changing requests
    request.app.database["tasks"].update_one(
        {"_id": str(_id)},
        {
            "$set": {
                key: item
                for key, item in dict(task_update).items()
                if (
                    (item not in ["", None])
                    and not repeated_entry(
                        old_document=old_task_mongo, key=key, new_value=item
                    )
                )
            }
        },
    )

    # Return the DB instance
    return TaskInDB(**request.app.database["tasks"].find_one(filter={"_id": str(_id)}))


@router.delete(path="", response_description="Delete a task")
async def delete_task(
    _id: UUID, request: Request, current_user: User = Depends(get_current_user)
) -> None:
    """Deletes a task

    Args:
        _id (UUID): id of the task to delete
        request (Request): request object to get the database client
        current_user (User, optional): the signed in user
    """
    task_mongo: Dict = request.app.database["tasks"].find_one(filter={"_id": str(_id)})

    result = validate_document_owner(user=current_user, mongo_result=task_mongo)
    if result is not None:
        raise result

    request.app.database["tasks"].delete_one(filter={"_id": str(_id)})

    return
