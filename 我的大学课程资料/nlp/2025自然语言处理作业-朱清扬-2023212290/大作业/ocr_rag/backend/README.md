# 多模态 RAG 工作台 - 后端 API

基于 LangChain 1.0 的智能对话后端服务，支持 GPT-5 等最新模型。

## 🚀 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置 API Key

修改 `env_config.py` 文件中的 OpenAI API Key：

```python
os.environ["OPENAI_API_KEY"] = "your_actual_api_key_here"
```

### 3. 启动服务

```bash
python start.py
```

服务将在 `http://localhost:8000` 启动

## 📚 API 接口

### 流式聊天接口
- **URL**: `POST /api/chat/stream`
- **Content-Type**: `application/json`
- **Response**: `text/event-stream`

```json
{
  "content": "你好",
  "history": [],
  "model": "gpt-4o",
  "knowledge_base": "default"
}
```

### 同步聊天接口
- **URL**: `POST /api/chat`
- **Content-Type**: `application/json`

### 健康检查
- **URL**: `GET /`

### 模型列表
- **URL**: `GET /api/models`

### 知识库列表
- **URL**: `GET /api/knowledge-bases`

## 🧪 测试

运行测试客户端：

```bash
python test_client.py
```

## 📖 API 文档

访问 `http://localhost:8000/docs` 查看交互式 API 文档。

## 🔧 配置说明

### 支持的模型
- `gpt-4o` - GPT-4 优化版本
- `gpt-4o-mini` - 轻量级版本
- `gpt-5` - 下一代模型（如果可用）

### 环境变量
- `OPENAI_API_KEY` - OpenAI API 密钥
- `OPENAI_BASE_URL` - API 基础URL
- `HOST` - 服务器主机
- `PORT` - 服务器端口
- `DEBUG` - 调试模式
- `LOG_LEVEL` - 日志级别

## 🔗 前端对接

前端通过 `src/api/chat.ts` 与后端通信，支持：
- 流式文本响应
- 历史对话管理
- 错误处理
- 模型切换 