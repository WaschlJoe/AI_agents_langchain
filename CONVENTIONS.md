# CONVENTIONS – Projektregeln für AI_agents_langchain

> Dieses Dokument ist das **Gesetz** des Projekts: Es definiert Struktur, Style und Platzierungs-Regeln,
> damit alle Entwickler konsistenten, reviewbaren Code liefern – auch wenn sie parallel an verschiedenen
> Workflows arbeiten.
>
> **Meta-Regel:** Eine Frage nach "Wie machen wir das hier?" die dieses Dokument nicht beantwortet →
> im PR besprechen und die Antwort HIER (oder als ADR) ergänzen. Kopf-Wissen ist kein Wissen.

---

## 1. Projektstruktur & Schichten

```
AI_agents_langchain/
├── README.md           ← Projekt-Einstieg: Quickstart, Struktur, Onboarding
├── WORKFLOWS.md        ← Index aller Workflows + Build-Plan + Status
├── CONVENTIONS.md      ← dieses Dokument (die Regeln)
├── docs/adr/           ← Architecture Decision Records (Entscheidungen + Warum)
├── core/               ← Schicht 1: geteilte Komponenten (1 Datei = 1 Komponente)
│   ├── config.py       ←    Settings aus .env (pydantic-settings)
│   └── llm.py          ←    LLM-Factory – EINZIGER Ort, der Provider kennt
├── workflows/<name>/   ← Schicht 2: deterministische Workflows (Code steuert den Flow)
├── agents/<name>/      ← Schicht 2: Agents (LLM steuert den Flow via Tools)
├── data/               ← Eingabedaten / Beispieldokumente
└── output/             ← generierte Ergebnisse (git-ignoriert)
```

**Schichten-Diagramm:**

```
┌────────────────────────────────────────────┐
│ Schicht 2: workflows/ + agents/            │  Use-Cases – dürfen von core abhängen
├────────────────────────────────────────────┤
│ Schicht 1: core/                           │  geteilte Basis – weiß NICHTS über Workflows
└────────────────────────────────────────────┘

Regel: Abhängigkeiten nur von oben nach unten. Nie umgekehrt.
```

**Harte Regeln:**
- Provider-Details (Base-URLs, API-Spezifika) **nie** außerhalb von `core/llm.py` + `core/config.py`.
- Neue geteilte Komponenten (Embeddings, Vector Store, Memory, …) → `core/<name>.py`, eine Datei = eine Komponente.
- Ein Workflow darf nicht aus einem anderen Workflow importieren – Geteiltes gehört nach `core/`.

---

## 2. Workflow-/Agent-Ordner: das Template (PFLICHT!)

Jeder Workflow und jeder Agent hat **ab Tag 1 exakt diese Root-Struktur** – keine Ausnahmen,
keine siebte Datei in der Root:

| Datei | Pflicht | Verantwortung ("Datei-Vertrag") |
|---|:---:|---|
| `README.md` | ✅ | Zweck, Datenfluss-Diagramm (ASCII), Aufruf, Status – **immer zuerst lesen** |
| `run.py` | ✅ | Einstiegspunkt: Parameter parsen · Wiring (Config + LLM) · IO (Rich, Dateien). **Keine Logik.** |
| `prompts.py` | ✅ | **Aller** Prompt-Text an einem Ort. Inhalt, keine Logik. |
| `schemas.py` | ✅ | Datenverträge als Pydantic-Modelle (Input/Output des Workflows + LLM-Outputs). Keine Logik. |
| `steps.py` | ✅ | Wiederverwendbare Bausteine: deterministische Funktionen + `build_*_chain(llm)`-Bausteine. *(Agent-Variante: `tools.py` – Funktionen mit Docstrings = Tool-Beschreibungen für das LLM)* |
| `chain.py` | ✅ | Orchestrierung: Reihenfolge der Schritte + **eine** öffentliche Entry-Funktion `run_<name>(llm, input) → Report`. *(Agent-Variante: `agent.py` mit `create_agent(...)`)* |

### Regel für Extras (Parser, Formatter, …)

1. Alles über die 6 Root-Dateien hinaus wandert in einen **nach Thema benannten Unterordner**:
   ```
   workflows/<name>/
   ├── (die 6 Pflicht-Dateien)
   ├── parsing/        ← z. B. parser.py, normalizer.py
   └── formatting/     ← z. B. report_builder.py
   ```
2. **Nie** als zusätzliche Datei in die Root – die Root bleibt in jedem Workflow identisch.
3. Ein Unterordner, der selbst wächst, folgt demselben Muster (eigene kurze README + Module).
4. Ordnername = Thema (semantisch), nicht generisch (`utils/` ist verboten – sagt nichts!).

**Warum so streng?** Zwei Entwickler, die parallel an Workflow 2 und 3 arbeiten, öffnen
`steps.py` und *wissen*, was drinsteht – ohne zu fragen. Das ist Review- und Übergabe-Fähigkeit.

---

## 3. Platzierungs-Baum: Wohin mit neuem Code?

```
NEUER CODE → wohin?
│
├── Von 2+ Workflows gebraucht? ──────────────► core/<komponente>.py   (1 Datei = 1 Komponente)
│
└── Nur für diesen Workflow?
    ├── Datenvertrag (was rein/raus kommt)?    → schemas.py
    ├── Text für das LLM?                      → prompts.py
    ├── Wiederverwendbarer Schritt / Tool?     → steps.py / tools.py
    ├── Reihenfolge / Orchestrierung?          → chain.py / agent.py
    └── CLI, Konsole, Dateien?                 → run.py

Keine Kategorie passt?
    → Wahrscheinlich ein neuer core-Komponente oder ein neuer Unterordner (§2)
      → im PR besprechen, ggf. ADR schreiben (siehe §10).
```

---

## 4. Code-Style

| Regel | Detail |
|---|---|
| **Typ-Hints überall** | Jede Funktion mit Signatur + Rückgabetyp; `from __future__ import annotations` in jeder Datei |
| **Module-Docstring** | Jede `.py` beginnt mit 2–4 Zeilen: *was gehört hier rein, was nicht* (Karte vor Territorium) |
| **Docstrings** | Öffentliche Funktionen: 1-Zeilen-Summary + Args/Returns bei Parametern |
| **Funktionslänge** | < ~70 Zeilen; darüber → splitten (Trigger, kein Gesetz – aber im PR erklären) |
| **Fehlerbehandlung** | `core/` + `steps.py`: aussagekräftige Exceptions werfen (`FileNotFoundError`, `ValueError` mit Kontext). Gefangen & formatiert wird **nur in `run.py`**. |
| **Kein `print()` außerhalb von `run.py`** | Dort: `rich` (Panels, Tabellen, Status-Spinner) – Präsentation an genau einem Ort |
| **LLM-Calls immer über `get_llm()`** | Nie `ChatOpenAI(...)` direkt in Workflows – sonst ist die Provider-Flexibilität kaputt |
| **Konstanten vs. Logik** | Prompts, Pfade, Limits = Konstanten am Datei-Start; keine Magischen Zahlen mitten in Funktionen |

### Naming-Konventionen (konsistent = vorhersagbar)

| Muster | Bedeutung | Beispiele |
|---|---|---|
| `load_*`, `split_*` | deterministische Aktionen (kein LLM) | `load_document()`, `split_into_chunks()` |
| `build_*_chain(llm)` | LCEL-Baustein (`prompt \| model`) | `build_chunk_analysis_chain()` |
| `run_<name>(llm, …)` | öffentliche Entry-Funktion eines Workflows | `run_pipeline()` |
| Verb-Namen für Tools | das LLM liest sie als Beschreibung | `search_knowledge_base()`, `calculate_ram()` |
| `PascalCase`-Klassen | nur Datenverträge (Pydantic) & ggf. Pipeline-Klasse bei Zustand | `PipelineReport`, `ChunkAnalysis` |

---

## 5. Prompts: wo leben sie?

- **Standard:** alle in `prompts.py` als benannte Konstanten (`CHUNK_ANALYSIS_PROMPT`).
- Lange Prompts machen **keine Funktionen länger** – sie sind Inhalt, keine Logik. Die
  Funktionslängen-Regel (§4) gilt nicht für Text-Konstanten.
- **Auslagerungs-Triggers** (dann: `workflows/<name>/prompt_texts/*.md` + Loader in `prompts.py`):
  1. Prompt > ~50 Zeilen (mehrseitiger System-Prompt)
  2. Nicht-Entwickler sollen den Prompt pflegen können
  3. Varianten / A-B-Tests nötig
- **Regel:** Der *Loader* bleibt immer in Python, der *Inhalt* darf wandern.

---

## 6. Testing: FakeLLM (der Payoff von Dependency Injection)

**Jeder Workflow muss ohne echtes LLM testbar sein.** Das ist der konkrete Nutzen der DI
(`run_pipeline(llm=…)` bekommt das Modell von außen):

```python
class FakeLLM:
    """Gleiche Schnittstelle wie ein echtes Chat-Modell, liefert aber
    vordefinierte, deterministische Antworten – keine API, keine Kosten."""
    def with_structured_output(self, schema): ...   # → gibt valide Schemas-Objekte zurück
    def invoke(self, prompt_value): ...             # → ChunkAnalysis / AIMessage aus dem Stand
```

**Was wir testen (deterministisch):** Splitten · Aggregation/Zählung · Schema-Validierung ·
Fehlerfälle (leere Datei, fehlende Datei) · Report-Struktur.
**Was wir NICHT testen:** "Schreibt das LLM gutes Deutsch?" – das ist per Definition nicht
deterministisch; dafür gibt man sich mit einem lokalen Smoke-Test gegen LM Studio zufrieden.

| Testart | Gegen | Geschwindigkeit |
|---|---|---|
| Unit (FakeLLM) | Logik um das LLM herum | sofort, offline, im CI |
| Integration (optional) | echter lokaler Endpoint | nur wenn LM Studio läuft (sonst skip) |

---

## 7. Definition of Done (pro Workflow / pro PR)

Ein Workflow gilt als **fertig**, wenn ALLES davon zutrifft:

```
□ Läuft lokal gegen den konfigurierten Endpoint (LM Studio)
□ Output ist ein validiertes Schema-Objekt (kein ungeprüftes JSON/Freitext)
□ Mit FakeLLM testbar (§6) – mindestens die Kernlogik
□ README.md des Workflows aktuell (Zweck, Datenfluss, Aufruf, Troubleshooting)
□ Keine Provider-Details außerhalb core/ (§1)
□ Root-Struktur entspricht dem Template (§2)
□ Neue Architektur-Entscheidung? → ADR geschrieben (§10)
```

Ohne DoD = kein Merge. Das ist die gemeinsame Qualitätslinie für Reviews.

---

## 8. Git-Konventionen

| Thema | Regel |
|---|---|
| **Branches** | `feature/<workflow>-<thema>` → z. B. `feature/workflow2-rag-indexing`, `fix/pipeline-default-path` |
| **Commits** | Imperativ + Scope: `pipeline: retry bei fehlgeschlagener Chunk-Analyse hinzufügen` |
| **Merge** | **Squash pro PR** → in `main` steht exakt ein sauberer Commit pro Feature (lesbare History) |
| **PRs** | klein & themenrein (1 Workflow = 1–2 PRs); Beschreibung: *Warum* + DoD-Checkliste (§7) abgehakt |
| **Konflikte** | `core/`-Änderungen zuerst mergen, dann Workflows darauf aufbauen (Schicht-Regel!) |

---

## 9. Onboarding-Pfad (erste 30 Minuten für neue Entwickler)

1. Root-`README.md` lesen → Quickstart durchlaufen (Workflow 1 läuft lokal)
2. `CONVENTIONS.md` §1–§3 lesen (Struktur, Template, Platzierungs-Baum)
3. `workflows/pipeline/README.md` lesen + den Code entlang des Datenflusses öffnen
4. `WORKFLOWS.md` ansehen → welchen Workflow übernimmt man?
5. Eigener Branch nach §8 anlegen → loslegen

> Onboarding ist **pro Projekt** einmalig definiert – nicht pro Workflow. Die lokalen
> Workflow-READMEs sind die zweite Ebene, wenn jemand einen bestimmten Workflow übernimmt.

---

## 10. ADRs – Architecture Decision Records

Nicht jede Entscheidung braucht ein ADR – aber jede, die **Struktur/Architektur betrifft und
nicht selbstverständlich ist** (z. B. "warum Funktionen statt Klasse?", "warum IO in run.py?").

- **Wo:** `docs/adr/NNNN-kurzer-titel.md` (nummeriert = chronologisch)
- **Format (halbe Seite):** Status · Kontext (warum stand's an?) · Entscheidung · Konsequenzen
- **Index:** `docs/adr/README.md`
- **Warum:** Das *Warum* hinter Entscheidungen überlebt sonst nur im Chatverlauf. ADRs sind die
  Versicherung, dass ein Nachfolger nicht dieselbe Diskussion von vorn beginnen muss.
