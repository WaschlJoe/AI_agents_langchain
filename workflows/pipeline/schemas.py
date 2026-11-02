"""Pydantic-Modelle: die "Verträge" der Pipeline.

Diese Schemas definieren, was das LLM liefern MUSS (Structured Outputs)
und wie das Endergebnis aussieht – typsicher statt fragiles JSON-Parsing.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ChunkCategory(str, Enum):
    """Mögliche Inhaltstypen eines Textabschnitts."""

    FAKTEN = "fakten"
    ANLEITUNG = "anleitung"
    MEINUNG = "meinung"
    FRAGE = "frage"
    SONSTIGES = "sonstiges"


class ChunkAnalysis(BaseModel):
    """Strukturiertes Ergebnis der LLM-Analyse für EINEN Textabschnitt."""

    summary: str = Field(
        description="Knappe Zusammenfassung des Abschnitts in 1-2 Sätzen (Deutsch)."
    )
    category: ChunkCategory = Field(
        description="Der dominante Inhaltstyp dieses Abschnitts."
    )
    key_points: list[str] = Field(
        default_factory=list,
        description="Wichtige Fakten/Punkte aus dem Abschnitt (max. 5, je ein Satz).",
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Wie eindeutig der Inhaltstyp zuordenbar ist (0.0–1.0).",
    )


class PipelineReport(BaseModel):
    """Das finale Ergebnis der gesamten Pipeline."""

    source_file: str = Field(description="Name der verarbeiteten Quelldatei.")
    total_chunks: int = Field(description="Anzahl analysierter Abschnitte.")
    chunks: list[ChunkAnalysis] = Field(
        description="Die Analysen aller Abschnitte, in Dokument-Reihenfolge."
    )
    overall_summary: str = Field(
        description="Gesamtzusammenfassung des gesamten Dokuments (2-4 Sätze)."
    )
    dominant_category: ChunkCategory | None = Field(
        default=None,
        description="Der häufigste Inhaltstyp über alle Abschnitte.",
    )
