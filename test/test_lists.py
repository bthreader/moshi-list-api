# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

# Fast
from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder

# Other
import pytest
from asgi_lifespan import LifespanManager
from uuid import UUID

# Module
from main.server import app
from main.dependencies.models import TaskList, TaskListInDB
from test.dependencies import create_access_token, test_user

# ----------------------------------------------------------------------------
# Set-up
# ----------------------------------------------------------------------------

# We run through create -> update -> delete
# Keep the ID between tests to for future reference
TASK_LIST_ID: UUID = None

# ----------------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------------


class TestLists:
    @pytest.mark.asyncio
    async def test_create_task_list(self, create_access_token):
        new_task_list = TaskList(
            name="Huge list of stuff to do :(",
        )

        async with LifespanManager(app):
            with TestClient(app) as client:
                response = client.post(
                    "/api/v1/lists",
                    headers={"Authorization": "Bearer " + create_access_token},
                    json=jsonable_encoder(new_task_list),
                )

                assert response.status_code == 200

                response_task_list = TaskListInDB(**response.json())
                assert response_task_list.name == "Huge list of stuff to do :("
                # assert response_task_list.username == test_user.username
                assert response_task_list.id.version == 4

                global TASK_LIST_ID
                TASK_LIST_ID = response_task_list.id

    @pytest.mark.asyncio
    async def test_delete_task_list(self, create_access_token):
        async with LifespanManager(app):
            with TestClient(app) as client:
                response = client.delete(
                    "/api/v1/lists",
                    params={"_id": TASK_LIST_ID},
                    headers={"Authorization": "Bearer " + create_access_token},
                )

                assert response.status_code == 200
