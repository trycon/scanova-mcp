import requests
from config import SCANOVA_BASE_URL

_BASE = SCANOVA_BASE_URL.rstrip("/")


def _headers(api_key: str) -> dict:
    return {"Authorization": api_key, "Content-Type": "application/json"}


def _auth_error():
    return {"error": "API key is required. Please configure your Scanova API key in your MCP client."}


def list_users(api_key: str = None) -> dict:
    """GET /user/ — list all users in the account."""
    if not api_key:
        return _auth_error()
    try:
        resp = requests.get(f"{_BASE}/user/", headers=_headers(api_key))
        return resp.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}


def get_user(user_id: str, api_key: str = None) -> dict:
    """GET /user/{id}/ — get details of a specific user."""
    if not api_key:
        return _auth_error()
    if not user_id:
        return {"error": "user_id is required"}
    try:
        resp = requests.get(f"{_BASE}/user/{user_id}/", headers=_headers(api_key))
        return resp.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}


def add_user(email: str, role: str, api_key: str = None) -> dict:
    """POST /user/ — invite a new user to the account."""
    if not api_key:
        return _auth_error()
    if not email:
        return {"error": "email is required"}
    if not role:
        return {"error": "role is required"}
    try:
        resp = requests.post(
            f"{_BASE}/user/",
            headers=_headers(api_key),
            json={"email": email, "role": role},
        )
        return resp.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}


def remove_user(user_id: str, api_key: str = None) -> dict:
    """DELETE /user/{id}/ — remove a user from the account."""
    if not api_key:
        return _auth_error()
    if not user_id:
        return {"error": "user_id is required"}
    try:
        resp = requests.delete(f"{_BASE}/user/{user_id}/", headers=_headers(api_key))
        if resp.status_code == 204:
            return {"success": True, "message": "User removed"}
        return resp.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}


def list_user_roles(api_key: str = None) -> dict:
    """GET /user/roles/ — list available user roles."""
    if not api_key:
        return _auth_error()
    try:
        resp = requests.get(f"{_BASE}/user/roles/", headers=_headers(api_key))
        return resp.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}


def update_user_role(user_id: str, role: str, api_key: str = None) -> dict:
    """PATCH /user/{id}/ — update a user's role."""
    if not api_key:
        return _auth_error()
    if not user_id:
        return {"error": "user_id is required"}
    if not role:
        return {"error": "role is required"}
    try:
        resp = requests.patch(
            f"{_BASE}/user/{user_id}/",
            headers=_headers(api_key),
            json={"role": role},
        )
        return resp.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
