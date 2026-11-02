"""Die einzelnen Schritte der Pipeline – jeder klein und einzeln testbar.

Regel: Deterministische Logik (laden, splitten) ist reiner Python-Code.
LLM-Aufrufe sind LCEL-Chains (`prompt | model`).
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import Runnable
from langchain_text_splitters import RecursiveCharacterTextSplitter

from workflows.pipeline.prompts import (
    CHUNK_ANALYSIS_PROMPT,
    OVERALL_SUMMARY_PROMPT,
)
from workflows.pipeline.schemas import ChunkAnalysis, ChunkCategory


# ── Schritt 1: Dokument laden (reiner Code, kein LLM) ────────────────

def load_document(path: str | Path) -> tuple[str, str]:
    """Lädt eine Text/Markdown-Datei → (text, dateiname)."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Eingabedatei nicht gefunden: {p.resolve()}")
    text = p.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Datei ist leer: {p}")
    return text, p.name


# ── Schritt 2: in Chunks aufteilen (reiner Code, kein LLM) ───────────

def split_into_chunks(text: str, max_chars: int = 1000, overlap: int = 150) -> list[str]:
    """Teilt Text in überlappende Abschnitte auf (Standard-Splitter von LangChain)."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_chars,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""],  # erst an Absatz-, dann Satz-/Wortgrenzen
    )
    return [chunk for chunk in splitter.split_text(text) if chunk.strip()]


# ── Schritt 3: LLM-Analyse eines Chunks (LCEL + Structured Output) ───

def build_chunk_analysis_chain(llm: BaseChatModel) -> Runnable:
    """`prompt | model` – die klassische LCEL-Zusammensetzung.

    `with_structured_output(ChunkAnalysis)` zwingt das LLM, ein validiertes
    Pydantic-Objekt zurückzugeben statt Freitext → keine fragilen JSON-Parses.
    """
    structured_llm = llm.with_structured_output(ChunkAnalysis)
    return CHUNK_ANALYSIS_PROMPT | structured_llm


# ── Schritt 4: Gesamtzusammenfassung (Freitext-LLM-Aufruf) ───────────

def build_overall_summary_chain(llm: BaseChatModel) -> Runnable:
    """`prompt | model` – hier liefert das LLM bewusst Freitext."""
    return OVERALL_SUMMARY_PROMPT | llm


# ── Schritt 5 (Hilfsfunktion): dominanter Inhaltstyp ermitteln ───────

def dominant_category(analyses: list[ChunkAnalysis]) -> ChunkCategory | None:
    """Zählt die häufigste Kategorie über alle Chunks."""
    if not analyses:
        return None
    counts = Counter(a.category for a in analyses)
    return counts.most_common(1)[0][0]
