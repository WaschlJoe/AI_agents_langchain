# AI_agents_langchain

LangChain-Lernprojekt: **Workflows & Agents** auf einer provider-flexiblen Basis.
Primär gegen einen lokalen, OpenAI-kompatiblen Endpoint (LM Studio) – per `.env` in einer Zeile
auf ChatGPT oder Claude umschaltbar. Ziel: verstehen, wie die Bausteine zusammenarbeiten.

## Quickstart

```bash
# 1. Virtuelle Umgebung + Abhängigkeiten
python -m venv .venv && .venv\Scripts\activate        # Windows
pip install -r requirements.txt

# 2. Konfiguration anlegen und anpassen
copy .env.example .env                                # → MODEL_NAME auf dein LM-Studio-Modell setzen!

# 3. Workflow 1 ausführen (LM Studio muss laufen, Server auf Port 1235)
python -m workflows.pipeline.run                      # nutzt data/beispiel.md
```

Ergebnis: formatierter Report in der Konsole + `output/beispiel.json` (validiertes Schema).

## Projektstruktur

```
├── README.md           ← du bist hier: Einstieg, Quickstart, Onboarding
├── WORKFLOWS.md        ← Index aller 6 geplanten Workflows + Build-Plan + Status
├── CONVENTIONS.md      ← die Regeln: Struktur, Style, Platzierung, DoD, Git
├── docs/adr/           ← Architektur-Entscheidungen mit Begründung (Warum?)
├── core/               ← Schicht 1: geteilte Basis (Config + LLM-Factory) – provider-unabhängig
│   ├── config.py       ←    Settings aus .env (typsicher via pydantic-settings)
│   └── llm.py          ←    Factory: EINZIGER Ort im Code, der Provider kennt
├── workflows/pipeline/ ← Schicht 2: Workflow 1 – Dokumenten-Pipeline (fertig ✅)
├── agents/             ← Schicht 2: Agents (Phase 2: Tool-Calling Agent)
├── data/               ← Eingabedokumente (Beispiel: beispiel.md)
└── output/             ← generierte JSON-Reports (git-ignoriert)
```

**Schichten:** Abhängigkeiten nur von oben nach unten – `workflows`/`agents` dürfen von `core`
abhängen, nie umgekehrt. Details in [CONVENTIONS.md](CONVENTIONS.md).

## Dokumentation

| Dokument | Inhalt |
|---|---|
| [WORKFLOWS.md](WORKFLOWS.md) | Die 6 geplanten Workflows, Workflow-vs-Agent-Erklärung, Build-Plan |
| [CONVENTIONS.md](CONVENTIONS.md) | Projektregeln: Ordner-Template, Platzierungs-Baum, Style, Testing, DoD, Git |
| [docs/adr/README.md](docs/adr/README.md) | Architektur-Entscheidungen (Factory/DI, Funktionen vs. Klassen, IO-Trennung, Template) |
| `workflows/pipeline/README.md` | Workflow 1 im Detail: Datenfluss, Dateien, Troubleshooting |

## Workflow-Status

| # | Workflow | Typ | Status |
|---|---|---|---|
| 1 | Dokumenten-Pipeline | Workflow (Code gesteuert) | ✅ gebaut & getestet |
| 3 | Tool-Calling Agent | Agent (LLM gesteuert) | ⬜ **nächster Schritt** |
| 2 | RAG / Knowledge Base | Workflow, 2 Phasen | ⬜ optional |
| 5 | Chat + Memory | Workflow | ⬜ optional |

## Onboarding für neue Entwickler (30 Minuten)

1. Dieses README lesen → Quickstart durchlaufen (Workflow 1 läuft lokal)
2. [CONVENTIONS.md](CONVENTIONS.md) §1–§3 lesen (Struktur, Template, Platzierungs-Baum)
3. `workflows/pipeline/README.md` lesen + Code entlang des Datenflusses öffnen
4. In [WORKFLOWS.md](WORKFLOWS.md) den nächsten Workflow wählen
5. Branch nach CONVENTIONS §8 anlegen → loslegen
