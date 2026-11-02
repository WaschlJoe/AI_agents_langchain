# Architecture Decision Records (ADRs)

Ein ADR hält eine **Architektur-Entscheidung mit ihrer Begründung** fest – damit das *Warum*
nicht im Chatverlauf stirbt, sondern nachvollziehbar bleibt.

**Format je ADR:** Status · Kontext (warum stand's an?) · Entscheidung · Konsequenzen.
**Regel:** Nur Entscheidungen, die Struktur/Architektur betreffen und nicht selbstverständlich sind.
Neues ADR = nächste freie Nummer, immer `accepted` oder `superseded by NNNN`.

## Index

| # | Titel | Status |
|---|---|---|
| [0001](0001-llm-factory-provider-abstraction.md) | LLM-Factory & Provider-Abschaltung (Factory + Strategy + DI + Adapter) | accepted |
| [0002](0002-functions-over-classes-for-orchestration.md) | Funktionen vor Klassen für die Orchestrierung | accepted |
| [0003](0003-io-nur-in-run-py.md) | IO (Konsole/Dateien) nur in `run.py` | accepted |
| [0004](0004-workflow-root-template.md) | Workflow-Root-Template: fixe 6 Dateien, Extras in benannte Unterordner | accepted |
