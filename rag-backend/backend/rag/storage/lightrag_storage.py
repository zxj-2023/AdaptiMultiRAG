import os
from typing import List, Dict, Any, Optional
import numpy as np
from dotenv import load_dotenv
import logging

from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.utils import setup_logger, EmbeddingFunc

# 设置日志
setup_logger("lightrag", level="INFO")
logger = logging.getLogger(__name__)


class LightRAGStorage:
    """LightRAG存储和检索类

    支持多种存储后端：
    - KV存储: PostgreSQL
    - 文档状态存储: PostgreSQL
    - 图存储: Neo4j
    - 向量存储: Milvus

    使用workspace实现数据隔离
    """

    def __init__(self, workspace: str = "default"):
        """初始化LightRAG存储

        Args:
            workspace: 工作空间名称，用于数据隔离
        """
        self.workspace = workspace

        # 加载环境变量
        load_dotenv()

        # 使用文件同级的 lightrag_storage 目录
        self.working_dir = os.path.join(os.path.dirname(__file__), "lightrag_storage")

        self.rag: Optional[LightRAG] = None

        # 确保工作目录存在
        os.makedirs(self.working_dir, exist_ok=True)

    async def _get_llm_model_func(self):
        """LLM模型函数"""
        async def llm_model_func(
            prompt,
            system_prompt=None,
            history_messages=[],
            keyword_extraction=False,
            **kwargs
        ) -> str:
            return await openai_complete_if_cache(
                model=os.getenv("LLM_DASHSCOPE_CHAT_MODEL", "qwen-plus"),
                prompt=prompt,
                system_prompt=system_prompt,
                history_messages=history_messages,
                api_key=os.getenv("LLM_DASHSCOPE_API_KEY"),
                base_url=os.getenv("LLM_DASHSCOPE_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
                **kwargs
            )
        return llm_model_func

    async def _get_embedding_func(self):
        """嵌入模型函数"""
        async def embedding_func(texts: List[str]) -> np.ndarray:
            return await openai_embed(
                texts,
                model=os.getenv("VECTOR_DASHSCOPE_EMBEDDING_MODEL", "text-embedding-v4"),
                api_key=os.getenv("VECTOR_DASHSCOPE_API_KEY"),
                base_url=os.getenv("VECTOR_DASHSCOPE_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
            )
        return embedding_func


    async def initialize(self) -> None:
        """初始化LightRAG实例"""
        if self.rag is not None:
            return

        # 获取模型函数
        llm_model_func = await self._get_llm_model_func()
        embedding_func = await self._get_embedding_func()

        # 存储配置 - 统一使用字符串方式，让LightRAG自动处理
        # 图存储配置
        # Neo4JStorage requires NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD env vars
        # These are configured in the project root .env file
        graph_storage = os.getenv("LIGHTRAG_GRAPH_STORAGE", "Neo4JStorage")

        # KV存储配置
        kv_storage = os.getenv("LIGHTRAG_KV_STORAGE", "PGKVStorage")

        # 文档状态存储配置
        doc_status_storage = os.getenv("LIGHTRAG_DOC_STATUS_STORAGE", "PGDocStatusStorage")

        # 向量存储配置
        vector_storage = os.getenv("LIGHTRAG_VECTOR_STORAGE", "MilvusVectorDBStorage")

        # 创建LightRAG实例
        self.rag = LightRAG(
            working_dir=self.working_dir,
            embedding_func=EmbeddingFunc(
                func=embedding_func,
                embedding_dim=int(os.getenv("EMBEDDING_DIM", 1024))
            ),
            llm_model_func=llm_model_func,
            workspace=self.workspace,
            graph_storage=graph_storage,
            kv_storage=kv_storage,
            doc_status_storage=doc_status_storage,
            vector_storage=vector_storage
        )

        # 初始化存储
        await self.rag.initialize_storages()
        await initialize_pipeline_status()

    async def insert_text(self, text: str) -> None:
        """插入文本到LightRAG

        Args:
            text: 要插入的文本内容
        """
        if self.rag is None:
            await self.initialize()

        await self.rag.ainsert(text)

    async def insert_texts(self, texts: List[str]) -> None:
        """批量插入文本

        Args:
            texts: 文本列表
        """
        for text in texts:
            await self.insert_text(text)

    async def query(
        self,
        query: str,
        mode: str = "hybrid",
        **kwargs
    ) -> str:
        """执行查询

        Args:
            query: 查询文本
            mode: 查询模式 ("naive", "local", "global", "hybrid")
            **kwargs: 其他查询参数

        Returns:
            查询结果
        """
        if self.rag is None:
            await self.initialize()

        return await self.rag.aquery(
            query,
            param=QueryParam(mode=mode, **kwargs)
        )

    async def finalize(self) -> None:
        """清理资源"""
        if self.rag is not None:
            await self.rag.finalize_storages()
            self.rag = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.finalize()

    async def drop_workspace(self) -> None:
        """删除当前workspace的所有数据

        通过日志输出删除结果
        """
        try:
            if self.rag is None:
                await self.initialize()

            logger.info(f"开始删除workspace '{self.workspace}' 的所有数据")

            # 定义所有需要删除的存储实例
            storages_to_drop = [
                ("full_docs", self.rag.full_docs),
                ("text_chunks", self.rag.text_chunks),
                ("full_entities", self.rag.full_entities),
                ("full_relations", self.rag.full_relations),
                ("entities_vdb", self.rag.entities_vdb),
                ("relationships_vdb", self.rag.relationships_vdb),
                ("chunks_vdb", self.rag.chunks_vdb),
                ("chunk_entity_relation_graph", self.rag.chunk_entity_relation_graph),
                ("llm_response_cache", self.rag.llm_response_cache),
                ("doc_status", self.rag.doc_status)
            ]

            # 逐个删除存储数据
            for storage_name, storage_instance in storages_to_drop:
                if storage_instance and hasattr(storage_instance, 'drop'):
                    try:
                        result = await storage_instance.drop()
                        logger.info(f"{storage_name}删除成功: {result}")
                    except Exception as e:
                        logger.error(f"{storage_name}删除失败: {str(e)}")
                else:
                    logger.warning(f"{storage_name}不存在或不支持drop操作")

            # 清理当前实例
            await self.finalize()

            logger.info(f"workspace '{self.workspace}' 的所有数据删除完成")

        except Exception as e:
            logger.error(f"删除workspace '{self.workspace}' 时出错: {str(e)}")


