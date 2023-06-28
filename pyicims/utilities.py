"""Various utilitis used by the client."""
import os
import requests

from pathlib import Path
from requests import Response

from pydantic import SecretStr
from pyicims.settings import iCIMSCreds
from pyicims.decorators import timed_lru_cache


@timed_lru_cache(seconds=28800)
def generate_auth_token_header() -> dict[str, str]:
    """Retrieves an OAUTH token.

    We are using a specialized lru cache decorator to cache and re-use the access tokens
    between API calls. Access tokens are valid for 24 hours; our cache maintains the
    token for 8 hours (28,000 seconds)

    Warning: iCIMS will throttle or disable access for clients that request more than
    500 access tokens in 10 minutes

    Returns:
        dict[str, str]: authorization header with the access token.
    """
    creds: iCIMSCreds = iCIMSCreds()

    access_token_url: str = creds.access_token_url
    client_id: str = creds.client_id
    client_secret: SecretStr = creds.client_secret
    grant_type: str = "client_credentials"
    audience: str = "https://api.icims.com/v1/"

    # fetch token
    try:
        data = {
            "grant_type": grant_type,
            "client_id": client_id,
            "client_secret": client_secret.get_secret_value(),
            "audience": audience,
        }
        auth_res: Response = requests.post(access_token_url, data=data)
        auth_res.raise_for_status()
    except requests.exceptions.HTTPError as errorh:
        print(f"Http Error: {errorh}")
    except requests.exceptions.ConnectionError as errorc:
        print(f"Error Connecting: {errorc}")
    except requests.exceptions.Timeout as errort:
        print(f"Timeout Error: {errort}")
    except requests.exceptions.RequestException as err:
        print(f"Unknown Error: {err}")

    # read token from auth response
    auth_response_json = auth_res.json()
    auth_token = auth_response_json["access_token"]
    auth_token_header_value = f"Bearer {auth_token}"
    auth_token_header = {"Authorization": auth_token_header_value}

    return auth_token_header


def get_resume_path(file_name: str) -> Path:
    """Retrieve path for storing resumes.

    Args:
        file_name (str): the name of the resume.

    Returns:
        Path: path where the resume should be stored.
    """
    path = Path(__file__).parent.parent / "docs" / "resumes"

    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

    path = path / file_name
    return path


def get_offer_path(file_name: str) -> Path:
    """Retrieve path for storing offer letters.

    Args:
        file_name (str): the name of the offer letter.

    Returns:
        Path: path where the offer letter should be stored.
    """
    path = Path(__file__).parent.parent / "docs" / "offer_letters"

    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

    path = path / file_name
    return path


@timed_lru_cache(seconds=120)
def fetch_files(directory: Path) -> list[str]:
    return os.listdir(directory)


def file_exists(directory: Path, file_name: str) -> bool:
    files = fetch_files(directory)
    for file in files:
        if file.startswith(file_name):
            return True
    return False
