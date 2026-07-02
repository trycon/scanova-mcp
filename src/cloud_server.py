import logging
import os

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from mcp.server.fastmcp import FastMCP

from config import MCP_RESOURCE_URL, OAUTH_SERVER_URL, OPENAI_APPS_CHALLENGE
from mcp_http.fastmcp_tools import register_fastmcp_tools
from mcp_http.protocol import PUBLIC_METHODS, handle_tool_method

log = logging.getLogger("mcp")

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
    auth_header = request.headers.get("Authorization", "")
    if auth_header:
        return auth_header

    return (
        request.headers.get("X-API-Key")
        or request.headers.get("x-api-key")
        or request.headers.get("Scanova-API-Key")
        or request.headers.get("scanova-api-key")
        or request.headers.get("API-Key")
        or request.headers.get("api-key")
    )


server = FastMCP()
register_fastmcp_tools(server)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "scanova-mcp"}


@app.get("/.well-known/oauth-protected-resource")
async def oauth_protected_resource():
    return {
        "resource": MCP_RESOURCE_URL,
        "authorization_servers": [OAUTH_SERVER_URL] if OAUTH_SERVER_URL else [],
    }


@app.get("/.well-known/oauth-protected-resource/mcp")
async def oauth_protected_resource_mcp():
    return {
        "resource": MCP_RESOURCE_URL,
        "authorization_servers": [OAUTH_SERVER_URL] if OAUTH_SERVER_URL else [],
    }

@app.get("/mcp/.well-known/oauth-protected-resource")
async def oauth_protected_resource_mcp_prefixed():
    return {
        "resource": MCP_RESOURCE_URL,
        "authorization_servers": [OAUTH_SERVER_URL] if OAUTH_SERVER_URL else [],
    }

@app.get("/.well-known/openai-apps-challenge", response_class=PlainTextResponse)
async def openai_apps_challenge():
    return OPENAI_APPS_CHALLENGE if OPENAI_APPS_CHALLENGE else "No challenge token configured"


@app.post("/mcp")
async def mcp_endpoint(request: Request):
    try:
        body = await request.json()
        method = body.get("method")
        api_key = extract_api_key(request)

        if method not in PUBLIC_METHODS and not api_key:
            log.warning("Unauthorized access attempt to method: %s", method)
            return JSONResponse(
                content={"error": "unauthorized", "message": "Valid Bearer token required"},
                status_code=401,
                headers={
                    "WWW-Authenticate": (
                        f'Bearer realm="Scanova MCP", resource_metadata="'
                        f'{MCP_RESOURCE_URL}/.well-known/oauth-protected-resource/mcp'
                    )
                },
            )

        result = handle_tool_method(method, body, api_key)
        if result is None:
            # Notification methods must not return a response body
            return Response(status_code=202)
        return JSONResponse(content=result)

    except Exception as e:
        log.error("MCP endpoint error: %s", e)
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": body.get("id") if "body" in locals() else None,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
            },
            status_code=500,
        )


@app.get("/")
async def root():
    return {
        "service": "Scanova MCP Server",
        "version": "1.0.0",
        "endpoints": {
            "mcp": "/mcp",
            "health": "/health",
        },
        "authentication": {
            "required": "Scanova API Key",
            "headers": ["Authorization", "X-API-Key", "Scanova-API-Key"],
            "note": "Configure your Scanova API key in your MCP client headers",
        },
    }


@app.post("/")
async def rootPost(request: Request):
    return {
        "service": "Scanova MCP Server",
        "version": "1.0.0",
        "endpoints": {
            "mcp": "/mcp",
            "health": "/health",
        },
        "authentication": {
            "required": "Scanova API Key",
            "headers": ["Authorization", "X-API-Key", "Scanova-API-Key"],
            "note": "Configure your Scanova API key in your MCP client headers",
        },
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    log.info("Starting Scanova MCP Server on %s:%s", host, port)
    log.info("MCP Endpoint: http://%s:%s/mcp", host, port)
    log.info("Health Check: http://%s:%s/health", host, port)
    log.info("Authentication: Configure your Scanova API key in MCP client headers")
    log.error("test error log")

    uvicorn.run(app, host=host, port=port)
