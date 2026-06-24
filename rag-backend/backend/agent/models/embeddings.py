import os
from typing import Any, Optional, Union

from langchain.embeddings import Embeddings, init_embeddings

# LangChain 1.x 支持的 embeddings provider 列表（原 _EMBEDDINGS_SUPPORTED_PROVIDERS 已从公开 API 移除）
_EMBEDDINGS_EMBEDDINGS_SUPPORTED_PROVIDERS = {
    "openai", "ollama", "huggingface", "cohere", "mistralai",
    "google_vertexai", "google_genai", "bedrock", "fireworks",
    "together", "nomic", "voyageai", "jina", "deepseek",
}
from langchain_core.runnables import Runnable


# 用于存储注册的嵌入模型提供方信息
_EMBEDDINGS_PROVIDERS_DICT = {}


def _parse_model_string(model_name: str) -> tuple[str, str]:
    """解析模型字符串，提取提供方和模型名称。

    参数:
        model_name: 模型名称字符串，格式应为 '提供方:模型名'，例如 'openai:text-embedding-ada-002'

    返回:
        一个元组 (提供方, 模型名)，均为去除首尾空格后的字符串

    异常:
        ValueError: 如果格式不合法或模型名为空
    """
    if ":" not in model_name:
        msg = (
            f"模型名称格式错误 '{model_name}'。\n"
            f"必须使用格式 '提供方:模型名'，例如 'openai:text-embedding-ada-002'\n"
        )
        raise ValueError(msg)

    provider, model = model_name.split(":", 1)  # 只分割一次，防止模型名中包含冒号
    provider = provider.lower().strip()        # 提供方统一转小写并去空格
    model = model.strip()                      # 模型名去空格
    if not model:
        msg = "模型名称不能为空"
        raise ValueError(msg)
    return provider, model


def register_embeddings_provider(
    provider_name: str,
    embeddings_model: Union[type[Embeddings], str],
    base_url: Optional[str] = None,
):
    """注册一个嵌入模型提供方。

    参数:
        provider_name: 要注册的提供方名称（自定义，如 'my_openai', 'zhipu' 等）
        embeddings_model: 可以是 Embeddings 类型的类，或者字符串（如 'openai', 'ollama' 等）
        base_url: 当 embeddings_model 为字符串时，必须提供 API 的基础 URL（如本地部署的地址）

    异常:
        ValueError: 如果 embeddings_model 是字符串但未提供 base_url，或字符串不在支持列表中
    """
    if isinstance(embeddings_model, str):
        # 如果传入的是字符串（如 'openai'），必须提供 base_url
        if base_url is None:
            raise ValueError(
                "当 embeddings_model 为字符串时，必须提供 base_url 参数"
            )

        # 检查是否为 LangChain 支持的提供方
        if embeddings_model not in _EMBEDDINGS_SUPPORTED_PROVIDERS:
            raise ValueError(
                f"embeddings_model 为字符串时，仅支持以下提供方: {_EMBEDDINGS_SUPPORTED_PROVIDERS}"
            )

        # 注册到全局字典中
        _EMBEDDINGS_PROVIDERS_DICT.update(
            {
                provider_name: {
                    "embeddings_model": embeddings_model,
                    "base_url": base_url,
                }
            }
        )
    else:
        # 如果传入的是 Embeddings 类，则直接注册
        _EMBEDDINGS_PROVIDERS_DICT.update(
            {provider_name: {"embeddings_model": embeddings_model}}
        )


def load_embeddings(
    model: str,
    *,
    provider: Optional[str] = None,
    **kwargs: Any,
) -> Union[Embeddings, Runnable[Any, list[float]]]:
    """加载嵌入模型实例。

    支持两种调用方式：
      1. load_embeddings("openai:text-embedding-3-small")
      2. load_embeddings("text-embedding-3-small", provider="openai")

    参数:
        model: 模型名称。若未指定 provider，则格式必须为 'provider:model-name'
        provider: 可选，提供方名称（若 model 中已包含则可省略）
        **kwargs: 初始化模型所需的其他参数（如 api_key, dimensions 等）

    返回:
        初始化后的嵌入模型实例（Embeddings 或 Runnable）

    异常:
        ValueError: 如果提供方未注册，或未找到 API Key
    """
    # 如果未指定 provider，则从 model 字符串中解析
    if provider is None:
        provider, model = _parse_model_string(model)

    # 检查提供方是否已注册
    if provider not in _EMBEDDINGS_PROVIDERS_DICT:
        raise ValueError(f"提供方 '{provider}' 未注册，请先调用 register_embeddings_provider 注册")

    # 获取注册的模型配置
    embeddings_config = _EMBEDDINGS_PROVIDERS_DICT[provider]
    embeddings = embeddings_config["embeddings_model"]

    # 如果是字符串类型（如 'openai'），说明是 LangChain 内置支持的提供方
    if isinstance(embeddings, str):
        # 优先从 kwargs 获取 api_key，若无则从环境变量获取
        if not (api_key := kwargs.get("api_key")):
            api_key = os.getenv(f"{provider.upper()}_API_KEY")
            if not api_key:
                raise ValueError(
                    f"未找到 {provider} 的 API Key，请设置环境变量 {provider.upper()}_API_KEY"
                )
            kwargs["api_key"] = api_key

            # 对 OpenAI 特殊处理：关闭上下文长度检查（避免报错）
            if embeddings == "openai":
                kwargs["check_embedding_ctx_length"] = False

        # 使用 LangChain 初始化函数创建嵌入模型
        return init_embeddings(
            model=model,
            provider=embeddings,
            base_url=embeddings_config.get("base_url"),  # 若有自定义 base_url 则传入
            **kwargs,
        )
    else:
        # 如果是自定义 Embeddings 类，则直接实例化
        return embeddings(model=model, **kwargs)
    
'''
https://tbice123123.github.io/langchain-dev-utils-docs/zh/
# 注册自定义embedding提供商
register_embeddings_provider(
    provider_name="doubao_embeddings",
    embeddings_model="openai",
    base_url="https://ark.cn-beijing.volces.com/api/v3"
)

# 加载embedding模型（必需）
embeddings_model = load_embeddings(
    "doubao_embeddings:doubao-embedding-text-240715",
    api_key="your-api-key-here",
    tiktoken_enabled=False,                 # 关键：禁止提前 tokenize
    check_embedding_ctx_length=False       # 可选：跳过长度检查
)
'''