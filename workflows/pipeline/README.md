# Workflow 1 – Dokumenten-Verarbeitungs-Pipeline

**Typ:** Workflow (Code gesteuert, deterministischer Ablauf)
**Zweck:** Ein Text/Markdown-Dokument wird in Abschnitte zerlegt; das LLM analysiert jeden Abschnitt (Zusammenfassung + Klassifikation + Kernaussagen) und liefert am Ende einen validierten Report als JSON.

## Architektur & Datenfluss

```
data/beispiel.md
      │
      ▼
┌──────────────┐   ┌───────────────┐   ┌────────────────────────┐   ┌──────────────────┐   ┌───────────────┐
│ 1. laden     │ → │ 2. splitten   │ → │ 3. LLM pro Chunk       │ → │ 4. Gesamt-       │ → │ 5. Report     │
│ load_        │   │ split_into_   │   │ build_chunk_analysis_  │   │ Zusammenfassung  │   │ PipelineReport │
│ document()   │   │ chunks()      │   │ chain(llm)             │   │ build_overall_   │   │ (Pydantic)     │
│ [Code]       │   │ [Code]        │   │ prompt | structured_llm│   │ summary_chain    │   │ + JSON-Datei   │
└──────────────┘   └───────────────┘   │ [LCEL + Structured Out]│   │ [LCEL, Freitext] │   └───────────────┘
                                       └────────────────────────┘   └──────────────────┘
```

**Prinzip:** Deterministische Schritte (laden, splitten, aggregieren) sind reiner Python-Code.
Die linearen LLM-Aufrufe sind **LCEL-Chains** (`prompt | model`). Der Loop über die Chunks ist bewusster Code – so bleibt jeder Teil einzeln testbar und nachvollziehbar.

## Dateien & Zuständigkeiten

| Datei | Verantwortung |
|---|---|
| `schemas.py` | Pydantic-Modelle: `ChunkAnalysis` (LLM-Output pro Chunk), `PipelineReport` (Endergebnis) – die "Verträge" der Pipeline |
| `prompts.py` | Prompt-Templates, strikt getrennt von Logik |
| `steps.py` | Die einzelnen Schritte als kleine Funktionen + Chain-Bausteine (`build_*_chain`) |
| `chain.py` | Orchestrierung: führt die Schritte in der richtigen Reihenfolge aus → `run_pipeline(llm, path)` |
| `run.py` | CLI-Einstiegspunkt: Config laden, LLM bauen (DI), Pipeline starten, Report ausgeben + JSON speichern |

## Design-Patterns – wo sie konkret sitzen

| Pattern | Ort |
|---|---|
| **Factory** | `core/llm.py → get_llm()` baut anhand der Config das passende Chat-Modell |
| **Strategy** | Alle Modelle implementieren `BaseChatModel` (Schnittstelle von LangChain) → austauschbar; `run_pipeline(llm, …)` hängt nur davon ab |
| **DI** | `llm` wird in `run_pipeline()` / `build_*_chain()` als Parameter übergeben, nie intern gebaut → testbar mit Mocks |
| **Adapter** | `langchain-openai` adaptiert jede OpenAI-kompatible API (lokal + ChatGPT); `langchain-anthropic` Claude – beide an dieselbe Schnittstelle |

## So startest du

```bash
# 1. Abhängigkeiten installieren (einmalig)
pip install -r requirements.txt

# 2. Konfiguration anpassen
copy .env.example .env        # Windows
# → MODEL_NAME auf dein in LM Studio geladenes Modell setzen!

# 3. Pipeline ausführen (LM Studio muss laufen, Server auf Port 1235)
python -m workflows.pipeline.run                    # nutzt data/beispiel.md
python -m workflows.pipeline.run pfad\zu\datei.md   # eigene Datei
```

**Ergebnis:** Formatierter Report in der Konsole + `output/<name>.json` mit dem strukturierten Ergebnis.

## Troubleshooting

| Symptom | Ursache / Lösung |
|---|---|
| `Connection error` auf localhost:1235 | LM Studio läuft nicht oder Server-Tab ist aus → in LM Studio unter "Developer" starten |
| `model not found` (404) | `MODEL_NAME` in `.env` passt nicht zum geladenen Modell (exakter Name aus "My Models") |
| Structured Output schlägt fehl / leere Felder | Das geladene Modell unterstützt kein Tool-Calling → ein tool-fähiges Modell laden (z. B. gpt-oss, Qwen3) |
