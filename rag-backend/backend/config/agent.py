#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAGGraph 动态创建和管理
基于 collection_id 动态创建 RAGGraph 实例
"""

import os
from typing import Optional
from dotenv import load_dotenv

from backend.agent.graph import RAGGraph
from backend.config.log import setup_default_logging, get_logger
from backend.config.models import initialize_models

# 初始化日志
logger = get_logger(__name__)


def create_rag_graph(collection_id: str) -> RAGGraph:
    """
    基于 collection_id 动态创建 RAGGraph 实例
    
    Args:
        collection_id: 知识库集合ID
        
    Returns:
        RAGGraph: 新创建的 RAGGraph 实例
        
    Raises:
        RuntimeError: 如果初始化失败
    """
    try:
        logger.info(f"为 collection_id={collection_id} 创建 RAGGraph 实例...")
        
        # 初始化所有模型
        chat_model, embeddings_model = initialize_models()
        
        # 创建 RAGGraph 实例
        rag_graph = RAGGraph(
            llm=chat_model,
            embedding_model=embeddings_model,
            enable_checkpointer=os.getenv("LANGGRAPH_ENABLE_CHECKPOINT", "true").lower() in ("true", "1", "yes"),
            workspace=collection_id  # 使用collection_id作为workspace
        )
        
        logger.info(f"RAGGraph 实例创建成功，collection_id={collection_id}")
        return rag_graph
        
    except Exception as e:
        logger.error(f"RAGGraph 创建失败，collection_id={collection_id}: {str(e)}")
        logger.exception("详细错误信息:")
        raise RuntimeError(f"RAGGraph 创建失败: {str(e)}")


def get_rag_graph_for_collection(collection_id: str) -> RAGGraph:
    """
    为指定的 collection_id 获取 RAGGraph 实例
    每次调用都会创建新的实例
    
    Args:
        collection_id: 知识库集合ID
        
    Returns:
        RAGGraph: RAGGraph 实例
    """
    return create_rag_graph(collection_id)