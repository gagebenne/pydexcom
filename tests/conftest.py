import os
import re
from pathlib import Path
from typing import Any, Dict, Generator
from uuid import UUID

import pytest
from vcr import VCR
from vcr.record_mode import RecordMode

from pydexcom import DEFAULT_UUID, DEXCOM_APPLICATION_IDS

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


def scrub_sub(match: re.Match) -> str:
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
        *DEXCOM_APPLICATION_IDS.values(),
        TEST_ACCOUNT_ID,
        TEST_SESSION_ID_EXPIRED,
        DEFAULT_UUID,
    ]:
        return match.group()
    print("Scrubbed session ID")
    return TEST_SESSION_ID


def scrub_response(response: Dict[str, Any]) -> Dict[str, Any]:
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


def scrub(key: str, value: Any, request: pytest.FixtureRequest) -> Any:  # type: ignore
    if isinstance(value, str):
        return re.sub(
            rf"({USERNAME}|{PASSWORD}|{r_UUID})",
            scrub_sub,  # type: ignore
            value,
        )
    return value


def scrub_path(path: str) -> str:
    return re.sub(rf"({USERNAME}|{PASSWORD}|{r_UUID})", scrub_sub, path) + ".yaml"


def pytest_addoption(parser: pytest.Parser) -> None:  # type: ignore
    group = parser.getgroup("vcr")
    group.addoption(
        "--record-mode",
        action="store",
        dest="vcr_record",
        default=None,
        choices=["once", "new_episodes", "none", "all"],
        help="Set the recording mode for VCR.py",
    )


def pytest_configure(config: pytest.Config) -> None:  # type: ignore
    config.addinivalue_line("markers", "vcr: mark the test as using VCR.py.")


@pytest.fixture(scope="package")
def vcr(request: pytest.FixtureRequest) -> VCR:  # type: ignore
    return VCR(
        filter_post_data_parameters=[
            ("accountName", scrub),
            ("accountId", scrub),
            ("password", scrub),
        ],
        filter_query_parameters=[
            ("sessionId", scrub),
        ],
        before_record_response=scrub_response,
        match_on=["uri", "method", "path", "query", "body"],
        path_transformer=scrub_path,
        record_mode=RecordMode(request.config.getoption("--record-mode") or "none"),
        cassette_library_dir=str(request.path.parent),
    )


def vcr_cassette_path(request: Any, fixture: bool = False) -> str:  # type: ignore
    path = Path("cassettes")
    name = Path(
        (request.fixturename if fixture else request.node.name) or pytest.fail()
    )
    if request.scope == "session":
        return str(path / name)

    path = path / request.path.stem
    if request.scope == "module":
        return str(path / name)

    if request.cls:
        name = request.cls.__name__ / name

    return str(path / name)


@pytest.fixture(autouse=True)
def _vcr_marker(request: pytest.FixtureRequest, vcr: VCR) -> Generator:  # type: ignore
    if request.node.get_closest_marker("vcr"):
        with vcr.use_cassette(vcr_cassette_path(request)) as cassette:
            yield cassette
