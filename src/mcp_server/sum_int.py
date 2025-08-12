from mcp.server.fastmcp import FastMCP

# 创建一个MCP服务器实例
mcp = FastMCP("pymcp")


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


if __name__ == "__main__":
    # 运行MCP服务器
    mcp.run()