import base64
import json
import requests
from config import SCANOVA_BASE_URL

_BASE = SCANOVA_BASE_URL.rstrip("/")


def get_url_from_user():
    """
    Prompt the user to enter a URL and name for QR code creation.
    
    This function interactively asks the user for:
    1. A URL to encode in the QR code
    2. A name for the QR code (optional, defaults to 'qrcode')
    
    The function automatically adds 'http://' prefix to URLs if not present.
    
    Returns:
        tuple: A tuple containing (url, name) where:
            - url (str): The URL to encode in the QR code
            - name (str): The name for the QR code
    
    Raises:
        ValueError: If no URL is provided by the user
    
    Example:
        >>> url, name = get_url_from_user()
        Enter the URL you want to encode in the QR code:
        URL: google.com
        Enter a name for the QR code (press Enter for default 'qrcode'):
        Name: my-google-qr
        >>> print(url, name)
        http://google.com my-google-qr
    """
    print("Enter the URL you want to encode in the QR code:")
    url = input("URL: ").strip()
    
    if not url:
        raise ValueError("URL is required to create a QR code")
    
    # Add http:// prefix if not present
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    print("Enter a name for the QR code (press Enter for default 'qrcode'):")
    name = input("Name: ").strip()
    
    # Use default name if none provided
    if not name:
        name = "qrcode"
    
    return url, name

def create_qr_code(params=None, api_key=None):
    """
    Create a new QR code with URL and name from user input or provided parameters.
    
    Args:
        params (dict, optional): Pre-defined parameters for QR code creation.
        api_key (str): Scanova API key from the MCP client
    
    Returns:
        dict: JSON response from the Scanova API containing the created QR code details.
    """
    if not api_key:
        return {"error": "API key is required. Please configure your Scanova API key in your MCP client."}
    
    # Get URL and name from user if not provided in params
    if params is None or 'info' not in params:
        # For MCP server, we need params to be provided
        return {"error": "Parameters with 'info' field are required for QR code creation"}
    
    # Auto-serialize info if caller passed a dict instead of a JSON string
    if params and isinstance(params.get("info"), (dict, list)):
        params = {**params, "info": json.dumps(params["info"])}
    headers = {"Authorization": f"{api_key}", "Content-Type": "application/json"}
    try:
        resp = requests.post(f"{_BASE}/qrcode/", headers=headers, json=params)
        return resp.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}

def get_qr_id_from_user():
    """
    Prompt the user to enter a QR code ID for update operations.
    
    This function interactively asks the user for the ID of an existing QR code
    that they want to update or modify.
    
    Returns:
        str: The QR code ID entered by the user
    
    Raises:
        ValueError: If no QR code ID is provided by the user
    
    Example:
        >>> qr_id = get_qr_id_from_user()
        Enter the QR code ID you want to update:
        QR ID: 12345
        >>> print(qr_id)
        12345
    """
    print("Enter the QR code ID you want to update:")
    qr_id = input("QR ID: ").strip()
    
    if not qr_id:
        raise ValueError("QR ID is required to update a QR code")
    
    return qr_id

def list_qr_codes(params=None, api_key=None):
    """
    Retrieve a list of QR codes from the Scanova API.
    
    Args:
        params (dict): Query parameters for filtering and pagination.
        api_key (str): Scanova API key from the MCP client
    
    Returns:
        dict: JSON response from the Scanova API containing the list of QR codes.
    """
    if not api_key:
        return {"error": "API key is required. Please configure your Scanova API key in your MCP client."}

    headers = {"Authorization": f"{api_key}", "Content-Type": "application/json"}
    try:
        resp = requests.get(f"{_BASE}/qrcode/", headers=headers, params=params)
        return resp.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}

def update_qr_code(qrid=None, params=None, api_key=None):
    """
    Update an existing QR code with new parameters.
    
    Args:
        qrid (str): The ID of the QR code to update.
        params (dict): Parameters for QR code update.
        api_key (str): Scanova API key from the MCP client
    
    Returns:
        dict: JSON response from the Scanova API containing the updated QR code details.
    """
    if not api_key:
        return {"error": "API key is required. Please configure your Scanova API key in your MCP client."}
    
    if not qrid:
        return {"error": "QR code ID is required for update operation"}
    
    if not params:
        return {"error": "Parameters are required for QR code update"}
    
    headers = {"Authorization": f"{api_key}", "Content-Type": "application/json"}
    try:
        resp = requests.put(f"{_BASE}/qrcode/{qrid}/", headers=headers, json=params)
        return resp.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}

def retrieve_qr_code(qrid=None, params=None, api_key=None):
    """
    Retrieve a QR code from the Scanova API.
    
    Args:
        qrid (str): The ID of the QR code to retrieve.
        params (dict, optional): Additional parameters.
        api_key (str): Scanova API key from the MCP client
    
    Returns:
        dict: JSON response from the Scanova API containing the QR code details.
    """
    if not api_key:
        return {"error": "API key is required. Please configure your Scanova API key in your MCP client."}
    
    if not qrid:
        return {"error": "QR code ID is required for retrieve operation"}

    headers = {"Authorization": f"{api_key}", "Content-Type": "application/json"}
    try:
        resp = requests.get(f"{_BASE}/qrcode/{qrid}/", headers=headers, params=params)
        return resp.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}

def download_qr_code(qrid=None, params=None, api_key=None):
    """
    Download a QR code from the Scanova API.
    
    Args:
        qrid (str): The ID of the QR code to download.
        params (dict, optional): Download parameters (size, format, etc.).
        api_key (str): Scanova API key from the MCP client
    
    Returns:
        dict: Response containing download information or error.
    """
    if not api_key:
        return {"error": "API key is required. Please configure your Scanova API key in your MCP client."}
    
    if not qrid:
        return {"error": "QR code ID is required for download operation"}

    headers = {"Authorization": f"{api_key}"}
    try:
        resp = requests.get(f"{_BASE}/qr/{qrid}/download/", headers=headers, params=params)
        if resp.status_code == 200:
            content_type = resp.headers.get("content-type", "image/png")
            return {
                "success": True,
                "content_type": content_type,
                "size_bytes": len(resp.content),
                "data_base64": base64.b64encode(resp.content).decode("utf-8"),
            }
        return resp.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}

def activate_qr_code(qrid=None, params=None, api_key=None):
    """
    Activate a QR code from the Scanova API.
    
    Args:
        qrid (str): The ID of the QR code to activate.
        params (dict, optional): Additional parameters.
        api_key (str): Scanova API key from the MCP client
    
    Returns:
        dict: JSON response from the Scanova API.
    """
    if not api_key:
        return {"error": "API key is required. Please configure your Scanova API key in your MCP client."}
    
    if not qrid:
        return {"error": "QR code ID is required for activate operation"}

    if params is None:
        params = {"is_active": True}
    
    headers = {"Authorization": f"{api_key}", "Content-Type": "application/json"}
    try:
        resp = requests.patch(f"{_BASE}/qrcode/{qrid}/", headers=headers, json=params)
        return resp.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}

def deactivate_qr_code(qrid=None, params=None, api_key=None):
    """
    Deactivate a QR code from the Scanova API.

    Args:
        qrid (str): The ID of the QR code to deactivate.
        params (dict, optional): Additional parameters.
        api_key (str): Scanova API key from the MCP client

    Returns:
        dict: JSON response from the Scanova API.
    """
    if not api_key:
        return {"error": "API key is required. Please configure your Scanova API key in your MCP client."}

    if not qrid:
        return {"error": "QR code ID is required for deactivate operation"}

    if params is None:
        params = {"is_active": False}

    headers = {"Authorization": f"{api_key}", "Content-Type": "application/json"}
    try:
        resp = requests.patch(f"{_BASE}/qrcode/{qrid}/", headers=headers, json=params)
        return resp.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}


def delete_qr_code(qrid=None, api_key=None):
    """DELETE /qrcode/{qrid}/ — permanently delete a QR code."""
    if not api_key:
        return {"error": "API key is required. Please configure your Scanova API key in your MCP client."}
    if not qrid:
        return {"error": "QR code ID is required for delete operation"}
    headers = {"Authorization": f"{api_key}", "Content-Type": "application/json"}
    try:
        resp = requests.delete(f"{_BASE}/qrcode/{qrid}/", headers=headers)
        if resp.status_code == 204:
            return {"success": True, "message": "QR code deleted"}
        return resp.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}


def get_qr_categories(view_type="all", api_key=None):
    """GET /qrcode/category/ — list available QR code categories."""
    if not api_key:
        return {"error": "API key is required. Please configure your Scanova API key in your MCP client."}
    headers = {"Authorization": f"{api_key}", "Content-Type": "application/json"}
    try:
        resp = requests.get(
            f"{_BASE}/qrcode/category/",
            headers=headers,
            params={"view_type": view_type},
        )
        return resp.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}


def download_qr_printable(qrid=None, size=600, name=None, api_key=None):
    """GET /qr/{qrid}/download/ with for_print=true — generate a print-optimised PDF QR code."""
    if not api_key:
        return {"error": "API key is required. Please configure your Scanova API key in your MCP client."}
    if not qrid:
        return {"error": "QR code ID is required for printable download"}
    headers = {"Authorization": f"{api_key}"}
    params = {"for_print": "true", "file": "pdf", "size": str(size)}
    if name:
        params["name"] = name
    try:
        resp = requests.get(f"{_BASE}/qr/{qrid}/download/", headers=headers, params=params)
        if resp.status_code == 200:
            content_type = resp.headers.get("content-type", "application/pdf")
            return {
                "success": True,
                "content_type": content_type,
                "size_bytes": len(resp.content),
                "data_base64": base64.b64encode(resp.content).decode("utf-8"),
            }
        return resp.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}


def attach_form_to_qr(qrid=None, form_id=None, api_key=None):
    """PATCH /qrcode/{qrid}/ — attach a lead capture form to a QR code."""
    if not api_key:
        return {"error": "API key is required. Please configure your Scanova API key in your MCP client."}
    if not qrid:
        return {"error": "QR code ID is required"}
    if form_id is None:
        return {"error": "form_id is required"}
    headers = {"Authorization": f"{api_key}", "Content-Type": "application/json"}
    try:
        resp = requests.patch(
            f"{_BASE}/qrcode/{qrid}/", headers=headers, json={"form": form_id}
        )
        return resp.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}


def detach_form_from_qr(qrid=None, api_key=None):
    """PATCH /qrcode/{qrid}/ — remove the lead capture form from a QR code."""
    if not api_key:
        return {"error": "API key is required. Please configure your Scanova API key in your MCP client."}
    if not qrid:
        return {"error": "QR code ID is required"}
    headers = {"Authorization": f"{api_key}", "Content-Type": "application/json"}
    try:
        resp = requests.patch(
            f"{_BASE}/qrcode/{qrid}/", headers=headers, json={"form": None}
        )
        return resp.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}


def attach_lead_list_to_qr(qrid=None, lead_list_id=None, api_key=None):
    """PATCH /qrcode/{qrid}/ — attach a lead list to a QR code."""
    if not api_key:
        return {"error": "API key is required. Please configure your Scanova API key in your MCP client."}
    if not qrid:
        return {"error": "QR code ID is required"}
    if lead_list_id is None:
        return {"error": "lead_list_id is required"}
    headers = {"Authorization": f"{api_key}", "Content-Type": "application/json"}
    try:
        resp = requests.patch(
            f"{_BASE}/qrcode/{qrid}/", headers=headers, json={"lead_list": lead_list_id}
        )
        return resp.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}


def detach_lead_list_from_qr(qrid=None, api_key=None):
    """PATCH /qrcode/{qrid}/ — remove the lead list from a QR code."""
    if not api_key:
        return {"error": "API key is required. Please configure your Scanova API key in your MCP client."}
    if not qrid:
        return {"error": "QR code ID is required"}
    headers = {"Authorization": f"{api_key}", "Content-Type": "application/json"}
    try:
        resp = requests.patch(
            f"{_BASE}/qrcode/{qrid}/", headers=headers, json={"lead_list": None}
        )
        return resp.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
