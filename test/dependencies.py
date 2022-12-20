# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

# Core
from typing import Dict

# Other
import pytest
import msal

# Module
from test.config import test_user, config

# ----------------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------------


@pytest.fixture(scope="class")
def create_access_token() -> str:
    """Generates an access token

    Returns:
        str: a Microsoft identity platform access token
    """
    app = msal.PublicClientApplication(
        config["client_id"],
        authority=config["authority"],
    )

    response = app.acquire_token_by_username_password(
        username=test_user.username,
        password=test_user.password,
        scopes=["api://" + config["client_id"] + "/user"],
    )

    return response["access_token"]
