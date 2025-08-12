#!/usr/bin/env python3
"""
通过agent使用MCP的测试脚本
"""

import asyncio
import sys
from pathlib import Path
import os
from dotenv import load_dotenv
import logging

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "mcp_server"))

# 尝试加载.env文件
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# 设置日志级别以显示更多LangChain内部信息
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from langchain_mcp_adapters.tools import load_mcp_tools
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
    from langgraph.prebuilt import create_react_agent
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    print(f"Warning: LangChain dependencies not found. Install with: pip install langchain langchain-openai langchain-mcp-adapters langgraph")
    print(f"Import error: {e}")


if LANGCHAIN_AVAILABLE:
    async def test_agent_with_mcp():
        """测试通过agent使用MCP"""
        # 从环境变量获取配置
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
        
        # 配置服务器参数
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["src/mcp_server/sum_int.py"],
        )
        
        # 使用指定的LLM配置
        try:
            model = ChatOpenAI(
                model=model,
                base_url=base_url,
                api_key=api_key,
                temperature=0  # 降低随机性以获得更一致的结果
            )
        except Exception as e:
            print(f"Failed to initialize model: {e}")
            raise
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 初始化连接
                await session.initialize()
                
                # 加载MCP工具
                tools = await load_mcp_tools(session)
                print(f"Loaded tools: {[tool.name for tool in tools]}")
                
                # 创建agent
                agent = create_react_agent(model, tools)
                
                # 测试问题列表
                test_questions = [
                    "What is 15 plus 25?",
                    "Calculate the sum of 123 and 456"
                ]
                
                expected_results = [40, 579]
                
                for i, question in enumerate(test_questions):
                    print(f"\n{'='*50}")
                    print(f"Testing question {i+1}: {question}")
                    print(f"{'='*50}")
                    
                    try:
                        # 显示发送给agent的消息
                        print(f"\n[User Message] Sending to agent:")
                        print(f"  Content: {question}")
                        
                        # 调用agent
                        response = await agent.ainvoke({
                            "messages": [HumanMessage(content=question)]
                        })
                        
                        # 显示完整的对话历史
                        print(f"\n[Agent Messages] Full conversation history:")
                        for j, msg in enumerate(response['messages']):
                            if isinstance(msg, HumanMessage):
                                print(f"  Message {j+1} [Human]: {msg.content}")
                            elif isinstance(msg, AIMessage):
                                print(f"  Message {j+1} [AI]: {msg.content}")
                                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                    print(f"    Tool Calls: {msg.tool_calls}")
                            elif isinstance(msg, ToolMessage):
                                print(f"  Message {j+1} [Tool]: {msg.content}")
                        
                        # 输出最终响应
                        agent_response = response['messages'][-1].content
                        print(f"\n[Final Response] Agent final response:")
                        print(f"  {agent_response}")
                        
                        # 验证结果是否包含预期值
                        if str(expected_results[i]) in agent_response:
                            print(f"\n✓ Test passed: Response contains expected result {expected_results[i]}")
                        else:
                            print(f"\n⚠ Warning: Response may not contain expected result {expected_results[i]}")
                            
                    except Exception as e:
                        print(f"Error processing question '{question}': {e}")
                        import traceback
                        traceback.print_exc()
                
                print(f"\n{'='*50}")
                print("Agent with MCP Tests Completed")
                print(f"{'='*50}")


    def main():
        """主函数"""
        if not LANGCHAIN_AVAILABLE:
            print("Cannot run agent tests without LangChain dependencies.")
            print("Install dependencies with: pip install langchain langchain-openai langchain-mcp-adapters langgraph")
            return
        
        print("=== Agent with MCP Integration Test ===")
        base_url = os.environ.get("LLM_BASE_URL")
        model = os.environ.get("LLM_MODEL")
        print(f"Using API base URL: {base_url}")
        print(f"Using model: {model}")
        
        try:
            asyncio.run(test_agent_with_mcp())
        except Exception as e:
            print(f"Test failed with error: {e}")
            import traceback
            traceback.print_exc()


    if __name__ == "__main__":
        main()
else:
    def main():
        print("Cannot run agent tests without LangChain dependencies.")
        print("Install dependencies with: pip install langchain langchain-openai langchain-mcp-adapters langgraph")

    if __name__ == "__main__":
        main()