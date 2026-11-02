# ADR 0001: LLM-Factory & Provider-Abschaltung

**Status:** accepted (2026-10-30)

## Kontext

Wir nutzen primär einen lokalen, OpenAI-kompatiblen Endpoint (`http://localhost:1235/v1`, LM Studio),
müssen aber jederzeit auf ChatGPT oder Claude umschaltbar bleiben – ohne Workflows anzufassen.
Zugleich sollen Workflows mit Mock-Modellen testbar sein (keine API-Calls in Tests).

## Entscheidung

- `core/llm.py` stellt **eine** Factory bereit: `get_llm(settings) -> BaseChatModel`.
  Sie ist der **einzige Ort im Code, der Provider kennt** (Factory-Pattern).
- Alle Workflows hängen nur von der gemeinsamen Schnittstelle `BaseChatModel` ab –
  die Strategy liefert LangChain bereits (alle Chat-Modelle implementieren dieselbe API).
- Die Adapter (`langchain-openai`, `langchain-anthropic`) werden von den jeweiligen
  Paketen gestellt; die Factory wählt nur aus.
- **Dependency Injection:** Workflows bauen das LLM nie selbst, sondern bekommen es als
  Parameter übergeben (`run_pipeline(llm=…, …)`).
- Provider-Konfiguration (PROVIDER, BASE_URL, API_KEY, MODEL_NAME) lebt ausschließlich in `.env`
  und wird typsicher via `pydantic-settings` geladen (`core/config.py`).

## Konsequenzen

- **Positiv:** Provider-Wechsel = eine Zeile in `.env`, null Code-Änderungen. Workflows sind mit
  einem FakeLLM testbar. `langchain-anthropic` bleibt optional (lazy import).
- **Negativ/Akzeptiert:** Jede neue Provider-Familie braucht einen Eintrag in Factory + Config
  (bewusst zentral statt verstreut).
