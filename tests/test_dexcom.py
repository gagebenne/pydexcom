"""Tests for the Dexcom class in the pydexcom package."""

from contextlib import nullcontext as does_not_raise
from typing import TYPE_CHECKING, Any
from uuid import UUID

import pytest

from pydexcom import Dexcom, Region
from pydexcom.const import DEFAULT_UUID
from pydexcom.errors import (
    AccountError,
    AccountErrorEnum,
    ArgumentError,
    ArgumentErrorEnum,
)
from pydexcom.util import valid_uuid

from .conftest import ACCOUNT_ID, PASSWORD, REGION, TEST_ACCOUNT_ID, USERNAME

if TYPE_CHECKING:
    from _pytest.python_api import RaisesContext


@pytest.mark.vcr
class TestDexcom:
    """Test class for Dexcom authentication."""

    @pytest.mark.parametrize(
        "password",
        [None, "", 1, "password", PASSWORD],
    )
    @pytest.mark.parametrize(
        "account_id",
        [None, "", 1, "77777777-7777-7777-7777-777777777777", ACCOUNT_ID],
    )
    @pytest.mark.parametrize(
        "username",
        [None, "", 1, "username", USERNAME],
    )
    @pytest.mark.parametrize(
        "region",
        [None, "", "region", Region.OUS, REGION],
    )
    def test_dexcom(  # noqa: C901
        self,
        password: Any,  # noqa: ANN401
        account_id: Any,  # noqa: ANN401
        username: Any,  # noqa: ANN401
        region: Any,  # noqa: ANN401
    ) -> None:
        """Test the Dexcom class for authentication."""
        enum: ArgumentErrorEnum | AccountErrorEnum | None
        raises: (
            RaisesContext[ArgumentError] | RaisesContext[AccountError] | does_not_raise
        )

        if not region or region not in list(Region):
            raises = pytest.raises(ArgumentError)
            enum = ArgumentErrorEnum.REGION_INVALID
        elif username is None and account_id is None:
            raises = pytest.raises(ArgumentError)
            enum = ArgumentErrorEnum.USER_ID_REQUIRED
        elif username is not None and account_id is not None:
            raises = pytest.raises(ArgumentError)
            enum = ArgumentErrorEnum.USER_ID_MULTIPLE
        elif not password or not isinstance(password, str):
            raises = pytest.raises(ArgumentError)
            enum = ArgumentErrorEnum.PASSWORD_INVALID
        elif account_id is None and (not username or not isinstance(username, str)):
            raises = pytest.raises(ArgumentError)
            enum = ArgumentErrorEnum.USERNAME_INVALID
        elif username is None and (
            not account_id
            or not isinstance(account_id, str)
            or not valid_uuid(str(account_id))
        ):
            raises = pytest.raises(ArgumentError)
            enum = ArgumentErrorEnum.ACCOUNT_ID_INVALID
        elif (
            (account_id is None and username != USERNAME)
            or (username is None and account_id != ACCOUNT_ID)
            or (account_id is None and username == USERNAME and password != PASSWORD)
            or (account_id == ACCOUNT_ID and username is None and password != PASSWORD)
            or (region != REGION)
        ):
            raises = pytest.raises(AccountError)
            enum = AccountErrorEnum.FAILED_AUTHENTICATION
        elif (account_id is None and username == USERNAME and password == PASSWORD) or (
            account_id == ACCOUNT_ID and username is None and password == PASSWORD
        ):
            raises = does_not_raise()
            enum = None
        else:
            pytest.fail("Unexpected test case")

        with raises as error:
            dexcom = Dexcom(
                password=password,
                account_id=account_id,
                username=username,
                region=region,
            )

            if username is not None:
                assert dexcom.username == USERNAME
            if account_id is not None:
                assert dexcom.account_id == ACCOUNT_ID
            assert dexcom.account_id in {ACCOUNT_ID, TEST_ACCOUNT_ID}
            assert dexcom._password == PASSWORD
            assert dexcom.account_id != DEFAULT_UUID
            assert UUID(dexcom._session_id)
            assert dexcom._session_id != DEFAULT_UUID
            return

        assert error.value.enum == enum
