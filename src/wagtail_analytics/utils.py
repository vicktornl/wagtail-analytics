import json

from google.auth.transport.requests import Request
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]


def get_access_token_from_string(value: str) -> str:
    value = value.replace("\n", "").replace("\r", "")

    json_keyfile_dict = json.loads(value)

    service_account_credentials = service_account.Credentials.from_service_account_info(
        json_keyfile_dict
    )

    scoped_credentials = service_account_credentials.with_scopes(SCOPES)

    if not scoped_credentials.token:
        request = Request()
        scoped_credentials.refresh(request)

    access_token = scoped_credentials.token
    return access_token
