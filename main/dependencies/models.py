"""The data structures used by the API"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


# ----------------------------------------------------------------------------
# User
# ----------------------------------------------------------------------------


class User(BaseModel):
    username: str


# ----------------------------------------------------------------------------
# Task
# ----------------------------------------------------------------------------


class Task(BaseModel):
    task: str
    list_id: UUID  # Secondary key
    notes: Optional[str]
    complete: bool = False
    pinned: bool = False

    class Config:
        schema_extra = {
            "example": {
                "task": "Water the plants",
                "list_id": "4c2bb70c-31df-4193-9dc5-6405c5dc21c8",
                "complete": True,
                "pinned": False,
            }
        }


class TaskInDB(Task):
    username: str

    # mongo uses _id
    # field names cannot start with an underscore
    # -> use alias
    id: UUID = Field(default_factory=uuid4, alias="_id")


class TaskUpdate(BaseModel):
    task: Optional[str]
    list_id: Optional[UUID]
    notes: Optional[str]
    complete: Optional[bool]
    pinned: Optional[bool]

    class Config:
        schema_extra = {
            "example": {
                "task": "My task without the previous typo...",
                "notes": "And don't forget to add some notes",
                "complete": True,
            }
        }


# ----------------------------------------------------------------------------
# List
# ----------------------------------------------------------------------------


class TaskList(BaseModel):
    name: str


class TaskListInDB(TaskList):
    username: str
    id: UUID = Field(default_factory=uuid4, alias="_id")
