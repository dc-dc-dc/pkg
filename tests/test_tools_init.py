import pytest
from pkg.tools import get_tool, TOOLS
from pkg.tools.uv import UvTool


def test_get_tool_uv():
    tool_class = get_tool("uv")
    assert tool_class is UvTool


def test_get_tool_unknown():
    with pytest.raises(ValueError, match="Unknown tool"):
        get_tool("unknown")


def test_tools_registry():
    assert "uv" in TOOLS
