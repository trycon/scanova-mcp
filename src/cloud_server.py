from mcp.server.fastmcp import FastMCP
import json
import os
import asyncio
from qrcode import create_qr_code, list_qr_codes, update_qr_code, retrieve_qr_code, download_qr_code, activate_qr_code, deactivate_qr_code
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging

# Create FastAPI app for HTTP transport
app = FastAPI(title="Scanova MCP Server", version="1.0.0")


# Add CORS middleware for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_api_key(request: Request) -> str:
    """
    Extract Scanova API key from MCP client headers.
    
    The API key can be provided in various header formats:
    - Authorization: Bearer <api_key>
    - Authorization: <api_key>
    - X-API-Key: <api_key>
    - Scanova-API-Key: <api_key>
    """
    # Try Authorization header first
    auth_header = request.headers.get("Authorization", "")
    if auth_header:
        # Handle "Bearer <token>" format
        if auth_header.startswith("Bearer "):
            return auth_header[7:]  # Remove "Bearer " prefix
        # Handle direct API key format
        return auth_header
    
    # Try other common API key headers
    api_key = (
        request.headers.get("X-API-Key") or
        request.headers.get("x-api-key") or
        request.headers.get("Scanova-API-Key") or
        request.headers.get("scanova-api-key") or
        request.headers.get("API-Key") or
        request.headers.get("api-key")
    )
    
    return api_key

# Create MCP server
server = FastMCP()

@server.tool()
def get_scanova_data(query: str) -> str:
    return "This is a test response"

@server.tool("create_qr_code", description="Create a new QR code. Can be called with: create qr, make qr code, generate qr, new qr code, add qr code")
def create_qr_code_tool(params: dict = None):
    # This tool is mainly for FastMCP, the HTTP endpoint handles API key extraction
    log.error(f"create_qr_code_tool")
    return {"error": "Please use the HTTP MCP endpoint for API key authentication"}

@server.tool("list_qr_codes", description="List QR codes. Can be called with: list qr codes, fetch qr list, get qr codes, show qr codes, display qr codes, last 5 qr codes, recent qr codes")
def list_qr_codes_tool(page: int = 1, limit: int = 10, search: str = None):
    # This tool is mainly for FastMCP, the HTTP endpoint handles API key extraction
    log.info(f"list_qr_codes_tool")
    return {"error": "Please use the HTTP MCP endpoint for API key authentication"}

@server.tool("update_qr_code", description="Update an existing QR code. Can be called with: update qr, modify qr code, edit qr code, change qr code")
def update_qr_code_tool(qrid: str = None, params: dict = None):
    # This tool is mainly for FastMCP, the HTTP endpoint handles API key extraction
    return {"error": "Please use the HTTP MCP endpoint for API key authentication"}

@server.tool("retrieve_qr_code", description="Get details of a specific QR code. Can be called with: get qr details, fetch qr code, show qr info, qr code info")
def retrieve_qr_code_tool(qrid: str = None):
    # This tool is mainly for FastMCP, the HTTP endpoint handles API key extraction
    return {"error": "Please use the HTTP MCP endpoint for API key authentication"}

@server.tool("download_qr_code", description="Download QR code image. Can be called with: download qr, get qr image, save qr code, export qr code")
def download_qr_code_tool(qrid: str = None):
    # This tool is mainly for FastMCP, the HTTP endpoint handles API key extraction
    return {"error": "Please use the HTTP MCP endpoint for API key authentication"}

@server.tool("activate_qr_code", description="Activate a QR code. Can be called with: activate qr, enable qr code, turn on qr code, make qr active")
def activate_qr_code_tool(qrid: str = None):
    # This tool is mainly for FastMCP, the HTTP endpoint handles API key extraction
    return {"error": "Please use the HTTP MCP endpoint for API key authentication"}

@server.tool("deactivate_qr_code", description="Deactivate a QR code. Can be called with: deactivate qr, disable qr code, turn off qr code, make qr inactive")
def deactivate_qr_code_tool(qrid: str = None):
    # This tool is mainly for FastMCP, the HTTP endpoint handles API key extraction
    return {"error": "Please use the HTTP MCP endpoint for API key authentication"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "scanova-mcp"}

# MCP JSON-RPC endpoint
@app.post("/mcp")
async def mcp_endpoint(request: Request):
    try:
        # Extract API key from headers
        api_key = extract_api_key(request)
        
        # Get the JSON-RPC request
        body = await request.json()
        
        # Handle basic MCP protocol methods
        if body.get("method") == "tools/list":
            # Return available tools
            tools = [
                {
                    "name": "create_qr_code",
                    "description": "Create a new QR code. Can be called with: create qr, make qr code, generate qr",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "params": {
                                "type": "object",
                                "description": "QR code parameters including qr_type, category, info, and name"
                            }
                        },
                        "required": ["params"]
                    }
                },
                {
                    "name": "list_qr_codes", 
                    "description": "List QR codes. Can be called with: list qr codes, show qr codes",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "page": {"type": "integer", "default": 1},
                            "limit": {"type": "integer", "default": 10},
                            "search": {"type": "string"}
                        }
                    }
                },
                {
                    "name": "update_qr_code",
                    "description": "Update an existing QR code",
                    "inputSchema": {
                        "type": "object", 
                        "properties": {
                            "qrid": {"type": "string"},
                            "params": {"type": "object"}
                        },
                        "required": ["qrid", "params"]
                    }
                },
                {
                    "name": "retrieve_qr_code",
                    "description": "Get details of a specific QR code",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "qrid": {"type": "string"}
                        },
                        "required": ["qrid"]
                    }
                },
                {
                    "name": "download_qr_code", 
                    "description": "Download QR code image",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "qrid": {"type": "string"},
                            "params": {"type": "object"}
                        },
                        "required": ["qrid"]
                    }
                },
                {
                    "name": "activate_qr_code",
                    "description": "Activate a QR code", 
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "qrid": {"type": "string"}
                        },
                        "required": ["qrid"]
                    }
                },
                {
                    "name": "deactivate_qr_code",
                    "description": "Deactivate a QR code",
                    "inputSchema": {
                        "type": "object", 
                        "properties": {
                            "qrid": {"type": "string"}
                        },
                        "required": ["qrid"]
                    }
                }
            ]
            
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {"tools": tools}
            })
            
        elif body.get("method") == "tools/call":
            # Check if API key is provided
            if not api_key:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "error": {
                        "code": -32602,
                        "message": "API key is required. Please configure your Scanova API key in your MCP client headers (Authorization, X-API-Key, or Scanova-API-Key)."
                    }
                })
            
            # Handle tool calls
            params = body.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            try:
                if tool_name == "create_qr_code":
                    result = create_qr_code(arguments.get("params"), api_key=api_key)
                elif tool_name == "list_qr_codes":
                    qr_params = {}
                    if arguments.get("page"):
                        qr_params["page"] = arguments.get("page")
                    if arguments.get("limit"):
                        qr_params["limit"] = arguments.get("limit")
                    if arguments.get("search"):
                        qr_params["search"] = arguments.get("search")
                    result = list_qr_codes(qr_params if qr_params else None, api_key=api_key)
                elif tool_name == "update_qr_code":
                    result = update_qr_code(arguments.get("qrid"), arguments.get("params"), api_key=api_key)
                elif tool_name == "retrieve_qr_code":
                    result = retrieve_qr_code(arguments.get("qrid"), api_key=api_key)
                elif tool_name == "download_qr_code":
                    result = download_qr_code(arguments.get("qrid"), arguments.get("params"), api_key=api_key)
                elif tool_name == "activate_qr_code":
                    result = activate_qr_code(arguments.get("qrid"), api_key=api_key)
                elif tool_name == "deactivate_qr_code":
                    result = deactivate_qr_code(arguments.get("qrid"), api_key=api_key)
                else:
                    raise ValueError(f"Unknown tool: {tool_name}")
                
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "result": {"content": [{"type": "text", "text": str(result)}]}
                })
                
            except Exception as e:
                log.error(f"Tool execution error: {str(e)}")
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "error": {
                        "code": -32603,
                        "message": f"Tool execution error: {str(e)}"
                    }
                })
        
        elif body.get("method") == "initialize":
            # MCP initialization
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "scanova-mcp",
                        "version": "1.0.0"
                    }
                }
            })
            
        else:
            # Unknown method
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {body.get('method')}"
                }
            })
            
    except Exception as e:
        log.error(f"MCP endpoint error: {str(e)}")
        return JSONResponse({
            "jsonrpc": "2.0", 
            "id": body.get("id") if 'body' in locals() else None,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        })

# Root endpoint
@app.get("/")
async def root():
    return {
        "service": "Scanova MCP Server",
        "version": "1.0.0",
        "endpoints": {
            "mcp": "/mcp",
            "health": "/health"
        },
        "authentication": {
            "required": "Scanova API Key",
            "headers": ["Authorization", "X-API-Key", "Scanova-API-Key"],
            "note": "Configure your Scanova API key in your MCP client headers"
        }
    }

if __name__ == "__main__":
    # Run FastAPI server with MCP endpoint
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    log.info(f"🚀 Starting Scanova MCP Server on {host}:{port}")
    log.info(f"📡 MCP Endpoint: http://{host}:{port}/mcp")
    log.info(f"❤️  Health Check: http://{host}:{port}/health")
    log.info(f"🔑 Authentication: Configure your Scanova API key in MCP client headers")
    log.error(f"test error log")
    
    uvicorn.run(app, host=host, port=port)