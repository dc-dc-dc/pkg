from .base import BuildTool
from .uv import UvTool

TOOLS: dict[str, type[BuildTool]] = {
    "uv": UvTool,
}


def get_tool(name: str) -> type[BuildTool]:
    if name not in TOOLS:
        raise ValueError(f"Unknown tool: {name}. Available: {', '.join(TOOLS.keys())}")
    return TOOLS[name]
