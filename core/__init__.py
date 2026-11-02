"""Schicht 1: gemeinsame Infrastruktur (provider-unabhängig).

Enthält nur Bausteine, die von ALLEN Workflows/Agents genutzt werden:
- config.py → typsichere Einstellungen aus .env / Umgebungsvariablen
- llm.py    → LLM-Factory (einziger Ort im Code, der Provider kennt)
"""
