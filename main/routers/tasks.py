"""Handles routes related to managing tasks"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

# Core
from filecmp import dircmp
from typing import List, Dict
from uuid import UUID

# Fast
from fastapi import Depends, APIRouter, Request, HTTPException
from fastapi.encoders import jsonable_encoder

# Other
from pydantic.error_wrappers import ValidationError
from pymongo.results import UpdateResult

# Module
from main.dependencies.models import Task, TaskInDB, TaskUpdate, User
from main.dependencies.user import get_current_user
from main.dependencies.utils import validate_document_owner

# ----------------------------------------------------------------------------
# Set-up
# ----------------------------------------------------------------------------

router = APIRouter(prefix="/api/v1/tasks")

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


@router.get(
    path="",
    response_description="Return tasks for a current user",
    response_model=List[TaskInDB],
)
async def read_tasks(
    list_id: UUID,
    complete: bool,
    request: Request,
    current_user: User = Depends(get_current_user),
):
    tasks = list(
        request.app.database["tasks"].find(
            filter={
                "username": current_user.username,
                "list_id": str(list_id),
                "complete": complete,
            }
        )
    )

    return tasks


@router.post(path="", response_description="Create a new task", response_model=TaskInDB)
async def create_task(
    task: Task,
    request: Request,
    current_user: User = Depends(get_current_user),
):
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


@router.put(path="", response_description="Update a task", response_model=TaskInDB)
async def update_task(
    _id: UUID,
    task_update: TaskUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
):
    old_task_mongo: Dict = request.app.database["tasks"].find_one(
        filter={"_id": str(_id)}
    )

    result = validate_document_owner(user=current_user, mongo_result=old_task_mongo)
    if result is not None:
        raise result

    # Make the necessary adjustments to the entry
    request.app.database["tasks"].update_one(
        {"_id": str(_id)},
        {
            "$set": {
                key: item for key, item in dict(task_update).items() if item is not None
            }
        },
    )

    # Return the DB instance
    return TaskInDB(**request.app.database["tasks"].find_one(filter={"_id": str(_id)}))


@router.delete(path="", response_description="Delete a task")
async def delete_task(
    _id: UUID, request: Request, current_user: User = Depends(get_current_user)
):
    task_mongo: Dict = request.app.database["tasks"].find_one(filter={"_id": str(_id)})

    result = validate_document_owner(user=current_user, mongo_result=task_mongo)
    if result is not None:
        raise result

    request.app.database["tasks"].delete_one(filter={"_id": str(_id)})

    return
