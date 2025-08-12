#!/usr/bin/env python3
"""
使用真实LLM模型调用sum_int工具的测试脚本
"""

import asyncio
import sys
from pathlib import Path
import json
import os
from dotenv import load_dotenv

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "mcp_server"))

# 尝试加载.env文件
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

try:
    import openai
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from mcp.types import Tool

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI dependencies not found. Install with: pip install openai")


def get_tool_definition(tool: Tool) -> dict:
    """将MCP工具转换为OpenAI函数格式"""
    # 构建参数规范
    properties = {}
    required = []

    # 根据工具输入模式动态构建参数
    if hasattr(tool, "inputSchema") and tool.inputSchema:
        input_schema = tool.inputSchema
        if isinstance(input_schema, dict):
            properties = input_schema.get("properties", {})
            required = input_schema.get("required", [])

    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


if OPENAI_AVAILABLE:

    async def test_real_llm_with_mcp():
        """使用真实LLM模型调用sum_int工具"""
        # 配置服务器参数
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["src/mcp_server/sum_int.py"],
        )

        # 从环境变量获取配置，不提供默认值
        base_url = os.environ.get("LLM_BASE_URL")
        api_key = os.environ.get("LLM_API_KEY")
        model = os.environ.get("LLM_MODEL")

        # 检查环境变量是否设置
        if not base_url:
            raise ValueError("LLM_BASE_URL environment variable is not set")
        if not api_key:
            raise ValueError("LLM_API_KEY environment variable is not set")
        if not model:
            raise ValueError("LLM_MODEL environment variable is not set")

        # 初始化客户端
        client = openai.AsyncOpenAI(base_url=base_url, api_key=api_key)

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 初始化连接
                await session.initialize()

                # 获取工具信息
                tools_list = await session.list_tools()
                print(f"Available tools: {[tool.name for tool in tools_list.tools]}")

                # 从MCP服务器的list_tools结果中动态构建工具定义
                tools_definition = []
                for tool in tools_list.tools:
                    tool_definition = get_tool_definition(tool)
                    print(f"{json.dumps(tool_definition, indent=2)}\n")

                    tools_definition.append(tool_definition)

                # 测试问题
                question = "Calculate the sum of 123 and 456"
                print(f"\n--- Testing question: {question} ---")

                # 调用LLM
                response = await client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that can perform mathematical calculations using available tools.",
                        },
                        {"role": "user", "content": question},
                    ],
                    tools=tools_definition,
                    tool_choice="auto",
                )

                # 检查是否需要调用工具
                message = response.choices[0].message
                if message.tool_calls:
                    for tool_call in message.tool_calls:
                        # 调用MCP工具
                        args = json.loads(tool_call.function.arguments)
                        print(
                            f"LLM wants to call {tool_call.function.name} with args: {args}"
                        )

                        # 调用MCP工具
                        tool_result = await session.call_tool(
                            tool_call.function.name, args
                        )
                        print(f"Tool result: {tool_result.structuredContent['result']}")

                        # 将结果返回给LLM
                        final_response = await client.chat.completions.create(
                            model=model,
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are a helpful assistant that can perform mathematical calculations using available tools.",
                                },
                                {"role": "user", "content": question},
                                {
                                    "role": "assistant",
                                    "content": None,
                                    "tool_calls": [tool_call],
                                },
                                {
                                    "role": "tool",
                                    "content": str(
                                        tool_result.structuredContent["result"]
                                    ),
                                    "tool_call_id": tool_call.id,
                                },
                            ],
                        )

                        print(
                            f"LLM final response: {final_response.choices[0].message.content}"
                        )
                else:
                    print(f"LLM response without tool calling: {message.content}")

                print("\n=== Real LLM Test Completed ===")

    def main():
        """主函数"""
        if not OPENAI_AVAILABLE:
            print("Cannot run real LLM tests without OpenAI dependencies.")
            print("Install dependencies with: pip install openai")
            return

        print("=== Real LLM Integration Test ===")
        base_url = os.environ.get("LLM_BASE_URL")
        model = os.environ.get("LLM_MODEL")

        # 检查环境变量是否设置
        if not base_url:
            print("Error: LLM_BASE_URL environment variable is not set")
            return
        if not model:
            print("Error: LLM_MODEL environment variable is not set")
            return

        print(f"Using API base URL: {base_url}")
        print(f"Using model: {model}")

        try:
            asyncio.run(test_real_llm_with_mcp())
        except Exception as e:
            print(f"Test failed with error: {e}")
            import traceback
            traceback.print_exc()

    if __name__ == "__main__":
        main()
else:

    def main():
        print("Cannot run real LLM tests without OpenAI dependencies.")
        print("Install dependencies with: pip install openai")

    if __name__ == "__main__":
        main()
