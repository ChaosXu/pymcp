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
├── test_sum_int.py                                # 基础功能测试
├── test_sum_int_with_real_llm.py                  # 真实LLM调用测试
├── test_sum_int_with_agent.py                     # 使用LangChain Agent的测试 (stdio方式)
├── test_sum_int_with_agent_sse.py                 # 使用LangChain Agent的测试 (SSE方式)
└── test_sum_int_with_agent_streamable_http.py     # 使用LangChain Agent的测试 (Streamable HTTP方式)
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

### 环境变量配置

复制 `.env.example` 文件并重命名为 `.env`，然后根据你的实际情况修改其中的值：

```bash
cp .env.example .env
```

环境变量说明：
- `LLM_BASE_URL`：LLM API的基础URL
- `LLM_API_KEY`：访问LLM API的密钥
- `LLM_MODEL`：要使用的模型名称
- `MCP_SERVER_PORT`：MCP服务器端口（默认为8000）

## 运行MCP服务器

MCP服务器支持多种传输方式：

### stdio方式（默认）
```bash
# 运行MCP服务器（stdio方式）
uv run mcp dev src/mcp_server/sum_int.py

# 或者直接运行
python src/mcp_server/sum_int.py

# 或者显式指定stdio方式
python src/mcp_server/sum_int.py stdio
```

### SSE方式
```bash
# 使用SSE方式运行
python src/mcp_server/sum_int.py sse
```

服务器将在 http://127.0.0.1:8000 启动

### Streamable HTTP方式
```bash
# 使用Streamable HTTP方式运行
python src/mcp_server/sum_int.py streamable-http
```

服务器将在 http://127.0.0.1:8000 启动

## 执行测试

### 基础功能测试
```bash
python tests/test_sum_int.py
```

### 真实LLM调用测试
```bash
python tests/test_sum_int_with_real_llm.py
```

### 使用LangChain Agent的测试 (stdio方式)
```bash
python tests/test_sum_int_with_agent.py
```

### 使用LangChain Agent的测试 (SSE方式)
```bash
python tests/test_sum_int_with_agent_sse.py
```

### 使用LangChain Agent的测试 (Streamable HTTP方式)
```bash
python tests/test_sum_int_with_agent_streamable_http.py
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