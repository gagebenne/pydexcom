"""Test authentication."""

import os

import pytest

from pydexcom import (
    ACCOUNT_ERROR_PASSWORD_INVALID,
    ACCOUNT_ERROR_PASSWORD_NULL_EMPTY,
    ACCOUNT_ERROR_USERNAME_NULL_EMPTY,
    AccountError,
    Dexcom,
)

USERNAME = os.environ.get("PYDEXCOM_USERNAME")
PASSWORD = os.environ.get("PYDEXCOM_PASSWORD")


def test_env():
    """Ensure environment variables are set."""
    assert USERNAME
    assert PASSWORD


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
def test_authentication_errors(input, output, reason):
    """Test initializing Dexcom with authentication errors."""
    with pytest.raises(output) as e:
        Dexcom(input[0], input[1])
    assert reason == str(e.value)


def test_authentication_success():
    """Test initializing Dexcom authentication success."""
    d = Dexcom(USERNAME, PASSWORD)
    d._validate_account()
    d._validate_session_id()
