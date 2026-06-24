#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG Backend 主入口

Docker 部署: docker compose up -d
本地开发: python main.py
"""

import sys
from pathlib import Path
from dotenv import load_dotenv


# ===== 第一步：加载环境变量（必须在所有其他 import 之前）=====
def _load_environment():
    """从多个候选路径加载 .env 文件（优先级递减）"""
    base = Path(__file__).resolve().parent
    candidate_paths = [
        base / ".env",                  # 仓库根目录 (AdaptiMultiRAG/.env) — Docker 部署
        base.parent / ".env",           # rag-backend/.env
        base / "backend" / ".env",      # rag-backend/backend/.env (兼容旧目录)
    ]
    for env_path in candidate_paths:
        if env_path.is_file():
            load_dotenv(env_path, override=False)
            print(f"[main] .env 已从 {env_path} 加载")
            return
    print("[main] 未找到 .env 文件，将使用容器注入的环境变量")


_load_environment()

# ===== 第二步：现在安全导入依赖环境变量的模块 =====
from backend.config.log import setup_default_logging, get_logger
from fastapi import FastAPI
from backend.api import rag, chat, auth, crawl, knowledge_library, visual_graph
import uvicorn
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 生命周期管理"""
    # --- 启动 ---
    setup_default_logging()
    logger = get_logger(__name__)
    logger.info("AdaptiMultiRAG FastAPI 应用启动中...")

    # MySQL 表结构初始化（幂等操作：如已存在则跳过）
    # 替代原来的 init_db.py
    try:
        from backend.config.database import DatabaseFactory
        engine = DatabaseFactory.get_engine()
        Base = DatabaseFactory.get_base()
        logger.info("正在初始化 MySQL 数据库表结构...")
        Base.metadata.create_all(engine)
        logger.info("MySQL 数据库表结构初始化完成")
    except Exception as e:
        logger.error(f"MySQL 数据库初始化失败（服务将继续启动）: {e}")

    # Redis 预热检查（非致命）
    try:
        from backend.config.redis import RedisClientFactory
        redis_client = await RedisClientFactory.get_instance()
        await redis_client.ping()
        logger.info("Redis 连接正常")
    except Exception as e:
        logger.warning(f"Redis 连接预热失败（非致命）: {e}")

    yield

    # --- 关闭 ---
    logger.info("FastAPI 应用关闭中...")
    try:
        from backend.config.redis import RedisClientFactory
        await RedisClientFactory.close_instance()
    except Exception:
        pass


app = FastAPI(title="AdaptiMultiRAG API", version="1.0.0", lifespan=lifespan)

app.include_router(rag.router)
app.include_router(chat.router)
app.include_router(auth.router)
app.include_router(crawl.router)
app.include_router(knowledge_library.router)
app.include_router(visual_graph.router)


@app.get("/health")
async def health():
    """健康检查：返回各依赖服务的连通性状态"""
    import os
    checks = {}
    overall = "healthy"

    # 检查 MySQL
    try:
        from backend.config.database import DatabaseFactory
        from sqlalchemy import text
        engine = DatabaseFactory.get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["mysql"] = "ok"
    except Exception as e:
        checks["mysql"] = f"error: {type(e).__name__}"
        overall = "degraded"

    # 检查 Redis
    try:
        from backend.config.redis import RedisClientFactory
        redis_client = await RedisClientFactory.get_instance()
        if await redis_client.ping():
            checks["redis"] = "ok"
        else:
            checks["redis"] = "error: ping failed"
            overall = "degraded"
    except Exception as e:
        checks["redis"] = f"error: {type(e).__name__}"
        overall = "degraded"

    # 检查 Milvus
    try:
        from pymilvus import MilvusClient
        uri = os.getenv("MILVUS_URI", "http://milvus:19530")
        client = MilvusClient(uri=uri, timeout=5)
        client.list_collections()
        checks["milvus"] = "ok"
        client.close()
    except Exception as e:
        checks["milvus"] = f"error: {type(e).__name__}"
        overall = "degraded"

    return {"status": overall, "checks": checks}


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
