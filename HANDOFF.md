# HANDOFF – Kontext für die Fortsetzung (anderes Agent-Harness / anderer PC)

> **Zweck:** Dieses Dokument enthält ALLES, was zur Fortentwicklung des Projekts nötig ist:
> Projektstand, Konventionen, Architektur-Entscheidungen, das aus der Diskussion gewonnene Wissen
> und den konkreten Bauplan für Phase 2.
> **Nutzung:** Als Kontext-Datei an einen neuen Agent (z. B. Claude Desktop) anhängen + dieses
> Dokument zusammen mit dem Projektordner auf den Ziel-PC übertragen.

---

## 1. Projekt in einem Absatz

`AI_agents_langchain` ist ein **LangChain-Lernprojekt** (Python): Workflows und Agents auf einer
provider-flexiblen Basis. Primär gegen einen lokalen, OpenAI-kompatiblen Endpoint (LM Studio,
`http://localhost:1235/v1`) – per `.env` in einer Zeile auf ChatGPT/Claude umschaltbar.
Ziel ist es zu verstehen, wie die Bausteine (LLM-Abstraktion, LCEL, Structured Outputs, Tools,
Memory) zusammenarbeiten. **Workflow 1 (Dokumenten-Pipeline) ist fertig und läuft erfolgreich.**

## 2. Umgebung & Laufzeit (Standort A – woher das Projekt kommt)

| | |
|---|---|
| OS | Windows (Git Bash verfügbar), Python 3.10.11, venv im Projektordner |
| LLM-Endpoint | LM Studio: `http://localhost:1235/v1` (OpenAI-kompatibel) |
| Modell | `qwen3.8-27b-heretic-abliterated-uncensored` – tool-fähig, Structured Outputs funktionieren ✅ |
| Status Workflow 1 | Läuft: 4 Chunks analysiert, validierter Report, `output/beispiel.json` erzeugt ✅ |

**Wichtig für den Ziel-PC:** LM Studio muss dort laufen (Server auf Port 1235) und ein
tool-fähiges Modell geladen sein; `MODEL_NAME` in der `.env` muss exakt zum geladenen Modell passen.

## 3. Projektstruktur (vollständig, Stand heute)

```
AI_agents_langchain/
├── README.md               ← Einstieg: Quickstart, Struktur, Onboarding-Pfad
├── WORKFLOWS.md            ← Index der 6 geplanten Workflows + Build-Plan + Status
├── CONVENTIONS.md          ← DAS Gesetz: Template, Platzierung, Style, Testing, DoD, Git, ADRs
├── HANDOFF.md              ← dieses Dokument
├── .env.example            ← Provider-Konfiguration (PROVIDER/BASE_URL/API_KEY/MODEL_NAME/TEMPERATURE)
├── .gitignore              ← .env, output/, venv, __pycache__
├── requirements.txt        ← langchain, langchain-openai, langchain-text-splitters, pydantic-settings, rich
├── docs/adr/               ← 4 ADRs (0001–0004) + Index-README
├── core/                   ← Schicht 1: config.py (Settings aus .env), llm.py (LLM-Factory – einziger Provider-Kontakt)
├── workflows/pipeline/     ← Workflow 1 (FERTIG): README, run.py, prompts.py, schemas.py, steps.py, chain.py
├── agents/                 ← Schicht 2: (noch leer – Phase 2 kommt hierher)
├── data/beispiel.md        ← Beispieldokument (lokal LLMs; Fakten/Anleitung/Meinung/Fragen)
└── output/beispiel.json    ← generierter Report (git-ignoriert)
```

## 4. Konventionen – Kern (vollständig in `CONVENTIONS.md`)

1. **Schichten:** `core` ← `workflows`/`agents`; Abhängigkeiten nur nach unten; Provider-Details NUR in `core/`.
2. **Root-6-Template (Pflicht, ab Tag 1):** Jeder Workflow-/Agent-Ordner hat exakt:
   `README.md · run.py · prompts.py · schemas.py · steps.py (Agent: tools.py) · chain.py (Agent: agent.py)` –
   Extras (Parser, Formatter …) NUR in nach Thema benannte Unterordner (`parsing/`, `formatting/`), nie als 7. Root-Datei; `utils/` verboten.
3. **Platzierungs-Baum:** geteilt von 2+ Workflows → `core/`; sonst: Vertrag→schemas, LLM-Text→prompts, Baustein→steps/tools, Orchestrierung→chain/agent, IO→run.py.
4. **Style:** Typ-Hints überall; Module-Docstrings; Funktionen < ~70 Zeilen; Exceptions in core/steps werfen, gefangen NUR in run.py; kein print() außerhalb run.py (dort rich); LLM-Calls immer über `get_llm()`; Naming: `load_*/split_*` (deterministisch), `build_*_chain`, `run_*` (Entry), Tools im Verb.
5. **Prompts:** alle in `prompts.py`; Auslagerung nach `prompt_texts/*.md` + Loader erst bei >~50 Zeilen / Nicht-Dev-Pflege / A-B-Varianten.
6. **Testing:** jeder Workflow mit FakeLLM testbar (DI-Payoff); getestet wird die Logik UM das LLM (Splitten, Zählen, Validierung, Fehlerfälle), nicht "gutes Deutsch".
7. **Definition of Done** (CONVENTIONS §7) + **Git**: Branches `feature/<workflow>-<thema>`, Commits imperativ+Scope, Squash-Merge pro PR.

## 5. Architektur-Entscheidungen (ADRs in `docs/adr/`)

| # | Entscheidung | Kern |
|---|---|---|
| 0001 | LLM-Factory & Provider-Abschaltung | Factory (`get_llm()`) + Strategy (BaseChatModel-Schnittstelle) + DI (llm wird übergeben, nie gebaut) + Adapter (langchain-openai/-anthropic); Provider-Wechsel = `.env` ändern |
| 0002 | Funktionen vor Klassen für Orchestrierung | stateless Single-Shot → Funktionen; **Umstiegs-Trigger:** Zustand lebt länger als ein Aufruf (Batch, Retry-Zähler, Cache) → dünne Pipeline-Klasse |
| 0003 | IO nur in `run.py` | Workflow produziert Daten (`PipelineReport`), Einstiegspunkt entscheidet über Konsole/Dateien; testbar + wiederverwendbar (z. B. API-Server) |
| 0004 | Root-6-Template | fixe 6 Dateien in jedem Workflow-Ordner ab Tag 1; Extras in benannte Unterordner → maximale Vorhersagbarkeit im Team |

**ADR-Prozess:** append-only Protokoll; altes ADR wird NIE umgeschrieben, nur Status-Zeile
markiert (`superseded by NNNN` + Link); neues ADR ersetzt es; Index in `docs/adr/README.md`.
Confluence-Struktur (besprochen): Projekt-Home dünn → Guidelines 1 Seite (lebend) → ADRs je eigene Subpage unter Index; **Repo bleibt kanonisch**, Confluence = gepflegter Spiegel.

## 6. Wichtige Konzepte aus der Diskussion (Wissen, das über die Dateien hinausgeht)

- **Workflow vs. Agent:** Workflow = Code steuert den Flow (A→B→C fest); Agent = LLM entscheidet zur Laufzeit (Tool-Loop). Faustregel: *Ein Agent ist ein Workflow, bei dem das LLM die Kontrolle übernimmt.*
- **Structured Outputs – wie der "Zwang" wirklich funktioniert:** (a) Pydantic-Schema wird als Tool-Definition/JSON-Schema an das Modell übergeben (Enum = erlaubte Werte), (b) Modell antwortet als strukturierter Call statt Freitext, (c) **harte Grenze bei uns**: Validierung via `model_validate` – ungültig = ValidationError. Schema=Vertrag, Training=Compliance, Validierung=Durchsetzung.
- **Pattern-Mapping:** Factory=`core/llm.py`; Strategy=BaseChatModel-Schnittstelle (von LangChain geliefert); DI=Parameter-Injection des LLMs; Adapter=langchain-openai/-anthropic-Pakete. Wir schreiben Factory+DI selbst, Strategy+Adapter kommen mit LangChain.
- **Funktionen vs. Klassen:** Entscheidungskriterium = *Habe ich Zustand, der länger lebt als ein Aufruf?* Ja→Klasse, Nein→Funktion. LangGraph löst die Spannung so: State=Objekt, Nodes=Funktionen.
- **Datenfluss Workflow 1 (gelernt):** laden(Code) → splitten(Code) → LLM pro Chunk(Structured) → Gesamt-Summary(LLM Freitext) → Aggregation(Code). 5 LLM-Calls + deterministischer Code drumherum. Zählen/Aggregieren = immer Code, nie LLM.
- **Skalierung:** lineare Pipeline → Funktionen+Orchestrierer; Verzweigung/Loops/Retry/Human-in-the-loop → LangGraph (State Machine); Produktion → with_retry/with_fallbacks, Tracing, Tests mit FakeLLM.

## 7. Phase 2 – Tool-Calling Agent: konkreter Bauplan

**Ziel:** LLM-gesteuerter Research-Agent auf derselben `core/`-Basis (null Änderungen dort).

```
agents/tool_agent/
├── README.md      ← Zweck + Datenfluss (Agent-Loop als Diagramm!) + Aufruf
├── run.py         ← Wiring (get_settings/get_llm) + Rich-Ausgabe inkl. Tool-Call-Nachverfolgung
├── prompts.py     ← System-Prompt des Agents (Rolle, Vorgehen, Antwortformat)
├── schemas.py     ← AgentReport: frage, antwort, verwendete_tools: list[str], quellen: list[str]
├── tools.py       ← die Tools als Funktionen mit präzisen Docstrings (= Tool-Beschreibung fürs LLM):
│                    z. B. search_knowledge_base(query) → durchsucht data/*.md (RAG-light, deterministisch!)
│                          calculate(expression)        → sichere Auswertung
│                          read_document(path)           ← Datei aus data/ lesen
└── agent.py       ← create_agent(llm, tools=[...]) aus langchain.agents (langchain ≥ 1.0);
                     öffentliche Entry-Funktion run_research(llm, question) → AgentReport
```

**Umsetzungs-Punkte:**
1. `create_agent` ist die LangChain-1.x-API (ersetzt AgentExecutor) – Loop (LLM denkt → Tool → Ergebnis → weiter) läuft im Modell.
2. Tools sind **deterministische Funktionen** (unser steps.py-Muster!) – sie lassen sich OHNE LLM unit-testen.
3. `AgentReport` via Structured Output für die finale Antwort; Tool-Nutzung aus dem Message-Verlauf extrahieren.
4. FakeLLM-Test: mindestens die Tools + Report-Zusammenstellung (CONVENTIONS §6/§7).
5. DoD aus CONVENTIONS §7 abhaken; README mit Agent-Loop-Sequenzdiagramm.

## 8. Start-Checkliste für den neuen Agent / auf dem Ziel-PC

```
□ Projektordner + HANDOFF.md entpacken (Zip enthält alles außer venv/__pycache__/output)
□ python -m venv .venv && activate; pip install -r requirements.txt
□ copy .env.example .env  →  MODEL_NAME = exakter Name des in LM Studio geladenen Modells!
□ Smoke-Test: python -m workflows.pipeline.run   (muss laufen, bevor Phase 2 startet)
□ CONVENTIONS.md + docs/adr/README.md lesen
□ Phase 2 gemäß §7 umsetzen (Branch: feature/workflow3-tool-agent)
```

## 9. Offene Punkte / Diskussionsstand (Stand: so beschlossen, bei Bedarf revidieren via ADR)

- Root-6 strikt ab Tag 1 (auch kleine Dateien) – **entschieden** (ADR 0004)
- 70-Zeilen-Funktionsgrenze als Faustzahl – **angenommen**, bei Bedarf im Team kalibrieren
- FakeLLM-Testpflicht in der DoD – **entschieden** (CONVENTIONS §6/§7)
- Unterordner-Namen: semantisch frei, `utils/` verboten – **entschieden**
- Git/Squash: aktuell lokal ohne Remote – Regeln stehen, greifen ab dem ersten Remote
