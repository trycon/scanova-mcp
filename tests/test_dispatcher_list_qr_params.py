from mcp_http.dispatcher import _list_qr_params


def test_limit_argument_maps_to_page_size_query_param():
    """The Scanova API's qrcode/ list endpoint uses page_size, not limit —
    https://docs.scanova.io/api-reference/management-api/qr/list"""
    params = _list_qr_params({"limit": 50})
    assert params == {"page_size": 50}
    assert "limit" not in params


def test_page_and_search_and_is_page_pass_through():
    params = _list_qr_params({"page": 2, "limit": 25, "search": "flyer", "is_page": False})
    assert params == {"page": 2, "page_size": 25, "search": "flyer", "is_page": False}


def test_no_arguments_returns_none():
    assert _list_qr_params({}) is None
