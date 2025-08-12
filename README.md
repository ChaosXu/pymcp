# pymcp
a MCP server

## SDK
https://github.com/modelcontextprotocol/python-sdk

## 项目结构
```
src/
└── mcp_server/
    ├── __init__.py
    └── sum_int.py        # MCP服务器实现，提供两个整数相加功能

tests/
├── test_sum_int.py                # 基础功能测试
├── test_sum_int_with_real_llm.py  # 真实LLM调用测试
└── test_sum_int_with_agent.py     # 使用LangChain Agent的测试
```

## 环境初始化

### 安装依赖
使用 uv 管理依赖：

```bash
# 安装生产依赖
uv pip install -e .

# 安装测试依赖（包括生产依赖）
uv pip install -e .[test]
```

### 配置环境变量
创建 `.env` 文件并配置LLM相关参数：

```bash
cp .env.example .env
```

编辑 `.env` 文件，添加以下内容：
```
LLM_BASE_URL=https://api.siliconflow.cn/v1
LLM_API_KEY=your_api_key_here
LLM_MODEL=Qwen/Qwen3-8B
```

## 运行MCP服务器

```bash
# 运行MCP服务器
uv run mcp dev src/mcp_server/sum_int.py
```

或者直接运行：
```bash
python src/mcp_server/sum_int.py
```


### 真实LLM调用测试
```bash
python tests/test_sum_int_with_real_llm.py
```

### 使用LangChain Agent的测试
```bash
python tests/test_sum_int_with_agent.py
```

## 依赖说明

生产依赖：
- `mcp[cli]>=1.12.4` - MCP Python SDK

测试依赖：
- `openai>=1.99.9` - OpenAI Python客户端
- `python-dotenv>=1.0.1` - 环境变量加载工具
- `httpx[socks]>=0.28.1` - HTTP客户端（支持SOCKS代理）
- `langchain>=0.3.27` - LangChain核心库
- `langchain-openai>=0.3.29` - LangChain的OpenAI集成
- `langchain-mcp-adapters>=0.1.9` - LangChain与MCP的适配器
- `langgraph>=0.6.4` - LangGraph库，用于构建agent工作流