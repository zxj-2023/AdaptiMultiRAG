# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于Python的RAG（检索增强生成）后端系统，结合LangGraph智能体框架。项目使用uv进行依赖管理，支持智能对话、知识库管理、文档检索和爬虫功能。

## 常用开发命令

### Docker Compose 一键部署（推荐）

```bash
# 在项目根目录 (AdaptiMultiRAG/) 执行

# 环境配置
cp .env.docker.example .env              # 复制 Docker 环境变量模板
# 编辑 .env 文件,配置 DASHSCOPE_API_KEY 和数据库密码

# 启动所有后端服务
docker compose up -d                     # 一键启动全部服务
docker compose ps                        # 查看所有容器状态
docker compose logs -f app               # 查看应用日志
docker compose down                      # 停止所有服务
docker compose down -v                   # 停止并删除所有数据卷（⚠️ 不可恢复）

# 重建应用镜像
docker compose build app
docker compose up -d --force-recreate app

# 服务地址
# - API服务: http://0.0.0.0:8000
# - API文档: http://0.0.0.0:8000/docs
# - MySQL: 端口 3306
# - PostgreSQL: 端口 5432
# - Milvus: 端口 19530
# - MinIO控制台: http://localhost:9001 (minioadmin/minioadmin)
# - Neo4j Browser: http://localhost:7474
# - Redis: 端口 6379
```

### 本地开发（非 Docker）

```bash
# 环境配置
cp backend/.env.example backend/.env    # 复制环境变量模板
# 编辑 backend/.env 文件,配置必需的环境变量

# 依赖管理
uv sync                    # 安装依赖
uv add <package>          # 添加依赖
uv remove <package>       # 移除依赖

# 启动服务
python main.py            # 启动FastAPI服务（端口8000）

# LangGraph相关
langgraph dev             # 启动LangGraph Studio开发环境
langgraph build           # 构建LangGraph应用

# 测试
uv run pytest backend/tests/              # 运行所有测试
uv run pytest -v                          # 详细测试输出
uv run pytest backend/tests/test_raggraph_simple.py -v    # 运行特定测试文件
```

## 项目架构

### 核心目录结构
```
rag-backend/
├── main.py                     # FastAPI应用主入口
├── backend/
│   ├── api/                    # API路由层（6个模块）
│   │   ├── rag.py             # RAG相关接口
│   │   ├── chat.py            # 聊天接口（流式/非流式）
│   │   ├── auth.py            # 认证接口
│   │   ├── crawl.py           # 爬虫接口
│   │   ├── knowledge_library.py  # 知识库管理接口
│   │   └── visual_graph.py    # 知识图谱可视化接口
│   ├── agent/                  # LangGraph智能体模块
│   │   ├── graph/             # 图结构定义
│   │   │   ├── raggraph.py    # 主RAG图实现
│   │   │   ├── raggraph_node.py  # 图节点实现
│   │   │   └── studio_graph.py   # Studio专用图
│   │   ├── models/            # 模型管理
│   │   │   ├── chat_model.py  # 对话模型加载器
│   │   │   ├── embeddings.py  # 向量模型加载器
│   │   │   └── raggraph_models.py  # RAG图模型配置
│   │   ├── contexts/          # 上下文管理
│   │   ├── states/            # 状态定义
│   │   ├── prompts/           # 提示词管理
│   │   └── tools/             # 工具函数
│   ├── service/               # 业务服务层
│   │   ├── chat.py           # 聊天服务
│   │   ├── conversation.py   # 会话管理
│   │   ├── knowledge_library.py  # 知识库服务
│   │   ├── auth.py           # 认证服务
│   │   └── crawl.py          # 爬虫服务
│   ├── model/                 # 数据库模型
│   │   ├── user.py           # 用户模型
│   │   ├── conversation.py   # 会话模型
│   │   └── knowledge_library.py  # 知识库模型
│   ├── param/                 # 请求/响应参数定义
│   ├── config/                # 配置模块
│   │   ├── database.py       # 数据库配置（双数据库）
│   │   ├── agent.py          # RAGGraph全局单例
│   │   ├── jwt.py            # JWT配置
│   │   ├── oss.py            # 阿里云OSS配置
│   │   ├── log.py            # 日志配置
│   │   └── dependencies.py   # FastAPI依赖注入
│   ├── rag/                   # RAG核心功能
│   │   ├── chunks/           # 文档切块处理
│   │   └── storage/          # 存储层
│   │       ├── milvus_storage.py    # Milvus向量存储
│   │       ├── lightrag_storage.py  # LightRAG图存储
│   │       └── docker-compose.yml   # Milvus部署配置
│   ├── tests/                # 测试文件
│   └── utils/                # 工具函数
├── langgraph.json            # LangGraph配置
├── pyproject.toml            # uv依赖配置
└── backend/.env              # 环境变量配置
```

### 主要组件

#### 1. FastAPI应用层
- **主入口**: `main.py` - 应用启动、路由注册、生命周期管理
- **API路由**: 6个模块（rag、chat、auth、crawl、knowledge_library、visual_graph）
- **生命周期**: lifespan函数初始化日志、环境变量、RAGGraph单例
- **新增功能**: visual_graph模块提供知识图谱可视化API

#### 2. LangGraph智能体系统
- **核心实现**: `backend/agent/graph/raggraph.py:RAGGraph` - 完整的RAG图计算框架
- **图结构**: 8个节点的工作流
  - start → check_retrieval_needed → (direct_answer | expand_subquestions)
  - expand_subquestions → classify_question_type → (vector_db_retrieval | graph_db_retrieval)
  - 检索节点 → generate_answer → END
- **双模式运行**:
  - 通过 `LANGGRAPH_ENABLE_CHECKPOINT` 环境变量控制（默认 `true`）
  - FastAPI模式: 启用PostgreSQL checkpoint持久化
  - Studio模式: 禁用checkpoint（`langgraph dev` 自动禁用）
- **记忆系统**: 集成langmem库，使用PostgreSQL Store存储长期记忆
- **模型管理**: 支持动态注册模型提供商（qwen、deepseek等）

#### 3. 双数据库架构
- **MySQL**: 业务数据（用户、知识库、会话历史）
  - 单例模式：`DatabaseFactory` 实现线程安全的双重检查锁定
  - 配置来源：环境变量 `DB_URL`
- **PostgreSQL**: LangGraph状态持久化
  - Checkpoint存储：`PostgresSaver` - 保存图执行状态
  - Memory Store：`PostgresStore` - 存储langmem记忆数据
  - 连接池：`ConnectionPool` 共享连接

#### 4. 向量检索系统
- **Milvus**: 主向量数据库（v2.6.0）
  - Docker Compose部署：etcd + MinIO + Milvus standalone
  - 端口：19530（Milvus）、9001（MinIO控制台）
  - 存储实现：`backend/rag/storage/milvus_storage.py`
- **LightRAG**: 图数据库检索
  - 实现：`backend/rag/storage/lightrag_storage.py`
  - Workspace配置：环境变量 `LIGHTRAG_WORKSPACE`

#### 5. 认证系统
- **JWT双token机制**: access token + refresh token
- **实现位置**:
  - 配置：`backend/config/jwt.py`
  - 服务层：`backend/service/auth.py`
  - 中间件：`backend/config/dependencies.py:get_current_user`
- **路由保护**: 所有需要认证的路由使用 `Depends(get_current_user)`

#### 6. 知识库系统
- **数据模型**:
  - `KnowledgeLibrary`: 知识库（支持软删除）
  - `KnowledgeDocument`: 文档管理
- **Collection ID生成**: `kb{library_id}_{timestamp}` 格式
- **权限控制**: 基于user_id的权限验证

### 技术栈
- **包管理**: uv (Python >= 3.12)
- **后端框架**: FastAPI + uvicorn
- **智能体**: LangGraph + LangChain + langmem
- **数据库**: MySQL (业务) + PostgreSQL (图状态)
- **向量数据库**: Milvus + MinIO + etcd
- **文档处理**: PyPDF2, python-docx, mineru (OCR)
- **模型**: 通义千问、DeepSeek、阿里云DashScope
- **云服务**: 阿里云OSS
- **爬虫**: crawl4ai
- **缓存**: Redis

### 环境配置

项目使用 `backend/.env` 文件配置服务。**首次运行请先复制模板文件**:

```bash
cp backend/.env.example backend/.env
# 然后编辑 backend/.env 文件，填写实际配置值
```

#### 必需配置项 ⚠️

以下配置项**必须**正确配置，否则系统无法正常运行:

- `DASHSCOPE_API_KEY`: 阿里云DashScope API密钥（**必须**，用于通义千问模型）
- `DB_URL`: MySQL业务数据库连接串（SQLAlchemy格式）
- `POSTGRES_HOST/PORT/DATABASE/USER/PASSWORD`: PostgreSQL配置（LangGraph状态存储）

#### 完整环境变量清单

**数据库配置**
- `DB_URL`: MySQL连接串，格式: `mysql+pymysql://user:pass@host:3306/db`
- `POSTGRES_HOST`: PostgreSQL主机地址
- `POSTGRES_PORT`: PostgreSQL端口（默认5432）
- `POSTGRES_DATABASE`: PostgreSQL数据库名（默认rag_checkpoint）
- `POSTGRES_USER`: PostgreSQL用户名
- `POSTGRES_PASSWORD`: PostgreSQL密码

**API密钥配置**
- `DASHSCOPE_API_KEY`: 阿里云DashScope API密钥（**必需**）
- `MINERU_API_URL`: MinerU OCR服务地址（可选）
- `MINERU_API_KEY`: MinerU API密钥（可选）
- `DEEPSEEK_API_KEY`: DeepSeek API密钥（可选）

**向量数据库 - Milvus**
- `MILVUS_URI`: 连接地址（默认localhost:19530）
- `MILVUS_DB_NAME`: 数据库名（默认default）
- `MILVUS_COLLECTION_NAME`: 集合名（系统自动生成，格式: kb{id}_{timestamp}）

**图数据库 - LightRAG**
- `LIGHTRAG_WORKSPACE`: 工作空间路径（存储图数据）

**对象存储 - 阿里云OSS**
- `OSS_ACCESS_KEY_ID`: OSS访问密钥ID
- `OSS_ACCESS_KEY_SECRET`: OSS访问密钥Secret
- `OSS_REGION`: OSS地域（如oss-cn-shanghai）
- `OSS_ENDPOINT`: OSS服务端点
- `OSS_BUCKET_NAME`: OSS存储桶名称

**JWT认证**
- `JWT_SECRET_KEY`: JWT签名密钥（生产环境务必使用强随机字符串）
- `JWT_ALGORITHM`: 加密算法（默认HS256）
- `JWT_ACCESS_TOKEN_EXPIRES`: access token过期时间（秒，默认86400=24小时）
- `JWT_REFRESH_TOKEN_EXPIRES`: refresh token过期时间（秒，默认604800=7天）

**Redis配置（可选）**
- `REDIS_HOST`: Redis主机地址（默认127.0.0.1）
- `REDIS_PORT`: Redis端口（默认6379）
- `REDIS_DB`: Redis数据库编号（默认0）
- `REDIS_PASSWORD`: Redis密码（可选）

**应用配置**
- `APP_ENV`: 应用运行模式（development/production）
- `LOG_LEVEL`: 日志级别（DEBUG/INFO/WARNING/ERROR）
- `API_HOST`: API服务主机（默认0.0.0.0）
- `API_PORT`: API服务端口（默认8000）

**LangGraph配置**
- `LANGGRAPH_ENABLE_CHECKPOINT`: 是否启用Checkpoint（生产环境建议true，默认true）
- `LANGGRAPH_STUDIO_MODE`: Studio调试模式（仅开发环境使用）

**图数据库 - Neo4j**
- `NEO4J_URI`: Neo4j Bolt 连接地址（LightRAG Neo4JStorage 使用）
- `NEO4J_USERNAME`: Neo4j 用户名
- `NEO4J_PASSWORD`: Neo4j 密码
- `LIGHTRAG_GRAPH_STORAGE`: 图存储后端（默认 `Neo4JStorage`）

**文档处理配置**
- `CHUNK_SIZE`: 文档切块大小（默认1000）
- `CHUNK_OVERLAP`: 文档切块重叠大小（默认200）
- `MAX_DOCUMENT_SIZE`: 最大文档大小（MB，默认50）

**检索配置**
- `DEFAULT_RETRIEVAL_MODE`: 默认检索模式（vector_only/graph_only/auto/no_retrieval）
- `VECTOR_SEARCH_TOP_K`: 向量检索TopK数量（默认5）
- `GRAPH_SEARCH_MODE`: 图检索模式（local/global/hybrid）

详细配置说明和示例值请参考 `backend/.env.example` 文件。

## 重要配置文件

### langgraph.json
LangGraph Studio配置，定义智能体图：
```json
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./backend/agent/graph/studio_graph.py:graph"
  },
  "env": "./backend/.env"
}
```

### pyproject.toml
uv包管理配置：
- Python >= 3.12版本要求
- 清华/阿里云/中科大镜像源加速
- 开发依赖：pytest、pytest-mock

## 数据库初始化

### MySQL数据库初始化

**Docker Compose 部署无需手动初始化** — FastAPI 启动时自动执行 `Base.metadata.create_all()`（幂等操作，已存在的表不会重复创建）。

**本地开发方式**（如不使用 Docker Compose）:

```bash
# 1. 创建数据库（如果未创建）
mysql -u root -p
CREATE DATABASE rag_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit

# 2. 启动应用时自动建表（main.py lifespan）
# 或手动调用:
python -c "from backend.config.database import DatabaseFactory; DatabaseFactory.get_base().metadata.create_all(DatabaseFactory.get_engine())"
```

**创建的表**:
- `users`: 用户表（id, email, hashed_password, created_at, updated_at）
- `conversations`: 会话表（id, user_id, title, created_at, updated_at）
- `knowledge_libraries`: 知识库表（id, user_id, name, description, collection_id, created_at, updated_at, is_deleted）
- `knowledge_documents`: 知识文档表（id, library_id, file_name, file_path, file_size, created_at）
- `chat_history`: 聊天历史表（id, conversation_id, user_message, assistant_message, created_at）

### PostgreSQL数据库

**无需手动初始化**，LangGraph会在首次运行时自动创建以下表:
- Checkpoint相关表: 存储图执行状态
- Memory Store相关表: 存储langmem记忆数据

**注意**: 确保PostgreSQL服务已启动，并且`.env`文件中的`POSTGRES_*`配置正确。

## 开发注意事项

### 启动顺序

**Docker Compose 一键部署（推荐）**: 在项目根目录执行
```bash
cp .env.docker.example .env  # 首次配置
docker compose up -d          # 自动编排所有服务启动顺序
```

**本地开发**: 手动启动
1. **配置环境变量**: `cp backend/.env.example backend/.env` 并编辑配置
2. **启动 MySQL/PostgreSQL/Redis/Neo4j**（自行安装）
3. **启动Milvus**: `cd backend/rag/storage && docker-compose up -d`
4. **检查服务状态**: `docker-compose ps` 确认Milvus启动成功
5. **启动应用**: `python main.py`（MySQL 表结构自动创建）

### RAGGraph动态创建机制

**重要**: 系统为每个知识库动态创建独立的RAGGraph实例，而非使用全局单例。

#### 实现位置
- **配置模块**: `backend/config/agent.py`
- **核心函数**: `create_rag_graph(collection_id: str) -> RAGGraph`
- **获取函数**: `get_rag_graph_for_collection(collection_id: str) -> RAGGraph`

#### 工作原理
每次聊天请求根据`collection_id`参数动态创建或获取对应的RAGGraph实例:

```python
from backend.config.agent import get_rag_graph_for_collection

# 为特定知识库创建RAG图实例
rag_graph = get_rag_graph_for_collection(collection_id="kb12_1760260169325")

# RAGGraph实例会自动配置:
# 1. workspace参数设置为collection_id
# 2. 关联对应的Milvus collection
# 3. 配置LightRAG图数据库workspace
```

#### Collection ID参数作用
- **Milvus隔离**: 每个collection_id对应独立的Milvus collection
- **LightRAG workspace**: 作为图数据库的工作空间路径
- **多知识库支持**: 实现不同知识库的数据完全隔离
- **动态创建**: 支持运行时动态添加新知识库

#### 模型配置
- **大模型**: 通义千问（qwen3-max-preview）
- **向量模型**: 阿里云text-embedding-v4（1536维）
- **Checkpoint**: 通过 `LANGGRAPH_ENABLE_CHECKPOINT` 环境变量控制（默认 `true`）

### LangGraph双运行模式
- **FastAPI模式**: 生产环境，启用checkpoint和memory store（由 `LANGGRAPH_ENABLE_CHECKPOINT` 控制）
  ```python
  # agent.py 中通过环境变量控制
  enable_checkpointer=os.getenv("LANGGRAPH_ENABLE_CHECKPOINT", "true").lower() in ("true", "1", "yes")
  ```
- **Studio模式**: 开发调试，禁用checkpoint（`langgraph dev` 自动禁用）

### 数据库会话管理
- **创建会话**: `DatabaseFactory.create_session()`
- **使用模式**: try-finally确保关闭
  ```python
  db = DatabaseFactory.create_session()
  try:
      # 数据库操作
      pass
  finally:
      db.close()
  ```
- **不要使用**: `DatabaseFactory.get_session()` (已弃用)

### 流式响应实现
- **聊天流式接口**: `POST /llm/chat/stream`
- **实现位置**: `backend/api/chat.py:chat_stream`
- **Stream模式**:
  - `updates`: 节点更新（默认）
  - `values`: 完整状态
  - `messages`: LLM token流
  - `mix`: 混合模式（messages + updates）
- **数据格式**: Server-Sent Events (SSE)
  ```python
  yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
  ```

### 模型注册和加载
- **注册提供商**: 使用 `register_model_provider` 和 `register_embeddings_provider`
- **加载模型**: 使用 `load_chat_model` 和 `load_embeddings`
- **示例**: 参考 `backend/tests/test_raggraph_simple.py:init_models()`

### 知识库Collection ID规则

#### 生成规则
- **生成时机**: 知识库创建后立即生成
- **格式**: `kb{library_id}_{timestamp_ms}`
- **示例**: `kb12_1760260169325`

#### 用途说明
1. **Milvus Collection标识**: 作为Milvus向量数据库中collection的唯一名称
2. **RAGGraph Workspace**: 作为RAGGraph实例的workspace参数
3. **LightRAG Workspace**: 作为图数据库的工作空间路径
4. **知识图谱路由参数**: 前端访问知识图谱页面时使用（`/knowledge-graph/:collection_id`）
5. **多知识库隔离**: 确保不同知识库的向量和图数据完全隔离

#### 实现位置
- **生成逻辑**: `backend/service/knowledge_library.py`
- **使用位置**:
  - `backend/config/agent.py`: 创建RAGGraph实例
  - `backend/rag/storage/milvus_storage.py`: Milvus collection操作
  - `backend/rag/storage/lightrag_storage.py`: LightRAG workspace配置
  - `backend/api/visual_graph.py`: 知识图谱可视化API

### 测试实践
- **测试位置**: `backend/tests/`
- **重要测试文件**:
  - `test_raggraph_simple.py`: RAGGraph基本测试（invoke和stream）
  - `test_raggraph_vector.py`: 向量检索测试
  - `test_raggraph_lightrag.py`: 图检索测试
  - `test_auth.py`: 认证功能测试
- **模型初始化**: 测试文件需要手动初始化模型，不依赖全局单例

### 日志系统
- **配置**: `backend/config/log.py`
- **初始化**: `setup_default_logging()` 在应用启动时调用
- **获取logger**: `get_logger(__name__)`
- **日志级别**: INFO（默认）

### API认证
- **认证依赖**: `Depends(get_current_user)` - 返回当前用户email
- **token格式**: Bearer token
- **刷新机制**: 使用refresh token获取新的access token
- **路由示例**: `/auth/protected` - 受保护路由示例

### Docker Compose管理
- **Milvus服务**: etcd、MinIO、Milvus standalone
- **数据持久化**: 使用Docker volumes
- **健康检查**: 所有服务配置了健康检查
- **网络**: 自定义网络 `milvus`
