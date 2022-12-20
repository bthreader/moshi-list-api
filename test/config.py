# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

from dataclasses import dataclass
from dotenv import load_dotenv
import os

# ----------------------------------------------------------------------------
# Set-up
# ----------------------------------------------------------------------------

load_dotenv()


@dataclass
class TestUser:
    username: str
    password: str
    sub: str


test_user = TestUser(
    username=os.environ["TEST_USER_USERNAME"],
    password=os.environ["TEST_USER_PASSWORD"],
    sub=os.environ["TEST_USER_SUB"],
)

config = {
    "client_id": os.environ["AZ_CLIENT_ID"],
    "authority": "https://login.microsoftonline.com/" + os.environ["AZ_TENANT_ID"],
}
