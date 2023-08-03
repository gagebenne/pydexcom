import os
import re
from typing import Any
from uuid import UUID

import pytest

from pydexcom import DEFAULT_UUID, DEXCOM_APPLICATION_ID

r_UUID = r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}"

TEST_USERNAME = "u$ern@me"
TEST_PASSWORD = "p@$$w0rd"
TEST_ACCOUNT_ID = "99999999-9999-9999-9999-999999999999"
TEST_SESSION_ID = "55555555-5555-5555-5555-555555555555"

USERNAME = os.environ.get("DEXCOM_USERNAME", TEST_USERNAME)
PASSWORD = os.environ.get("DEXCOM_PASSWORD", TEST_PASSWORD)
ACCOUNT_ID = os.environ.get("DEXCOM_ACCOUNT_ID", TEST_ACCOUNT_ID)
SESSION_ID = os.environ.get("DEXCOM_SESSION_ID", TEST_SESSION_ID)

TEST_SESSION_ID_EXPIRED = "33333333-3333-3333-3333-333333333333"


def is_uuid(uuid: Any) -> bool:
    try:
        UUID(uuid)
        return True
    except (ValueError, AttributeError):
        return False


def scrub_sub(match: re.Match[str]) -> str:
    if match.group() == USERNAME:
        print("Scrubbed username")
        return TEST_USERNAME
    if match.group() == PASSWORD:
        print("Scrubbed password")
        return TEST_PASSWORD
    if match.group() == ACCOUNT_ID:
        print("Scrubbed account ID")
        return TEST_ACCOUNT_ID
    if match.group() in [
        DEXCOM_APPLICATION_ID,
        TEST_ACCOUNT_ID,
        TEST_SESSION_ID_EXPIRED,
        DEFAULT_UUID,
    ]:
        return match.group()
    print("Scrubbed session ID")
    return TEST_SESSION_ID


def scrub_response(response: dict[str, Any]) -> dict[str, Any]:
    if response["headers"].get("Content-Encoding") == ["gzip"]:
        return response
    body = response["body"]["string"].decode()

    body = re.sub(
        rf"({USERNAME}|{PASSWORD}|{r_UUID})",
        scrub_sub,
        body,
    )

    response["body"]["string"] = body.encode()

    return response


def scrub(key: str, value: Any, request: Any) -> Any:
    if isinstance(value, str):
        return re.sub(rf"({USERNAME}|{PASSWORD}|{r_UUID})", scrub_sub, value)
    return value


def scrub_path(path: str) -> str:
    return re.sub(rf"({USERNAME}|{PASSWORD}|{r_UUID})", scrub_sub, path) + ".yaml"


@pytest.fixture(scope="module")
def vcr_config() -> dict[str, Any]:
    return {
        "filter_post_data_parameters": [
            ("accountName", scrub),
            ("accountId", scrub),
            ("password", scrub),
        ],
        "filter_query_parameters": [
            ("sessionId", scrub),
        ],
        "before_record_response": scrub_response,
        "match_on": ["uri", "method", "path", "query", "body"],
        "path_transformer": scrub_path,
    }
