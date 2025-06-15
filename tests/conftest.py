"""pytest configuration for pydexcom package tests."""

import logging
import os
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Union
from uuid import UUID

import pytest
from vcr import VCR
from vcr.cassette import Cassette
from vcr.record_mode import RecordMode
from vcr.request import Request

from pydexcom.const import DEFAULT_UUID, Region

LOGGER = logging.getLogger(__name__)

TEST_USERNAME = "u$ern@me"
TEST_PASSWORD = "p@$$w0rd"  # noqa: S105
TEST_ACCOUNT_ID = "99999999-9999-9999-9999-999999999999"
TEST_SESSION_ID = "55555555-5555-5555-5555-555555555555"
TEST_SESSION_ID_EXPIRED = "33333333-3333-3333-3333-333333333333"

USERNAME = os.environ.get("DEXCOM_USERNAME", TEST_USERNAME)
PASSWORD = os.environ.get("DEXCOM_PASSWORD", TEST_PASSWORD)
ACCOUNT_ID = os.environ.get("DEXCOM_ACCOUNT_ID", TEST_ACCOUNT_ID)
REGION = os.environ.get("DEXCOM_REGION", Region.US)


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add VCR.py options to pytest."""
    group = parser.getgroup("vcr")
    group.addoption(
        "--record-mode",
        action="store",
        dest="vcr_record_mode",
        default=RecordMode.NONE,
        type=RecordMode,
        choices=list(RecordMode),
        help="Set the recording mode for VCR.py",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Add VCR.py markers to pytest."""
    config.addinivalue_line("markers", "vcr: mark the test as using VCR.py.")

    # Check if the test is not running in a CI environment
    if config.getoption("vcr_record_mode") != RecordMode.NONE:
        assert USERNAME != TEST_USERNAME
        assert PASSWORD != TEST_PASSWORD
        assert ACCOUNT_ID != TEST_ACCOUNT_ID


@pytest.fixture(scope="session")
def record_mode(request: pytest.FixtureRequest) -> RecordMode:
    """Return the record mode for VCR.py."""
    return request.config.getoption("vcr_record_mode", RecordMode.NONE)


SENSITIVE_DATA = re.compile(rf"({USERNAME}|{PASSWORD}|{ACCOUNT_ID})")


def _scrub_sensitive_data(match: re.Match) -> str:
    if match.group() == USERNAME:
        LOGGER.warning("Scrubbed username")
        return TEST_USERNAME
    if match.group() == PASSWORD:
        LOGGER.warning("Scrubbed password")
        return TEST_PASSWORD
    if match.group() == ACCOUNT_ID:
        LOGGER.warning("Scrubbed account ID")
        return TEST_ACCOUNT_ID
    return match.group()


def scrub_sensitive_data(string: str) -> str:
    """Scrub sensitive data from the string."""
    return SENSITIVE_DATA.sub(
        _scrub_sensitive_data,
        string,
    )


def scrub_response(response: dict[str, Any]) -> dict[str, Any]:
    """Scrub sensitive data from the response."""
    if response["headers"].get("Content-Type") == ["application/json"]:
        body = response["body"]["string"].decode()
        try:
            uuid = UUID(body.strip('"'))
            if str(uuid) in {TEST_ACCOUNT_ID, TEST_SESSION_ID, DEFAULT_UUID}:
                pass
            # Replace account ID with test account ID
            elif uuid == UUID(ACCOUNT_ID):
                LOGGER.warning("Scrubbed account ID %s with %s", uuid, TEST_ACCOUNT_ID)
                body = body.replace(str(uuid), TEST_ACCOUNT_ID)
            # Replace session ID with test session ID
            else:
                LOGGER.warning("Scrubbed session ID %s with %s", uuid, TEST_SESSION_ID)
                body = body.replace(str(uuid), TEST_SESSION_ID)
        except ValueError:
            pass
        response["body"]["string"] = body.encode()
    return response


def scrub_parameter(key: str, value: Any, request: Request) -> Any:  # noqa: ANN401, ARG001
    """Scrub sensitive data from the request parameters."""
    if isinstance(value, str):
        return scrub_sensitive_data(value)
    return value


def scrub_session_id(key: str, value: Any, request: Request) -> Any:  # noqa: ANN401, ARG001
    """Scrub session ID from the request query."""
    try:
        uuid = UUID(value)
        # Replace session ID with test session ID
        if str(uuid) not in {TEST_SESSION_ID_EXPIRED, DEFAULT_UUID}:
            LOGGER.warning("Scrubbed session ID %s with %s", uuid, TEST_SESSION_ID)
            return TEST_SESSION_ID
    except ValueError:
        return value


def scrub_path(path: str) -> str:
    """Scrub sensitive data from the cassette path."""
    return scrub_sensitive_data(path)


@pytest.fixture(scope="session")
def vcr(
    request: pytest.FixtureRequest,
    record_mode: RecordMode,
) -> VCR:
    """Generate a VCR fixture."""
    return VCR(
        filter_post_data_parameters=[
            ("accountName", scrub_parameter),
            ("accountId", scrub_parameter),
            ("password", scrub_parameter),
        ],
        filter_query_parameters=[
            ("sessionId", scrub_session_id),
        ],
        before_record_response=scrub_response,
        match_on=["uri", "method", "path", "query", "body"],
        path_transformer=scrub_path,
        record_mode=record_mode,
        cassette_library_dir=str(Path(request.config.rootpath) / "tests" / "cassettes"),
    )


def cassette_path(
    request: pytest.FixtureRequest,
    *,
    autouse: bool = False,
) -> str:
    """Generate a cassette path based on the request fixture."""
    cassette_path: Path = Path()

    if module := getattr(request, "module", None):
        cassette_path /= Path(*module.__name__.split("."))

    if cls := getattr(request, "cls", None):
        # Class scoped fixture used in class.
        cassette_path /= cls.__name__
    elif request.scope == "class":
        # Class scoped fixture used in function.
        cassette_path /= request.node.name

    if getattr(request, "function", None):
        cassette_path /= request.node.name

    if request.scope in {"session", "package", "module"}:
        cassette_path /= request.fixturename or request.node.name
    else:
        cassette_path /= (
            request.node.name if autouse else (request.fixturename or request.node.name)
        )

    return str(cassette_path.with_suffix(".yaml"))


@pytest.fixture(autouse=True)
def _vcr_marker_autouse(
    request: pytest.FixtureRequest,
    vcr: VCR,
) -> Iterator[Union[Cassette, None]]:
    if request.node.get_closest_marker("vcr"):
        with vcr.use_cassette(cassette_path(request, autouse=True)) as cassette:
            yield cassette
    else:
        yield None
