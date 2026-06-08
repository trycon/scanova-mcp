from mcp.server.fastmcp import FastMCP
from mcp_http.fastmcp_tools import register_fastmcp_tools

server = FastMCP()
register_fastmcp_tools(server)
