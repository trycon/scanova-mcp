from mcp.server.fastmcp import FastMCP
import json
from qrcode import create_qr_code, list_qr_codes, update_qr_code, retrieve_qr_code, download_qr_code, activate_qr_code, deactivate_qr_code

server = FastMCP()

@server.tool()
def get_scanova_data(query: str) -> str:
    return "This is a test response"

@server.tool("create_qr_code", description="Create a new QR code. Can be called with: create qr, make qr code, generate qr, new qr code, add qr code")
def create_qr_code_tool(params: dict = None):
    return create_qr_code(params)

@server.tool("list_qr_codes", description="List QR codes. Can be called with: list qr codes, fetch qr list, get qr codes, show qr codes, display qr codes, last 5 qr codes, recent qr codes")
def list_qr_codes_tool(page: int = 1, limit: int = 10, search: str = None):
    params = {
        "page": page,
        "limit": limit
    }
    if search:
        params["search"] = search
    return list_qr_codes(params)

@server.tool("update_qr_code", description="Update an existing QR code. Can be called with: update qr, modify qr code, edit qr code, change qr code")
def update_qr_code_tool(qrid: str = None, params: dict = None):
    return update_qr_code(qrid, params)

@server.tool("retrieve_qr_code", description="Get details of a specific QR code. Can be called with: get qr details, fetch qr code, show qr info, qr code info")
def retrieve_qr_code_tool(qrid: str = None):
    return retrieve_qr_code(qrid)

@server.tool("download_qr_code", description="Download QR code image. Can be called with: download qr, get qr image, save qr code, export qr code")
def download_qr_code_tool(qrid: str = None):
    return download_qr_code(qrid)

@server.tool("activate_qr_code", description="Activate a QR code. Can be called with: activate qr, enable qr code, turn on qr code, make qr active")
def activate_qr_code_tool(qrid: str = None):
    return activate_qr_code(qrid)

@server.tool("deactivate_qr_code", description="Deactivate a QR code. Can be called with: deactivate qr, disable qr code, turn off qr code, make qr inactive")
def deactivate_qr_code_tool(qrid: str = None):
    return deactivate_qr_code(qrid)
