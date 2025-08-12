#!/usr/bin/env python3
"""
测试MCP服务器的客户端脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "mcp_server"))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_add_tool():
    """测试add工具函数"""
    # 配置服务器参数
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["src/mcp_server/sum_int.py"]
    )
    
    # 创建stdio客户端连接
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化会话
            await session.initialize()
            
            # 列出可用工具
            print("Available tools:")
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")
            # 检查是否存在sum工具
            sum_tool = next((tool for tool in tools.tools if tool.name == "sum"), None)
            assert sum_tool is not None, "sum tool should be available"
            
            # 调用sum工具进行测试
            print("\nTesting sum tool:")
            result = await session.call_tool("sum", {"a": 5, "b": 3})
            print(f"Result of 5 + 3: {result}")
            
            # 验证结果
            assert not result.isError, "Result should not be an error"
            assert result.structuredContent['result'] == 8, f"Expected 8, but got {result.structuredContent['result']}"
            
            # 测试其他数值
            result2 = await session.call_tool("sum", {"a": -2, "b": 7})
            assert result2.structuredContent['result'] == 5, f"Expected 5, but got {result2.structuredContent['result']}"
            
            result3 = await session.call_tool("sum", {"a": 0, "b": 0})
            assert result3.structuredContent['result'] == 0, f"Expected 0, but got {result3.structuredContent['result']}"
            
            print("All tests passed!")


if __name__ == "__main__":
    asyncio.run(test_add_tool())