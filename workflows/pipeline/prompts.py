"""Prompt-Templates für Workflow 1 – strikt getrennt von der Logik.

Prompts sind "Inhalt", Steps/Chains sind "Mechanik". So kann man Prompts
optimieren, ohne Code anzufassen – und umgekehrt.
"""

from langchain_core.prompts import ChatPromptTemplate

# ── Schritt 3: Analyse eines einzelnen Chunks (→ Structured Output) ──
CHUNK_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Du bist ein präziser Dokumenten-Analyst. "
            "Analysiere den übergebenen Textabschnitt sachlich und neutral. "
            "Gib die Ergebnisse strikt im vorgegebenen Format zurück.",
        ),
        (
            "human",
            "Dokument: {source_file}\n\n"
            "Textabschnitt:\n\"\"\"\n{text}\n\"\"\"",
        ),
    ]
)

# ── Schritt 4: Gesamtzusammenfassung aus den Chunk-Analysen (Freitext) ──
OVERALL_SUMMARY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Du fasst Dokument-Analysen zusammen. Schreibe eine knappe, neutrale "
            "Gesamtzusammenfassung auf Deutsch.",
        ),
        (
            "human",
            "Hier sind die Analysen der einzelnen Abschnitte eines Dokuments:\n\n"
            "{chunk_analyses}\n\n"
            "Schreibe daraus eine Gesamtzusammenfassung in 2-4 Sätzen. "
            "Nenne am Ende auch den dominanten Inhaltstyp des Dokuments.",
        ),
    ]
)
