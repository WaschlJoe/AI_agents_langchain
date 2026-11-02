# LangChain Workflows – Ideen & Plan

> **Projekt:** AI_agents_langchain
> **Ziel:** Verstehen, wie die Bausteine von LangChain zusammenarbeiten.
> **LLM-Endpoint (lokal, OpenAI-kompatibel):** `http://localhost:1235/v1`
> **Provider-Flexibilität:** ChatGPT, Claude & Co. per Konfiguration umschaltbar (siehe unten).

---

## Grundprinzip: Workflow vs. Agent

| | **Workflow** | **Agent** |
|---|---|---|
| Wer steuert den Ablauf? | Der **Code** (fest vorgegeben) | Das **LLM** (zur Laufzeit) |
| Muster | A → B → C, immer gleich | LLM denkt → ruft Tool auf → liest Ergebnis → entscheidet weiter |

> **Faustregel:** Ein Agent ist ein Workflow, bei dem das LLM die Kontrolle über den Flow übernimmt.
> In der Praxis mischen sich beide – z.B. ein RAG-Workflow, der *innerhalb* eines Agents als Tool aufgerufen wird.

---

## Die 6 Workflows

### 1. 📄 Dokumenten-Verarbeitungs-Pipeline *(Workflow)*
**Flow:** Text/Markdown rein → in Chunks aufteilen → pro Chunk extrahieren / klassifizieren / zusammenfassen (LLM) → Ergebnisse aggregieren → strukturiertes JSON (Pydantic) + Report.

**Bausteine:** LLM, Prompt-Templates, **LCEL-Chains (`|` Operator)**, Structured Outputs.
**Warum zuerst?** Kleiner gemeinsamer Nenner – alle Kern-Bausteine sichtbar, ohne Tool-/Loop-Komplexität.

### 2. 🔍 RAG – Retrieval-Augmented Generation *(Workflow)*
**Flow:** Dokumente → Embeddings → Vector Store (z.B. Chroma lokal) → Nutzer-Frage → Top-k Retrieval → LLM antwortet **nur auf Basis der Treffer**, mit Quellenangaben.

**Bausteine:** Embedding-Modelle, Vector Stores, Retriever als eigene Komponente in einer Chain.
**Kernidee:** "LLM + eigene Daten" – der Klassiker.

### 3. 🛠️ Tool-Calling Agent *(Agent)*
**Flow:** LLM bekommt Tools (z.B. Rechner, Datei-Lesen, API) → entscheidet selbst, welches Tool wann → iteriert im Loop, bis die Antwort steht.

**Bausteine:** `Tool`-Definitionen, **Agent-Loop**, Function Calling unter der Haube.
**Kernidee:** Das LLM steuert den Flow – dynamische Seite von LangChain.

### 4. 🤖 Multi-Agent / Supervisor-Pattern *(Orchestrierung)*
**Flow:** Ein "Supervisor"-Agent triagt Anfragen und delegiert an Spezialisten (z.B. *Fakten-Checker*, *Schreiber*, *Kritiker*). Der Kritiker gibt Feedback, der Schreiber überarbeitet – bis die Qualität stimmt.

**Bausteine:** Orchestrierung mehrerer LLM-Aufrufe, Zustandsübergabe zwischen Agenten, Reflexion/Feedback-Loops.
**Kernidee:** Basis für LangGraph (State Machines).

### 5. 💬 Chat mit Gedächtnis + Zusammenfassung *(Workflow)*
**Flow:** Mehrere Nachrichten → wenn der Kontext zu lang wird: alte Messages automatisch zusammenfassen → nur Summary + letzte N Messages ans LLM.

**Bausteine:** Message-History, Token-Management, `trim_messages`, realistische Context-Fenster-Handhabung.

### 6. 📊 Daten-Analyst-Copilot *(Hybrid / Agent)*
**Flow:** CSV/SQLite lokal → LLM schreibt SQL/Python → Code wird ausgeführt (Sandbox) → Ergebnis zurück ans LLM → iteriert bei Fehlern → finale Antwort mit Tabelle + Interpretation.

**Bausteine:** Sandbox-Ausführung, Fehler-Feedback-Loops, strukturierte Ergebnisse.

---

## Baustein-Übersicht (wer braucht was?)

| Baustein | 1 Pipeline | 2 RAG | 3 Agent | 4 Multi-Agent | 5 Chat | 6 Analyst |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| LLM (Chat-Modell) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Prompt-Templates | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Structured Outputs (Pydantic) | ✅ | ✅ | – | – | – | ✅ |
| Retriever / Vector Store | – | ✅ | – | – | – | – |
| Tools + Agent-Loop | – | – | ✅ | ✅ | – | ✅ |
| Memory / History | – | – | – | – | ✅ | – |

> Alle 6 Workflows sind **verschiedene Kombinationen derselben Bausteine**.
> Wer die Bausteine einmal verstanden hat, kann jeden Workflow nachvollziehen.

---

## Build-Plan

| Phase | Inhalt | Status |
|---|---|---|
| **0** | Gemeinsame Basis: Projektstruktur, `requirements.txt`, `.env`, LLM-Factory (Provider-flexibel) | ⬜ offen |
| **1** | Workflow 1 – Dokumenten-Pipeline (deterministisch, alle Kern-Bausteine) | ⬜ offen |
| **2** | Workflow 3 – Tool-Calling Agent (dynamisch, LLM-gesteuert) | ⬜ offen |
| **3** | Optional: Workflow 2 (RAG) oder 5 (Chat + Memory), je nach Interesse | ⬜ offen |

Jeder Workflow bekommt seinen eigenen Ordner/Modul (`workflows/`, `agents/`) und teilt sich die Basis-Infrastruktur aus `core/`.

---

## Provider-Konfiguration (Vorschlag)

Alles läuft über Umgebungsvariablen (`.env`), der Rest des Codes bleibt unverändert:

```bash
# Lokal (LM Studio / OpenAI-kompatibel)
PROVIDER=openai_compatible
BASE_URL=http://localhost:1235/v1
API_KEY=not-needed-locally
MODEL_NAME=<dein-lokales-modell>

# Alternativ: ChatGPT
# PROVIDER=openai
# BASE_URL=https://api.openai.com/v1
# API_KEY=sk-...
# MODEL_NAME=gpt-4o-mini

# Alternativ: Claude (via langchain-anthropic)
# PROVIDER=anthropic
# API_KEY=sk-ant-...
# MODEL_NAME=claude-sonnet-4-20250514
```
