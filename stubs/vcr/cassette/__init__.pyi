# ruff: noqa: UP007, ANN401
from types import TracebackType
from typing import Self, Union

class Cassette:
    def __enter__(self) -> Self: ...
    def __exit__(
        self,
        exc_type: Union[type[BaseException], None],
        exc_val: Union[BaseException, None],
        exc_tb: Union[TracebackType, None],
    ) -> None: ...
