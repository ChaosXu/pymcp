#!/usr/bin/env python3
"""
模拟LLM执行sum_int工具的测试脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "mcp_server"))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_llm_execution():
    """模拟LLM执行sum_int工具"""
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
            
            # 获取工具列表
            print("=== LLM Tool Execution Simulation ===")
            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools.tools]}")
            
            # 模拟LLM根据用户问题选择并调用工具
            user_questions = [
                "What is 15 plus 25?",
                "Calculate the sum of 123 and 456",
                "What do you get when you add -10 and 30?",
                "Find the result of 0 + 100"
            ]
            
            expected_results = [40, 579, 20, 100]
            
            for i, question in enumerate(user_questions):
                print(f"\n--- User Question {i+1}: {question} ---")
                
                # 模拟LLM分析问题并提取参数
                # 在实际应用中，这部分由LLM完成，这里我们直接给出参数
                a, b = extract_numbers_from_question(question)
                print(f"LLM extracted parameters: a={a}, b={b}")
                
                # 调用sum工具
                result = await session.call_tool("sum", {"a": a, "b": b})
                
                # 模拟LLM生成自然语言响应
                sum_result = result.structuredContent['result']
                llm_response = generate_natural_response(question, a, b, sum_result)
                print(f"LLM response: {llm_response}")
                
                # 验证结果
                assert sum_result == expected_results[i], \
                    f"Expected {expected_results[i]}, but got {sum_result}"
                print(f"✓ Test passed: {a} + {b} = {sum_result}")
            
            print("\n=== All LLM Simulation Tests Passed! ===")


def extract_numbers_from_question(question):
    """从问题中提取两个数字（模拟LLM的参数提取能力）"""
    # 这是一个简化的实现，实际LLM会更智能地处理各种问题表述
    if "15 plus 25" in question:
        return 15, 25
    elif "sum of 123 and 456" in question:
        return 123, 456
    elif "add -10 and 30" in question:
        return -10, 30
    elif "0 + 100" in question:
        return 0, 100
    else:
        # 默认返回值
        return 1, 1


def generate_natural_response(question, a, b, result):
    """生成自然语言响应（模拟LLM的响应生成能力）"""
    return f"The sum of {a} and {b} is {result}."


async def test_complex_llm_scenario():
    """测试更复杂的LLM场景"""
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
            
            print("\n=== Complex LLM Scenario Test ===")
            
            # 模拟LLM进行多步推理
            print("User: I bought 3 apples at $2 each and 5 oranges at $3 each. How much did I spend in total?")
            
            # 第一步：计算苹果总价
            apple_cost = await session.call_tool("sum", {"a": 2, "b": 2, "b_count": 2})  # 2+2+2 = 2*3
            # 由于我们只有两数相加的工具，需要分步执行
            step1 = await session.call_tool("sum", {"a": 2, "b": 2})  # 4
            step2 = await session.call_tool("sum", {"a": step1.structuredContent['result'], "b": 2})  # 6
            
            # 第二步：计算橙子总价
            step3 = await session.call_tool("sum", {"a": 3, "b": 3})  # 6
            step4 = await session.call_tool("sum", {"a": step3.structuredContent['result'], "b": 3})  # 9
            step5 = await session.call_tool("sum", {"a": step4.structuredContent['result'], "b": 3})  # 12
            step6 = await session.call_tool("sum", {"a": step5.structuredContent['result'], "b": 3})  # 15
            
            # 第三步：计算总花费
            total_cost = await session.call_tool("sum", 
                                               {"a": step2.structuredContent['result'], 
                                                "b": step6.structuredContent['result']})
            
            print(f"LLM: You spent $6 on apples and $15 on oranges, for a total of ${total_cost.structuredContent['result']}.")
            assert total_cost.structuredContent['result'] == 21, \
                f"Expected total cost of 21, but got {total_cost.structuredContent['result']}"
            
            print("✓ Complex scenario test passed!")


async def main():
    """主函数，运行所有LLM模拟测试"""
    await test_llm_execution()
    await test_complex_llm_scenario()


if __name__ == "__main__":
    asyncio.run(main())