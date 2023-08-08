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
)

from .conftest import PASSWORD, USERNAME


@pytest.mark.vcr()
class TestDexcom:
    @pytest.mark.parametrize(
        "username",
        [None, "", 1, "username", USERNAME],
    )
    @pytest.mark.parametrize(
        "password",
        [None, "", 1, "password", PASSWORD],
    )
    def test_dexcom(self, username: Any, password: Any) -> None:
        raises = does_not_raise()
        expected: Optional[Union[ArgumentErrorEnum, AccountErrorEnum]] = None

        if any([username is None, username == "", not isinstance(username, str)]):
            raises = pytest.raises(ArgumentError)  # type: ignore
            expected = ArgumentErrorEnum.USERNAME_INVALID
        elif any([password is None, password == "", not isinstance(password, str)]):
            raises = pytest.raises(ArgumentError)  # type: ignore
            expected = ArgumentErrorEnum.PASSWORD_INVALID
        elif any([username != USERNAME, password != PASSWORD]):
            raises = pytest.raises(AccountError)  # type: ignore
            expected = AccountErrorEnum.PASSWORD_INVALID
        elif all([username == USERNAME, password == PASSWORD]):
            pass
        else:
            pytest.fail()

        with raises as error:
            dexcom = Dexcom(username, password)

            assert dexcom._username == username
            assert dexcom._password == password
            assert dexcom._account_id != DEFAULT_UUID
            # assert dexcom._account_id == ACCOUNT_ID
            assert UUID(dexcom._session_id)
            assert dexcom._session_id != DEFAULT_UUID
            return

        assert error.value.enum == expected
