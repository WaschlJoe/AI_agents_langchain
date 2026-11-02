# ADR 0002: Funktionen vor Klassen für die Orchestrierung

**Status:** accepted (2026-10-30)

## Kontext

Die Pipeline-Orchestrierung (`run_pipeline`) braucht das LLM in mehreren Schritten. Eine Klasse
könnte `llm` + Chains einmal binden und wäre bei Batch-Nutzung (viele Dateien, ein LLM) eleganter.
Gleichzeitig ist unser aktueller Use-Case "eine Datei pro Prozesslauf" – stateless zwischen Aufrufen.

## Entscheidung

- Orchestrierung und Schritte sind **Funktionen mit expliziten Parametern**
  (`run_pipeline(llm, path)`, `build_chunk_analysis_chain(llm)`).
- Klassen werden nur für **Datenverträge** (Pydantic: `ChunkAnalysis`, `PipelineReport`) verwendet.
- **Umstiegs-Trigger:** Sobald Zustand länger lebt als ein einzelner Aufruf (Batch-Modus,
  Retry-Zähler, Cache, wiederverwendete gebaute Chains) → dünne Pipeline-Klasse einführen,
  die `llm` + Chains in `__init__` bindet. Bis dahin: YAGNI.

## Konsequenzen

- **Positiv:** Schritte sind trivial einzeln testbar; alle Abhängigkeiten am Aufrufer sichtbar
  (explizit > implizit); passt zum LCEL-Idiom (`prompt | model` als komponierbare Runnables).
- **Negativ/Akzeptiert:** `llm` wird pro Ebene explizit weitergegeben (bewusste Wiederholung
  statt verstecktem `self.llm`).
