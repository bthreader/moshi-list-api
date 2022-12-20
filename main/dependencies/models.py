"""The data structures used by the API"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from typing import Optional

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
    # Secondary key
    list_id: UUID
    notes: Optional[str]
    complete: bool = False

    class Config:
        schema_extra = {
            "example": {
                "task": "Water the plants",
            }
        }


class TaskInDB(Task):
    username: str

    # mongo uses _id
    # field names cannot start with an underscore
    # -> use alias
    id: UUID = Field(default_factory=uuid4, alias="_id")

    class Config:
        schema_extra = {
            "example": {
                "_id": "14eae223-3628-45a4-acbf-ca71707c9cd0",
                "username": "johnsmith",
                "task": "Water the plants",
                "complete": False,
            }
        }


class TaskUpdate(BaseModel):
    task: Optional[str]
    list_id: Optional[UUID]
    notes: Optional[str]
    complete: Optional[bool]

    class Config:
        schema_extra = {
            "example": {
                "task": "My task without the previous typo...",
                "notes": "And don't forget to add XYZ",
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
