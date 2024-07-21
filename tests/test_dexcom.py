from contextlib import nullcontext as does_not_raise
from typing import Any, Optional, Union
from uuid import UUID

import pytest

from pydexcom import (
    DEFAULT_UUID,
    AccountError,
    AccountErrorEnum,
    ArgumentError,
    ArgumentErrorEnum,
    Dexcom,
    valid_uuid,
)

from .conftest import ACCOUNT_ID, PASSWORD, USERNAME


@pytest.mark.vcr()
class TestDexcom:
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
    def test_dexcom(self, password: Any, account_id: Any, username: Any) -> None:
        raises: Any = does_not_raise()
        expected: Optional[Union[ArgumentErrorEnum, AccountErrorEnum]] = None

        if username is None and account_id is None:
            raises = pytest.raises(ArgumentError)
            expected = ArgumentErrorEnum.NONE_USER_ID_PROVIDED
        elif username is not None and account_id is not None:
            raises = pytest.raises(ArgumentError)
            expected = ArgumentErrorEnum.TOO_MANY_USER_ID_PROVIDED
        elif not password or not isinstance(password, str):
            raises = pytest.raises(ArgumentError)
            expected = ArgumentErrorEnum.PASSWORD_INVALID
        elif account_id is None and (not username or not isinstance(username, str)):
            raises = pytest.raises(ArgumentError)
            expected = ArgumentErrorEnum.USERNAME_INVALID
        elif username is None and (
            not account_id
            or not isinstance(account_id, str)
            or not valid_uuid(str(account_id))
        ):
            raises = pytest.raises(ArgumentError)
            expected = ArgumentErrorEnum.ACCOUNT_ID_INVALID
        elif (
            (account_id is None and username != USERNAME)
            or (username is None and account_id != ACCOUNT_ID)
            or (account_id is None and username == USERNAME and password != PASSWORD)
            or (account_id == ACCOUNT_ID and username is None and password != PASSWORD)
        ):
            raises = pytest.raises(AccountError)
            expected = AccountErrorEnum.FAILED_AUTHENTICATION
        elif (account_id is None and username == USERNAME and password == PASSWORD) or (
            account_id == ACCOUNT_ID and username is None and password == PASSWORD
        ):
            pass
        else:
            pytest.fail()

        print(expected)

        with raises as error:
            dexcom = Dexcom(password=password, account_id=account_id, username=username)

            assert dexcom._username == username
            assert dexcom._password == password
            assert dexcom._account_id != DEFAULT_UUID
            # assert dexcom._account_id == ACCOUNT_ID
            assert UUID(dexcom._session_id)
            assert dexcom._session_id != DEFAULT_UUID
            return

        assert error.value.enum == expected
