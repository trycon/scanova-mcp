from mcp.types import ToolAnnotations

READ_ONLY_TOOL_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True, openWorldHint=True, destructiveHint=False
)
WRITE_TOOL_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False, openWorldHint=True, destructiveHint=False
)

READ_ONLY_TOOL_ANNOTATIONS_JSON = {
    "readOnlyHint": True,
    "openWorldHint": True,
    "destructiveHint": False,
}
WRITE_TOOL_ANNOTATIONS_JSON = {
    "readOnlyHint": False,
    "openWorldHint": True,
    "destructiveHint": False,
}
DESTRUCTIVE_TOOL_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False, openWorldHint=True, destructiveHint=True
)
DESTRUCTIVE_TOOL_ANNOTATIONS_JSON = {
    "readOnlyHint": False,
    "openWorldHint": True,
    "destructiveHint": True,
}
