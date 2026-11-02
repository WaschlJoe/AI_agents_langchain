# ADR 0004: Workflow-Root-Template – fixe 6 Dateien, Extras in benannte Unterordner

**Status:** accepted (2026-10-30)

## Kontext

Mehrere Entwickler arbeiten parallel an verschiedenen Workflows/Agents. Für Reviews und
Übergaben (Krankheit, Abgang) muss die Struktur **vorhersehbar** sein: Wer `steps.py` öffnet,
weiß, was drinsteht – in jedem Ordner. Reaktive Faustregeln ("flat until it hurts") lassen
Interpretationsspielraum – den wollen wir nicht.

## Entscheidung

Jeder Workflow- und Agent-Ordner hat **ab Tag 1 exakt diese 6 Root-Dateien**:

```
README.md · run.py · prompts.py · schemas.py · steps.py (Agent: tools.py) · chain.py (Agent: agent.py)
```

- Alles darüber hinaus (Parser, Formatter, …) wandert in einen **nach Thema benannten
  Unterordner** (`parsing/`, `formatting/`) – nie als siebte Root-Datei.
- Generische Ordernamen wie `utils/` sind verboten; der Name muss das Thema sagen.
- Gewachsene Unterordner folgen demselben Muster (eigene kurze README + Module).

## Konsequenzen

- **Positiv:** Maximale Vorhersagbarkeit ("Muskelspeicher") über alle Workflows; Reviews werden
  schneller, weil man weiß, wo was ist; Onboarding reduziert sich auf "Template kennen".
- **Negativ/Akzeptiert:** Manche Dateien sind anfangs klein (z. B. `schemas.py` bei einfachen
  Agents) – bewusst akzeptiert im Namen der Konsistenz.
