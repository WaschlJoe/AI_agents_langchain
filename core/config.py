"""Konfiguration für das gesamte Projekt (Schicht 1).

Lädt Einstellungen aus Umgebungsvariablen / `.env` – typsicher via pydantic-settings.
Dies ist der EINZIGE Ort, an dem provider-spezifische Werte vorkommen.
"""

from __future__ import annotations

from enum import Enum
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Provider(str, Enum):
    """Die unterstützten LLM-Provider."""

    OPENAI_COMPATIBLE = "openai_compatible"  # lokaler Endpoint (LM Studio, Ollama, vLLM …)
    OPENAI = "openai"                        # ChatGPT API
    ANTHROPIC = "anthropic"                  # Claude API


class Settings(BaseSettings):
    """Typsichere Einstellungen aus `.env` / Umgebungsvariablen.

    Feldnamen werden case-insensitiv mit den Env-Variablen gemappt:
    `base_url` ← `BASE_URL`, `model_name` ← `MODEL_NAME` usw.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # unbekannte Variablen in der .env ignorieren statt Fehler
    )

    provider: Provider = Provider.OPENAI_COMPATIBLE
    base_url: str | None = None          # z. B. http://localhost:1235/v1
    api_key: str = "not-needed"          # lokale Endpoints ignorieren den Key meist
    model_name: str = "local-model"      # muss zum geladenen Modell (LM Studio) passen!
    temperature: float = 0.2

    @property
    def resolved_base_url(self) -> str | None:
        """base_url mit sinnvollem Default je nach Provider."""
        if self.base_url:
            return self.base_url
        if self.provider is Provider.OPENAI:
            return "https://api.openai.com/v1"
        return None  # lokaler Endpoint ohne BASE_URL → Fehler früh sichtbar


@lru_cache
def get_settings() -> Settings:
    """Settings-Instanz (pro Prozess genau einmal gebaut, danach gecacht)."""
    return Settings()
