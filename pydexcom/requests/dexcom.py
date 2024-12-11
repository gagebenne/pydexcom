from __future__ import annotations

import requests

from pydexcom.base import DexcomSync
from pydexcom.const import Region


class Dexcom(DexcomSync):
    def __init__(
        self,
        *,
        password: str,
        account_id: str | None = None,
        username: str | None = None,
        region: Region = Region.US,
    ) -> None:
        super().__init__(
            password=password,
            account_id=account_id,
            username=username,
            region=region,
        )
        self._session = requests.Session()
        self._get_session()
