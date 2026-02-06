from .base import BuildTool
from .bun import BunTool
from .uv import UvTool

TOOLS: dict[str, type[BuildTool]] = {
    "bun": BunTool,
    "uv": UvTool,
}


def get_tool(name: str) -> type[BuildTool]:
    if name not in TOOLS:
        raise ValueError(f"Unknown tool: {name}. Available: {', '.join(TOOLS.keys())}")
    return TOOLS[name]
