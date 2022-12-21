"""Utilities for getting information about users"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

# Core
from typing import Dict
import json
from urllib.request import urlopen

# Fast
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException

# Other
from jose import jwt
from jose.backends.base import Key

# Module
from main.config import config
from main.dependencies.models import User

# ----------------------------------------------------------------------------
# Set-up
# ----------------------------------------------------------------------------

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="fuckoff")

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Returns the current user provided their JWT is valid and they have the
    required security_scopes.

    Args:
        security_scopes (SecurityScopes): The scopes the token must contain
        token (str, optional): JWT

    Returns:
        User: Identifies the token sender to the backend
    """
    # Validate the key
    key = validate_key(token=token)

    # Validate the payload
    payload = validate_payload(
        token=token,
        key=key,
    )

    return User(username=payload.get("sub"))


def validate_key(token: str) -> Dict[str, str]:
    """Cross references MSFT JWKS with the key provided in the JWT header

    Args:
        token (str): JWT

    Returns:
        Dict[str, str]: full details of (verified) RSA key provided in header
    """
    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.JWTError as exc:
        raise HTTPException(401, "Unable to decode token header") from exc

    # Get the JSON Web Key Set from MSFT for the tenant
    jsonurl = urlopen(
        "https://login.microsoftonline.com/"
        + config["TENANT_ID"]
        + "/discovery/v2.0/keys"
    )
    jwks = json.loads(jsonurl.read())

    # Iterate through the keys to see which one was used and save it
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }
    if not rsa_key:
        raise HTTPException(401, "Unable to find appropriate key")

    return rsa_key


def validate_payload(token: str, key: Key):
    """Takes a JWT, gets the JWKS then validates the payload of the JWT

    Args:
        token (str): JWT
        key (Key): the key used to encrypt the JWT

    Returns:
        str: (validated) payload
    """
    try:
        payload = jwt.decode(
            token=token, key=key, algorithms=["RS256"], audience=config["CLIENT_ID"]
        )

    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(401, "Token is expired") from exc

    except jwt.JWTClaimsError as exc:
        raise HTTPException(401, "Incorrect claims") from exc

    except Exception as exc:
        raise HTTPException(401, "Unable to parse token") from exc

    return payload
