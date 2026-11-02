"""Workflow 1 – Dokumenten-Verarbeitungs-Pipeline.

Orchestriert die Schritte aus `steps.py`. Der Kontrollfluss (Loop über Chunks,
Aggregation) ist bewusster Python-Code; die linearen LLM-Aufrufe sind LCEL-Chains.

    ┌──────────┐   ┌──────────┐   ┌───────────────┐   ┌──────────┐   ┌──────────┐
    │ laden    │ → │ splitten │ → │ LLM pro Chunk │ → │ Summary  │ → │ Report   │
    │ (Code)   │   │ (Code)   │   │ (Structured)  │   │ (LLM)    │   │(Pydantic│
    └──────────┘   └──────────┘   └───────────────┘   └──────────┘   └──────────┘
"""

from __future__ import annotations

from pathlib import Path

from langchain_core.language_models.chat_models import BaseChatModel

from workflows.pipeline.schemas import ChunkAnalysis, PipelineReport
from workflows.pipeline.steps import (
    build_chunk_analysis_chain,
    build_overall_summary_chain,
    dominant_category,
    load_document,
    split_into_chunks,
)


def run_pipeline(
    llm: BaseChatModel,
    source_path: str | Path,
    max_chars: int = 1000,
    overlap: int = 150,
) -> PipelineReport:
    """Führt die komplette Pipeline aus.

    DI (Dependency Injection): `llm` wird von außen übergeben und hier NICHT
    gebaut → diese Funktion ist mit einem Mock-Modell testbar, ohne API-Calls.

    Args:
        llm:          Chat-Modell (aus core.llm.get_llm()).
        source_path:  Pfad zur Eingabedatei (.md / .txt).
        max_chars:    Maximale Zeichen pro Chunk (Default: 1000).
        overlap:      Überlappung zwischen Chunks in Zeichen (Default: 150).
    """
    # Schritt 1 + 2: laden & splitten (deterministisch)
    text, filename = load_document(source_path)
    chunks = split_into_chunks(text, max_chars=max_chars, overlap=overlap)

    # Schritt 3: LLM-Analyse pro Chunk (Structured Output → validierte Objekte)
    chunk_chain = build_chunk_analysis_chain(llm)
    analyses: list[ChunkAnalysis] = [
        chunk_chain.invoke({"source_file": filename, "text": chunk}) for chunk in chunks
    ]

    # Schritt 4: Gesamtzusammenfassung (Freitext) aus den Analysen
    summary_chain = build_overall_summary_chain(llm)
    result = summary_chain.invoke(
        {"chunk_analyses": "\n".join(a.model_dump_json(indent=2) for a in analyses)}
    )
    overall_summary = (result.content if hasattr(result, "content") else str(result)).strip()

    # Schritt 5: alles in den typisierten Report aggregieren
    return PipelineReport(
        source_file=filename,
        total_chunks=len(analyses),
        chunks=analyses,
        overall_summary=overall_summary,
        dominant_category=dominant_category(analyses),
    )
