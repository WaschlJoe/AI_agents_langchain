"""LLM-Factory – der EINZIGE Ort im Code, der Provider kennt.

Pattern-Kombination:
- Factory   : baut anhand der Config das passende Chat-Modell
- Strategy  : alle Modelle implementieren `BaseChatModel` → überall austauschbar
              (diese Schnittstelle liefert LangChain bereits – wir nutzen sie aus)
- Adapter   : langchain-openai / langchain-anthropic adaptieren die jeweilige
              Provider-API an dieselbe gemeinsame Schnittstelle

DI: Workflows rufen diese Factory NICHT selbst auf, sondern bekommen das
    fertige Modell als Parameter übergeben (→ testbar mit Mocks).
"""

from __future__ import annotations

from typing import Optional

from langchain_core.language_models.chat_models import BaseChatModel

from core.config import Provider, Settings, get_settings


def get_llm(settings: Optional[Settings] = None) -> BaseChatModel:
    """Baut das konfigurierte Chat-Modell.

    Args:
        settings: optional injizierte Config (Default: aus .env / Umgebung).
    """
    settings = settings or get_settings()

    if settings.provider is Provider.ANTHROPIC:
        # Lazy Import: nur nötig, wenn Claude tatsächlich konfiguriert ist
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=settings.model_name,
            api_key=settings.api_key,
            temperature=settings.temperature,
        )

    # "openai_compatible" (lokal) und "openai" (ChatGPT) sprechen beide das
    # OpenAI-Protokoll → derselbe Adapter passt für beide.
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=settings.model_name,
        base_url=settings.resolved_base_url,  # None → Package-Default
        api_key=settings.api_key or "not-needed",
        temperature=settings.temperature,
    )
