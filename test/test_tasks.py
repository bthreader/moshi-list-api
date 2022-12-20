# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

# Core
from typing import Dict
import pytest

# Fast
from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder

# Other
from asgi_lifespan import LifespanManager
from uuid import UUID

# Module
from main.server import app
from main.dependencies.models import Task, TaskUpdate, TaskInDB, TaskList, TaskListInDB
from test.dependencies import create_access_token

# ----------------------------------------------------------------------------
# Set-up
# ----------------------------------------------------------------------------


@pytest.fixture(scope="class")
async def create_task_list(create_access_token) -> UUID:
    # Set up
    new_task_list = TaskList(name="Dummy List")

    async with LifespanManager(app):
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/lists",
                headers={"Authorization": "Bearer " + create_access_token},
                json=jsonable_encoder(new_task_list),
            )
            created_task_list = TaskListInDB(**response.json())
            yield created_task_list.id

    # Teardown
    async with LifespanManager(app):
        with TestClient(app) as client:
            client.delete(
                "/api/v1/lists",
                params={"_id": created_task_list.id},
                headers={"Authorization": "Bearer " + create_access_token},
            )


@pytest.fixture(scope="class")
def context():
    return {}


# ----------------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------------


class TestTasks:
    @pytest.mark.asyncio
    async def test_create_task(
        self, create_access_token: str, create_task_list: UUID, context: Dict
    ):
        async for value in create_task_list:
            task_list_id = value

        new_task = Task(
            task="Water the plants", notes="Don't drown them!!", list_id=task_list_id
        )

        async with LifespanManager(app):
            with TestClient(app) as client:
                response = client.post(
                    "/api/v1/tasks",
                    headers={"Authorization": "Bearer " + create_access_token},
                    json=jsonable_encoder(new_task),
                )

                assert response.status_code == 200

                response_task = TaskInDB(**response.json())
                assert response_task.task == "Water the plants"
                assert response_task.notes == "Don't drown them!!"
                assert response_task.complete == False
                assert response_task.id.version == 4

                context["task_id"] = response_task.id

    @pytest.mark.asyncio
    async def test_update_task(self, create_access_token, context):
        # Change complete to true
        updated_task = TaskUpdate(complete=True)

        async with LifespanManager(app):
            with TestClient(app) as client:
                response = client.put(
                    "/api/v1/tasks",
                    params={"_id": context["task_id"]},
                    headers={"Authorization": "Bearer " + create_access_token},
                    json=jsonable_encoder(updated_task),
                )

                assert response.status_code == 200

                response_task = TaskInDB(**response.json())
                assert response_task.complete

    @pytest.mark.asyncio
    async def test_delete_task(self, create_access_token, context):
        async with LifespanManager(app):
            with TestClient(app) as client:
                response = client.delete(
                    "/api/v1/tasks",
                    params={"_id": context["task_id"]},
                    headers={"Authorization": "Bearer " + create_access_token},
                )

                assert response.status_code == 200
