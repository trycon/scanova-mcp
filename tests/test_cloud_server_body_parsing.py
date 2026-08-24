"""An empty or malformed request body to POST /mcp used to raise an
uncaught json.JSONDecodeError, get logged at ERROR level, and return a
500 — indistinguishable from an actual server bug. It's a client error
(often just a bot/health-check probing the public endpoint), so it should
be a 400 with a proper JSON-RPC Parse error, logged at warning."""

from fastapi.testclient import TestClient

from cloud_server import app

client = TestClient(app)


def test_empty_body_returns_400_parse_error():
    resp = client.post("/mcp", content=b"", headers={"content-type": "application/json"})
    assert resp.status_code == 400
    body = resp.json()
    assert body["jsonrpc"] == "2.0"
    assert body["id"] is None
    assert body["error"]["code"] == -32700


def test_malformed_body_returns_400_parse_error():
    resp = client.post("/mcp", content=b"not json", headers={"content-type": "application/json"})
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == -32700


def test_valid_request_still_works():
    resp = client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    assert resp.status_code == 200
    assert resp.json()["result"]["serverInfo"]["name"] == "scanova-mcp"
