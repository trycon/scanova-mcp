"""top_qr_codes_by_scans, and the analytics results the normalizer used to report as validation errors.

"Which of my QR codes got the most scans in the last 30 days?" failed for every model: get_qr_analytics with
types=["qr"] answers {"qr": [[name, scans], ...], "qr_meta": {...}}, and the normalizer read any dict with a list
value (and no count/results) as a DRF 422, so a successful lookup came back as a tool error. The assistant retried
it until ai-api's stop rule ended the turn. The overview ({"last_months": [...]}) had the same problem.
"""

import json
from datetime import date

import pytest

import scanova_api
from mcp_http.dispatcher import execute_tool
from mcp_http.more_tools import _top_qr_codes_by_scans
from mcp_http.normalizer import normalize


class _Resp:
    def __init__(self, status=200, body=None):
        self.status_code = status
        self._body = body
        self.text = json.dumps(body)

    def json(self):
        return self._body


@pytest.fixture
def api(monkeypatch):
    calls, answers = [], []

    def fake(method, url, headers=None, params=None, json=None, timeout=None):
        calls.append({"method": method, "path": url.split("/", 3)[-1], "params": params or {}, "body": json})
        return answers.pop(0)

    monkeypatch.setattr(scanova_api.requests, "request", fake)
    fake.calls, fake.answers = calls, answers
    return fake


ANALYTICS = {
    "qr": [["Menu", 40], ["Flyer", 120], ["Poster", 0], ["Card", 7]],
    "qr_meta": {
        "Menu": {"qrid": "Qmenu", "category": "Website", "category_slug": "website"},
        "Flyer": {"qrid": "Qflyer", "category": "PDF", "category_slug": "pdf"},
        "Poster": {"qrid": "Qposter", "category": "Website", "category_slug": "website"},
        "Card": {"qrid": "Qcard", "category": "vCard", "category_slug": "vcard"},
    },
}


def test_analytics_breakdowns_are_successes_not_validation_errors():
    for raw, tool in [
        (ANALYTICS, "get_qr_analytics"),
        ({"qr": [], "qr_meta": {}}, "get_qr_analytics"),
        ({"date": [["2026-10-01", 3]]}, "get_qr_analytics"),
        ({"date": []}, "get_qr_analytics"),
        ({"all_time": {"count_total_scans": 9}, "last_months": [], "scan_dates": [["2026-10-01", 3]]}, "get_analytics_overview"),
    ]:
        env = normalize(raw, tool)
        assert env["ok"] is True, (tool, raw)
        assert env["data"] == raw


def test_drf_field_errors_are_still_validation_errors():
    env = normalize({"q": ["This field is required."], "filter_by": ["\"x\" is not a valid choice."]}, "get_qr_analytics")
    assert env["ok"] is False and env["status_code"] == 422


def test_ranks_the_whole_account_in_one_call(api):
    api.answers.append(_Resp(200, ANALYTICS))
    out = _top_qr_codes_by_scans({"limit": 2}, "key", today=date(2026, 10, 14))
    assert api.calls == [{
        "method": "POST", "path": "analytics/qr/",
        "params": {"type": "qr", "from": "2026-09-15", "to": "2026-10-14", "all": "true", "overview": "true"},
        "body": {"q": [], "filter_by": "qrid"},
    }]
    assert out["from_date"] == "2026-09-15" and out["to_date"] == "2026-10-14"
    assert out["total_scans"] == 167 and out["qr_codes_counted"] == 4 and out["qr_codes_with_scans"] == 3
    assert out["top"] == [
        {"rank": 1, "qrid": "Qflyer", "name": "Flyer", "scans": 120, "category": "PDF"},
        {"rank": 2, "qrid": "Qmenu", "name": "Menu", "scans": 40, "category": "Website"},
    ]


def test_codes_with_no_scans_are_not_ranked(api):
    api.answers.append(_Resp(200, {"qr": [["Poster", 0]], "qr_meta": {"Poster": {"qrid": "Qp"}}}))
    out = _top_qr_codes_by_scans({"days": 7}, "key", today=date(2026, 10, 14))
    assert api.calls[0]["params"]["from"] == "2026-10-08"
    assert out["top"] == [] and out["total_scans"] == 0 and out["qr_codes_counted"] == 1


def test_a_name_two_codes_share_gets_no_qrid(api):
    api.answers.append(_Resp(200, {"qr": [["Menu", 5], ["Menu", 3]], "qr_meta": {"Menu": {"qrid": "Q2"}}}))
    out = _top_qr_codes_by_scans({}, "key", today=date(2026, 10, 14))
    assert [t["qrid"] for t in out["top"]] == [None, None]


def test_plans_without_per_qr_analytics_get_the_total_and_a_note(api):
    api.answers.append(_Resp(200, {"count": 42}))
    out = _top_qr_codes_by_scans({}, "key", today=date(2026, 10, 14))
    assert out["total_scans"] == 42 and out["top"] == [] and "total scans only" in out["note"]


def test_bad_periods_call_nothing(api):
    assert "between" in _top_qr_codes_by_scans({"days": 0}, "key")["error"]
    assert "between" in _top_qr_codes_by_scans({"days": 9999}, "key")["error"]
    assert "required" in _top_qr_codes_by_scans({"from_date": "2026-10-01"}, "key")["error"]
    assert api.calls == []


def test_an_api_failure_is_a_tool_error(api):
    api.answers.append(_Resp(400, {"q": ["High Volume of data."]}))
    env = normalize(execute_tool("top_qr_codes_by_scans", {}, "key"), "top_qr_codes_by_scans")
    assert env["ok"] is False and env["status_code"] == 400


def test_the_reply_is_small_however_big_the_account(api):
    rows = [[f"QR {i}", i] for i in range(5000)]
    api.answers.append(_Resp(200, {"qr": rows, "qr_meta": {f"QR {i}": {"qrid": f"Q{i}"} for i in range(5000)}}))
    env = normalize(execute_tool("top_qr_codes_by_scans", {"limit": 50}, "key"), "top_qr_codes_by_scans")
    assert env["ok"] is True and len(env["data"]["top"]) == 50 and env["data"]["top"][0]["scans"] == 4999
    assert len(json.dumps(env)) < 20_000  # ai-api's cut for one tool result
