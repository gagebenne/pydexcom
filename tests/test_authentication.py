"""Test authentication."""
from typing import Type

import pytest
import requests

from pydexcom import (
    ACCOUNT_ERROR_PASSWORD_INVALID,
    ACCOUNT_ERROR_PASSWORD_NULL_EMPTY,
    ACCOUNT_ERROR_USERNAME_NULL_EMPTY,
    DEFAULT_SESSION_ID,
    DEXCOM_APPLICATION_ID,
    DEXCOM_BASE_URL,
    DEXCOM_LOGIN_ID_ENDPOINT,
    AccountError,
    Dexcom,
)
from pydexcom.errors import DexcomError

from . import PASSWORD, USERNAME


@pytest.mark.parametrize(
    "input, output, reason",
    [
        ([None, None], AccountError, ACCOUNT_ERROR_USERNAME_NULL_EMPTY),
        (["", None], AccountError, ACCOUNT_ERROR_USERNAME_NULL_EMPTY),
        ([None, ""], AccountError, ACCOUNT_ERROR_USERNAME_NULL_EMPTY),
        (["", ""], AccountError, ACCOUNT_ERROR_USERNAME_NULL_EMPTY),
        (["a", None], AccountError, ACCOUNT_ERROR_PASSWORD_NULL_EMPTY),
        (["a", ""], AccountError, ACCOUNT_ERROR_PASSWORD_NULL_EMPTY),
        ([None, "a"], AccountError, ACCOUNT_ERROR_USERNAME_NULL_EMPTY),
        (["", "a"], AccountError, ACCOUNT_ERROR_USERNAME_NULL_EMPTY),
        ([USERNAME, None], AccountError, ACCOUNT_ERROR_PASSWORD_NULL_EMPTY),
        ([USERNAME, ""], AccountError, ACCOUNT_ERROR_PASSWORD_NULL_EMPTY),
        ([USERNAME, "a"], AccountError, ACCOUNT_ERROR_PASSWORD_INVALID),
    ],
)
def test_authentication_errors(
    input: str, output: Type[DexcomError], reason: str
) -> None:
    """Test initializing Dexcom with authentication errors."""
    with pytest.raises(output) as e:
        Dexcom(input[0], input[1])
    assert reason == str(e.value)


def test_authentication_success() -> None:
    """Test initializing Dexcom authentication success."""
    d = Dexcom(USERNAME, PASSWORD)
    d._validate_account()
    d._validate_session_id()


def test_login_endpoint_not_verbose() -> None:
    """Test particular endpoint continues to be non-verbose."""
    url = f"{DEXCOM_BASE_URL}/{DEXCOM_LOGIN_ID_ENDPOINT}"
    json = {
        "accountName": USERNAME,
        "password": "a",
        "applicationId": DEXCOM_APPLICATION_ID,
    }
    r = requests.request(
        "post",
        url,
        json=json,
    )
    assert r.json() == DEFAULT_SESSION_ID
