"""LLM provider registry and factory."""

from __future__ import annotations

from importlib import import_module

from backend.config import settings

from .base import LLMProvider
from .types import ModelInfo, ProviderInfo

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
XIAOMI_BASE_URL = "https://api.xiaomimimo.com/v1"
OPENAI_NEXT_BASE_URL = "https://api.openai-next.com/v1"

_PROVIDER_IMPORTS: dict[str, tuple[str, str]] = {
    "openai": ("backend.llm.provider_openai", "OpenAIProvider"),
    "deepseek": ("backend.llm.provider_openai", "OpenAIProvider"),
    "anthropic": ("backend.llm.provider_anthropic", "AnthropicProvider"),
    "gemini": ("backend.llm.provider_gemini", "GeminiProvider"),
    "xiaomi": ("backend.llm.provider_openai", "OpenAIProvider"),
    "openai_next": ("backend.llm.provider_openai", "OpenAIProvider"),
}

_PROVIDER_INFO: dict[str, ProviderInfo] = {
    "openai": ProviderInfo(
        name="openai",
        display_name="OpenAI",
        models=[
            ModelInfo(
                id="gpt-5.5",
                display_name="GPT-5.5",
                supports_vision=True,
                supports_structured_output=True,
                context_window=400000,
            ),
            ModelInfo(
                id="gpt-5.4",
                display_name="GPT-5.4",
                supports_vision=True,
                supports_structured_output=True,
                context_window=400000,
            ),
        ],
    ),
    "deepseek": ProviderInfo(
        name="deepseek",
        display_name="DeepSeek",
        default_base_url=DEEPSEEK_BASE_URL,
        models=[
            ModelInfo(
                id="deepseek-v4-flash",
                display_name="DeepSeek V4 Flash",
                supports_vision=True,
                supports_structured_output=True,
                context_window=128000,
            ),
            ModelInfo(
                id="deepseek-v4-pro",
                display_name="DeepSeek V4 Pro",
                supports_vision=True,
                supports_structured_output=True,
                context_window=128000,
            ),
        ],
    ),
    "anthropic": ProviderInfo(
        name="anthropic",
        display_name="Anthropic",
        default_base_url=settings.anthropic_base_url,
        models=[
            ModelInfo(
                id="claude-opus-4.6",
                display_name="Claude Opus 4.6",
                supports_vision=True,
                supports_structured_output=True,
                context_window=200000,
            ),
            ModelInfo(
                id="claude-sonnet-4.6",
                display_name="Claude Sonnet 4.6",
                supports_vision=True,
                supports_structured_output=True,
                context_window=200000,
            ),
            ModelInfo(
                id="claude-haiku-4.6",
                display_name="Claude Haiku 4.6",
                supports_vision=True,
                supports_structured_output=True,
                context_window=200000,
            ),
        ],
    ),
    "xiaomi": ProviderInfo(
        name="xiaomi",
        display_name="Xiaomi MiMo",
        default_base_url=settings.xiaomi_base_url or XIAOMI_BASE_URL,
        models=[
            ModelInfo(
                id="mimo-v2.5-pro",
                display_name="MiMo V2.5 Pro",
                supports_vision=False,
                supports_structured_output=True,
                context_window=131072,
            ),
        ],
    ),
    "openai_next": ProviderInfo(
        name="openai_next",
        display_name="OpenAI Next (Aggregator)",
        default_base_url=settings.openai_next_base_url or OPENAI_NEXT_BASE_URL,
        # Curated premium picks across vendors. The platform exposes 600+
        # models; users can override the model field in the UI if they
        # want anything else from https://credits.openai-next.com.
        models=[
            ModelInfo(
                id="gpt-5.5",
                display_name="GPT-5.5",
                supports_vision=True,
                supports_structured_output=True,
                context_window=400000,
            ),
            ModelInfo(
                id="gpt-5.4",
                display_name="GPT-5.4",
                supports_vision=True,
                supports_structured_output=True,
                context_window=400000,
            ),
            ModelInfo(
                id="claude-opus-4-7",
                display_name="Claude Opus 4.7",
                supports_vision=True,
                supports_structured_output=True,
                context_window=200000,
            ),
            ModelInfo(
                id="claude-sonnet-4-6",
                display_name="Claude Sonnet 4.6",
                supports_vision=True,
                supports_structured_output=True,
                context_window=200000,
            ),
            ModelInfo(
                id="gemini-3-pro-preview",
                display_name="Gemini 3 Pro Preview",
                supports_vision=True,
                supports_structured_output=True,
                context_window=1048576,
            ),
            ModelInfo(
                id="deepseek-v3.2",
                display_name="DeepSeek V3.2",
                supports_vision=False,
                supports_structured_output=True,
                context_window=128000,
            ),
        ],
    ),
    "gemini": ProviderInfo(
        name="gemini",
        display_name="Google Gemini",
        models=[
            ModelInfo(
                id="gemini-3.1-pro-preview",
                display_name="Gemini 3.1 Pro Preview",
                supports_vision=True,
                supports_structured_output=True,
                context_window=1048576,
            ),
            ModelInfo(
                id="gemini-3.1-flash-preview",
                display_name="Gemini 3.1 Flash Preview",
                supports_vision=True,
                supports_structured_output=True,
                context_window=1048576,
            ),
        ],
    ),
}


def _load_provider_class(name: str) -> type[LLMProvider]:
    module_name, class_name = _PROVIDER_IMPORTS[name]
    try:
        module = import_module(module_name)
    except ModuleNotFoundError as exc:
        missing = exc.name or module_name
        raise RuntimeError(
            f"Provider '{name}' is unavailable because the optional dependency "
            f"'{missing}' is not installed."
        ) from exc
    return getattr(module, class_name)


def create_provider(
    name: str,
    api_key: str,
    *,
    base_url: str | None = None,
    deepseek_settings: dict | None = None,
    openai_settings: dict | None = None,
) -> LLMProvider:
    """Create an LLM provider instance by name."""
    if name not in _PROVIDER_IMPORTS:
        raise ValueError(f"Unknown provider '{name}'. Available: {list(_PROVIDER_IMPORTS)}")

    cls = _load_provider_class(name)
    if name in {"openai", "deepseek", "xiaomi", "openai_next"}:
        resolved_base_url = base_url
        if name == "deepseek" and not resolved_base_url:
            resolved_base_url = DEEPSEEK_BASE_URL
        if name == "xiaomi" and not resolved_base_url:
            resolved_base_url = settings.xiaomi_base_url or XIAOMI_BASE_URL
        if name == "openai_next" and not resolved_base_url:
            resolved_base_url = settings.openai_next_base_url or OPENAI_NEXT_BASE_URL
        kwargs = {
            "api_key": api_key,
            "base_url": resolved_base_url,
            "provider_name": name,
        }
        if deepseek_settings is not None:
            kwargs["deepseek_settings"] = deepseek_settings
        if openai_settings is not None:
            kwargs["openai_settings"] = openai_settings
        return cls(**kwargs)
    return cls(api_key=api_key, base_url=base_url) if base_url else cls(api_key=api_key)


def list_providers() -> list[ProviderInfo]:
    """List configured providers without importing optional SDKs."""
    return list(_PROVIDER_INFO.values())
