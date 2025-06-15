# ruff: noqa: UP007, ANN401
from typing import Any, Callable, Union

from typing_extensions import TypeAlias
from vcr.cassette import Cassette
from vcr.record_mode import RecordMode
from vcr.request import Request

Filter: TypeAlias = list[
    Union[
        list[str],
        tuple[str, str],
        tuple[str, None],
        tuple[
            str,
            Callable[[str, Any, Request], Union[str, None]],
        ],
    ],
]

BeforeRecordRequestCallback: TypeAlias = Callable[
    [Request],
    Union[Request, None],
]

BeforeRecordResponseCallback: TypeAlias = Callable[
    [dict[str, Any]],
    Union[dict[str, Any], None],
]

class VCR:
    def __init__(
        self,
        cassette_library_dir: Union[str, None] = ...,
        path_transformer: Union[Callable[[str], str], None] = ...,
        record_mode: Union[RecordMode, None] = ...,
        match_on: Union[list[str], None] = ...,
        filter_headers: Union[Filter, None] = ...,
        filter_query_parameters: Union[Filter, None] = ...,
        filter_post_data_parameters: Union[Filter, None] = ...,
        ignore_hosts: Union[list[str], None] = ...,
        ignore_localhost: bool = ...,
        ignore_errors: bool = ...,
        before_record_request: Union[BeforeRecordRequestCallback, None] = ...,
        before_record_response: Union[BeforeRecordResponseCallback, None] = ...,
    ) -> None: ...
    def use_cassette(
        self,
        path: Union[str, None] = ...,
        **kwargs: Any,
    ) -> Cassette: ...
