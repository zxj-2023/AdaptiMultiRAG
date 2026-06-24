import os
from typing import Any, Optional, Union, cast

from langchain.chat_models.base import (
    BaseChatModel,
    init_chat_model,
)

# LangChain 1.x 支持的 model_provider 列表（原 _SUPPORTED_PROVIDERS 已从公开 API 移除）
_SUPPORTED_PROVIDERS = {
    "openai", "anthropic", "azure_openai", "azure_ai",
    "google_vertexai", "google_genai", "anthropic_bedrock", "bedrock",
    "bedrock_converse", "cohere", "fireworks", "together", "mistralai",
    "huggingface", "groq", "ollama", "google_anthropic_vertex",
    "deepseek", "ibm", "nvidia", "xai", "openrouter", "perplexity",
    "upstage", "baseten",
}


# 存储自定义注册的模型提供方配置
_MODEL_PROVIDERS_DICT = {}


def _parse_model(model: str, model_provider: Optional[str]) -> tuple[str, str]:
    """解析模型名称和提供方名称。

    支持格式：
      - 直接传入 model="gpt-4"，并指定 model_provider="openai"
      - 或传入 model="openai:gpt-4"，自动解析 provider

    参数:
        model: 模型名称字符串，可能包含提供方前缀（如 "openai:gpt-4"）
        model_provider: 可选，显式指定的提供方名称

    返回:
        (模型名, 提供方名) 的元组，提供方名统一转为小写并替换 '-' 为 '_'

    异常:
        ValueError: 无法推断提供方时抛出
    """
    # 合并支持的提供方列表：自定义注册的 + LangChain 内置支持的
    support_providers = list(_MODEL_PROVIDERS_DICT.keys()) + list(_SUPPORTED_PROVIDERS)

    # 如果未指定 provider，但 model 中包含冒号，且冒号前是合法 provider，则自动解析
    if not model_provider and ":" in model and model.split(":")[0] in support_providers:
        model_provider = model.split(":")[0]
        model = ":".join(model.split(":")[1:])  # 剩余部分作为模型名

    # 如果仍无 provider，则报错
    if not model_provider:
        msg = (
            f"无法推断模型 {model} 的提供方，请显式指定 model_provider 参数。\n"
            f"支持的提供方有: {support_providers}"
        )
        raise ValueError(msg)

    # 标准化 provider 名称：转小写，替换 '-' 为 '_'
    model_provider = model_provider.replace("-", "_").lower()
    return model, model_provider


def _load_chat_model_helper(
    model: str,
    model_provider: Optional[str] = None,
    **kwargs: Any,
) -> BaseChatModel:
    """加载聊天模型的辅助函数（实际执行逻辑）。

    参数:
        model: 模型名称
        model_provider: 可选，提供方名称
        **kwargs: 初始化模型所需的其他参数（如 api_key, temperature 等）

    返回:
        初始化后的 BaseChatModel 实例
    """
    # 解析模型和提供方
    model, model_provider = _parse_model(model, model_provider)

    # 优先检查是否为自定义注册的提供方
    if model_provider in _MODEL_PROVIDERS_DICT:
        config = _MODEL_PROVIDERS_DICT[model_provider]
        chat_model = config["chat_model"]

        # 如果是字符串类型（如 'openai', 'anthropic'），说明是 LangChain 支持的内置类型
        if isinstance(chat_model, str):
            # 优先从 kwargs 获取 api_key，若无则从环境变量获取
            if not (api_key := kwargs.get("api_key")):
                api_key = os.getenv(f"{model_provider.upper()}_API_KEY")
                if not api_key:
                    raise ValueError(
                        f"未找到 {model_provider} 的 API Key，请设置环境变量 {model_provider.upper()}_API_KEY"
                    )
                kwargs["api_key"] = api_key

            base_url = config["base_url"]

            # 对 OpenAI / Anthropic 使用标准 base_url 参数
            if chat_model in ["openai", "anthropic"]:
                return init_chat_model(
                    model=model,
                    model_provider=chat_model,
                    base_url=base_url,
                    **kwargs,
                )
            else:
                # 其他模型使用 api_base（如 Ollama, LocalAI 等）
                return init_chat_model(
                    model=model,
                    model_provider=chat_model,
                    api_base=base_url,
                    **kwargs,
                )

        else:
            # 如果是自定义 BaseChatModel 类，则直接实例化
            return chat_model(model=model, **kwargs)

    # 如果不是自定义注册的，交给 LangChain 原生加载逻辑
    return init_chat_model(model, model_provider=model_provider, **kwargs)


def register_model_provider(
    provider_name: str,
    chat_model: Union[type[BaseChatModel], str],
    base_url: Optional[str] = None,
):
    """注册一个新的聊天模型提供方。

    用途：
      - 注册私有部署模型（如本地 Ollama、FastChat、LocalAI）
      - 注册不同区域/账号的 OpenAI/Azure/Anthropic 实例

    参数:
        provider_name: 自定义提供方名称（如 "my_ollama", "company_openai"）
        chat_model: 可以是 BaseChatModel 的子类，或 LangChain 支持的字符串标识（如 "openai"）
        base_url: 当 chat_model 为字符串时，必须提供 API 基础地址（如 "http://localhost:11434"）

    异常:
        ValueError: chat_model 为字符串但未提供 base_url，或字符串不在支持列表中
    """
    if isinstance(chat_model, str):
        # 字符串类型必须提供 base_url
        if base_url is None:
            raise ValueError("当 chat_model 为字符串时，必须提供 base_url 参数")

        # 检查是否为 LangChain 支持的提供方
        if chat_model not in _SUPPORTED_PROVIDERS:
            raise ValueError(
                f"chat_model 为字符串时，仅支持以下提供方: {_SUPPORTED_PROVIDERS}"
            )

        # 注册配置
        _MODEL_PROVIDERS_DICT.update(
            {provider_name: {"chat_model": chat_model, "base_url": base_url}}
        )
    else:
        # 如果是自定义类，直接注册
        _MODEL_PROVIDERS_DICT.update({provider_name: {"chat_model": chat_model}})


def load_chat_model(
    model: str,
    *,
    model_provider: Optional[str] = None,
    **kwargs: Any,
) -> BaseChatModel:
    """加载聊天模型实例（对外统一接口）。

    支持两种调用方式：
      1. load_chat_model("openai:gpt-4o")
      2. load_chat_model("gpt-4o", model_provider="openai")

    参数:
        model: 模型名称，可包含提供方前缀
        model_provider: 可选，显式指定提供方
        **kwargs: 初始化参数（如 api_key, temperature, max_tokens 等）

    返回:
        初始化后的聊天模型实例（BaseChatModel）
    """
    # cast 是类型提示，确保传入的是 str（避免 mypy 报错）
    return _load_chat_model_helper(
        cast(str, model),
        model_provider=model_provider,
        **kwargs,
    )