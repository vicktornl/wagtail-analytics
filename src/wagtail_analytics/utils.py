import json

from oauth2client.service_account import ServiceAccountCredentials

SCOPE = "https://www.googleapis.com/auth/analytics.readonly"


def get_access_token_from_string(value: str) -> str:
    value = value.replace("\n", "").replace("\r", "")

    json_keyfile_dict = json.loads(value)

    service_account_credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        json_keyfile_dict, SCOPE
    )

    access_token = service_account_credentials.get_access_token().access_token
    return access_token
