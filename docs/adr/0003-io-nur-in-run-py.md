# ADR 0003: IO (Konsole/Dateien) nur in `run.py`

**Status:** accepted (2026-10-30)

## Kontext

Die Pipeline erzeugt einen Report. Frage: Wer zeigt ihn an und wer schreibt `output/*.json` –
die Orchestrierung (`chain.py`) oder der Einstiegspunkt (`run.py`)?

## Entscheidung

- **Workflows produzieren Daten** (typisierte Objekte wie `PipelineReport`) – nichts anderes.
  `chain.py`, `steps.py`, `core/` berühren nie Konsole oder Dateisystem-Ausgabe.
- **Der Einstiegspunkt entscheidet über das Schicksal der Daten:** `run.py` macht Rich-Konsole,
  JSON-Speicherung, Fehlerformatierung – alles an genau einem Ort.

## Konsequenzen

- **Positiv:** Workflow-Logik ist side-effect-frei testbar (keine Dateien/Konsolensalat in Tests);
  dieselbe Pipeline lässt sich später in einen API-Server einbinden, wo "Output" eine HTTP-Antwort
  statt einer Datei ist; Präsentationsänderungen touchen nie die Logik.
- **Negativ/Akzeptiert:** `run.py` bündelt mehrere Sorgen (Parsing + Wiring + IO) – bewusst,
  weil es der dünne Rand des Systems ist.
