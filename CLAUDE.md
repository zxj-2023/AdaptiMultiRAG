# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 回答规矩

- 思考推理过程和回答一律使用简体中文的形式呈现



## 项目概述

这是一个全栈RAG(检索增强生成)系统,包含前端和后端两个独立项目:

- **rag-backend/**: Python后端,基于FastAPI + LangGraph智能体框架,支持向量检索、图检索、记忆管理等功能
- **rag-frontend/**: Vue 3前端,提供智能对话、知识库管理和文档上传界面

**重要**: 每个子项目都有自己详细的CLAUDE.md文档,请查看对应目录下的文档获取详细信息。

## 快速开始

### 推荐方式: Docker Compose 一键部署 (无需本地安装数据库)

```bash
# 1. 配置环境变量
cp .env.docker.example .env
# 编辑 .env 文件,配置 DASHSCOPE_API_KEY 和数据库密码

# 2. 一键启动所有后端服务
docker compose up -d
# 自动启动 MySQL, PostgreSQL, Redis, Milvus, Neo4j, FastAPI

# 3. 检查服务状态
docker compose ps
curl http://localhost:8000/health

# 4. 前端启动 (本地开发)
cd rag-frontend
npm install && npm run dev
```

### 本地开发方式 (非 Docker)

**后端环境变量配置** (必需):
```bash
cd rag-backend/backend
cp .env.example .env
# 编辑 .env 文件,配置以下必需项:
# - DASHSCOPE_API_KEY: 阿里云API密钥 (必须)
# - DB_URL: MySQL连接串
# - POSTGRES_*: PostgreSQL配置
# 详细配置说明见 .env.example 文件注释
```

### 数据库初始化 (本地开发)

**MySQL数据库初始化** (首次运行必需 - 仅本地开发):
```bash
# Docker Compose 方式无需手动初始化，FastAPI 启动时自动建表
# 本地开发方式:
mysql -u root -p
CREATE DATABASE rag_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit
```

**PostgreSQL数据库**:
- LangGraph会自动创建checkpoint和store相关表
- 确保POSTGRES_*环境变量配置正确

### 后端启动 (本地开发)
```bash
cd rag-backend

# 1. 启动Milvus向量数据库(必须先启动)
cd backend/rag/storage && docker-compose up -d

# 2. 安装依赖
uv sync

# 3. 配置环境变量 (见上方"环境配置"章节)

# 4. 初始化数据库 (首次运行,见上方"数据库初始化"章节)

# 5. 启动FastAPI服务
python main.py
# API服务: http://0.0.0.0:8000
# API文档: http://0.0.0.0:8000/docs
```

### 前端启动
```bash
cd rag-frontend

# 1. 安装依赖
npm install

# 2. 启动开发服务器
npm run dev
# 前端服务: http://localhost:5173
```

## 开发文档

- **后端开发**: 查看 `rag-backend/CLAUDE.md` - 包含完整的架构说明、API设计、数据库配置、LangGraph使用等
- **前端开发**: 查看 `rag-frontend/CLAUDE.md` - 包含Vue 3架构、组件设计、状态管理、路由配置等

## 项目架构

### 技术栈总览

**后端 (rag-backend/)**
- 框架: FastAPI + uvicorn
- 智能体: LangGraph + LangChain + langmem
- 数据库: MySQL (业务) + PostgreSQL (图状态)
- 向量数据库: Milvus + MinIO + etcd
- 图数据库: Neo4j (LightRAG 知识图谱)
- 缓存: Redis (爬虫状态)
- 文档处理: PyPDF2, python-docx, mineru (OCR)
- 模型: 通义千问、DeepSeek、阿里云DashScope
- 包管理: uv (Python >= 3.12)
- 部署: Docker Compose (一键启动所有服务)

**前端 (rag-frontend/)**
- 框架: Vue 3 (Composition API)
- 构建工具: Vite 7.x
- UI组件库: Element Plus
- 状态管理: Pinia
- 路由: Vue Router 4
- 样式: Tailwind CSS + Tailwind Typography

### 核心功能

1. **智能对话**: 基于LangGraph的RAG智能体,支持流式和非流式响应
2. **知识库管理**: 支持PDF、DOCX文档上传、切块、向量化
3. **双模式检索**: 向量数据库(Milvus) + 图数据库(LightRAG)
4. **记忆管理**: 基于langmem的长期记忆系统
5. **用户认证**: JWT双token机制(access + refresh)
6. **对话历史**: 会话管理和历史记录
7. **知识图谱可视化**: 基于ECharts的知识库实体和关系可视化

## 服务依赖

**Docker Compose 自动化编排**（推荐）:
```bash
docker compose up -d  # 一键启动，自动管理启动顺序
```
启动顺序:
1. **etcd**: Milvus 元数据存储
2. **MinIO**: Milvus 对象存储
3. **Milvus 向量数据库**: 向量检索
4. **MySQL 数据库**: 业务数据存储
5. **PostgreSQL 数据库**: LangGraph 状态存储
6. **Redis**: 缓存
7. **Neo4j 图数据库**: LightRAG 知识图谱存储
8. **FastAPI 后端**: API 服务
9. **Vite 前端**: 开发服务器（本地运行）

**本地开发**（手动启动）:
1. **Milvus向量数据库** (必须): Docker Compose部署
2. **MySQL数据库** (必须): 业务数据存储
3. **PostgreSQL数据库** (必须): LangGraph状态存储
4. **后端API服务**: FastAPI
5. **前端开发服务器**: Vite

默认端口:
- 前端: 5173
- 后端API: 8000
- MySQL: 3306
- PostgreSQL: 5432
- Milvus: 19530
- MinIO控制台: 9001
- Redis: 6379
- Neo4j Browser: 7474
- Neo4j Bolt: 7687

## 测试

### 后端测试
```bash
cd rag-backend
uv run pytest backend/tests/              # 运行所有测试
uv run pytest -v                          # 详细输出
uv run pytest backend/tests/test_raggraph_simple.py -v    # 运行特定测试
```

### 前端构建
```bash
cd rag-frontend
npm run build                             # 构建生产版本
npm run preview                           # 预览构建结果
```

## Collection ID规则

知识库创建后会生成唯一的Collection ID用于标识和隔离不同知识库:

- **格式**: `kb{library_id}_{timestamp_ms}`
- **示例**: `kb12_1760260169325`
- **用途**:
  - 关联Milvus向量数据库中的collection
  - 作为RAGGraph实例的workspace参数
  - 知识图谱可视化的路由参数
  - 实现多知识库数据隔离

## 开发注意事项

1. **环境变量配置**: Docker 部署使用根目录 `.env`（模板: `.env.docker.example`），本地开发使用 `rag-backend/backend/.env`
2. **数据库初始化**: Docker 部署无需手动初始化，FastAPI 启动时自动建表（幂等）
3. **Docker Compose 一键启动**: `docker compose up -d` 自动管理所有服务启动顺序和健康检查
4. **双数据库配置**: 后端同时使用MySQL和PostgreSQL，Docker 中通过 `depends_on` 保证启动顺序
5. **API代理配置**: 前端开发时通过Vite代理转发请求到后端8000端口,需要配置所有API路径(不仅仅是`/api`)
6. **认证机制**: 前端使用localStorage存储token,后端自动验证JWT
7. **LangGraph双模式**: 通过 `LANGGRAPH_ENABLE_CHECKPOINT` 环境变量控制checkpoint开关（默认true）
8. **Collection ID生成**: 创建知识库时自动生成,用于多知识库隔离
9. **Neo4j 图数据库**: LightRAG 知识图谱存储，通过 `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` 配置

## 常见问题

### Docker Compose 启动失败
**检查清单**:
- `.env` 文件是否存在且配置正确: `ls -la .env`
- Docker 服务是否运行: `docker ps`
- 端口是否被占用: `netstat -an | grep -E "3306|5432|6379|7474|7687|8000|9001|19530"`
- 查看服务日志: `docker compose logs <service_name>`
- 重建应用镜像: `docker compose build app && docker compose up -d`

### 前端API请求404
**原因**: Vite代理配置不完整,仅配置了`/api`路径
**解决**: 需要在`rag-frontend/vite.config.js`中配置所有后端路径(`/auth`, `/llm`, `/knowledge`, `/crawl`等)
**详见**: [rag-frontend/CLAUDE.md](rag-frontend/CLAUDE.md) 中的"Vite代理配置"章节

### 数据库连接失败
**检查清单**:
- Docker Compose 是否所有服务都 healthy: `docker compose ps`
- `.env`文件中的数据库 host 是否为 Docker 服务名（如 `mysql`, `postgres` 而非 `localhost`）
- 数据库用户是否有足够的权限

### Milvus连接失败
**检查清单**:
- Docker Compose: `docker compose ps milvus` 确认状态为 healthy
- Milvus 依赖的 etcd/minio 是否正常: `docker compose ps etcd minio`
- 查看 Milvus 日志: `docker compose logs milvus`

### Neo4j 连接失败
**检查清单**:
- `.env` 中 `NEO4J_AUTH` 格式是否为 `username/password`
- `NEO4J_URI` 是否为 `bolt://neo4j:7687`
- `LIGHTRAG_GRAPH_STORAGE` 是否设置为 `Neo4JStorage`
- Neo4j 容器日志: `docker compose logs neo4j`

详细的开发指南、架构设计和最佳实践请参考各子项目的CLAUDE.md文档。
