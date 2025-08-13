from mcp.server.fastmcp import FastMCP
import sys
from typing import Literal, cast
import os

# 创建一个MCP服务器实例，支持从环境变量获取端口配置
mcp_port = int(os.environ.get("MCP_SERVER_PORT", "8000"))
mcp = FastMCP("pymcp", port=mcp_port)


# 添加一个加法工具，计算两个整数的和
@mcp.tool()
def sum(a: int, b: int) -> int:
    """
    Add two integers together.
    
    Args:
        a: First integer
        b: Second integer
        
    Returns:
        The sum of the two integers
    """
    return a + b


def run(transport: Literal["stdio", "sse", "streamable-http"] = "stdio"):
    """运行MCP服务器
    
    Args:
        transport: 传输方式，可选值为 "stdio", "sse", "streamable-http"
    """
    mcp.run(transport)


if __name__ == "__main__":
    # 运行MCP服务器，支持指定传输方式
    transport = "stdio"
    if len(sys.argv) > 1:
        transport = sys.argv[1]
    
    # 确保传输方式是有效的选项之一
    if transport not in ["stdio", "sse", "streamable-http"]:
        print(f"Invalid transport: {transport}")
        print("Available transports: stdio (default), sse, streamable-http")
        sys.exit(1)
    
    run(cast(Literal["stdio", "sse", "streamable-http"], transport))