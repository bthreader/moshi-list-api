"""Sets up environment for main/"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import os
from dotenv import load_dotenv

# ----------------------------------------------------------------------------
# Set-up
# ----------------------------------------------------------------------------

load_dotenv()

config = {
    "ATLAS_URI": os.environ["ATLAS_URI"],
    "DB_NAME": os.environ["ATLAS_DB_NAME"],
    "TENANT_ID": os.environ["AZ_TENANT_ID"],
    "CLIENT_ID": os.environ["AZ_CLIENT_ID"],
}
