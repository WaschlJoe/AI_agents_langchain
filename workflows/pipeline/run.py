"""CLI-Einstiegspunkt für Workflow 1 (Dokumenten-Verarbeitungs-Pipeline).

Aufruf:
    python -m workflows.pipeline.run [Pfad-zu-Datei]
    (Default: data/beispiel.md)
"""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from core.config import get_settings
from core.llm import get_llm
from workflows.pipeline.chain import run_pipeline
from workflows.pipeline.schemas import PipelineReport

# run.py liegt in workflows/pipeline/ → 2 Ebenen hoch = Projekt-Root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "beispiel.md"
OUTPUT_DIR = PROJECT_ROOT / "output"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Workflow 1: Dokumenten-Verarbeitungs-Pipeline (LangChain)"
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=str(DEFAULT_INPUT),
        help="Pfad zur .md/.txt-Datei (Default: data/beispiel.md)",
    )
    parser.add_argument(
        "--chunk-size", type=int, default=1000,
        help="Maximale Zeichen pro Chunk (Default: 1000)",
    )
    parser.add_argument(
        "--overlap", type=int, default=150,
        help="Überlappung zwischen Chunks in Zeichen (Default: 150)",
    )
    args = parser.parse_args()

    console = Console()

    # ── Config & LLM (DI: genau einmal bauen, dann weiterreichen) ─────
    settings = get_settings()
    llm = get_llm(settings)

    console.print(
        Panel.fit(
            f"[bold]Provider:[/bold] {settings.provider.value}\n"
            f"[bold]Endpoint:[/bold] {settings.resolved_base_url or '(Package-Default)'}\n"
            f"[bold]Modell:[/bold]   {settings.model_name}",
            title="LLM-Konfiguration",
        )
    )

    # ── Pipeline ausführen ────────────────────────────────────────────
    with console.status("Pipeline läuft …"):
        report = run_pipeline(
            llm=llm,
            source_path=args.input,
            max_chars=args.chunk_size,
            overlap=args.overlap,
        )

    _print_report(console, report)

    # ── JSON-Report speichern (das "strukturierte Ergebnis") ─────────
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUTPUT_DIR / f"{Path(args.input).stem}.json"
    out_file.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    console.print(f"\n[green]✔[/green] JSON-Report gespeichert: [bold]{out_file}[/bold]")


def _print_report(console: Console, report: PipelineReport) -> None:
    """Gibt den Report formatiert in der Konsole aus."""
    console.rule("Ergebnis")
    dominant = (
        report.dominant_category.value if report.dominant_category else "-"
    )
    console.print(
        f"[bold]Dokument:[/bold] {report.source_file}   "
        f"[bold]Chunks:[/bold] {report.total_chunks}   "
        f"[bold]Dominanter Typ:[/bold] {dominant}"
    )
    console.print()

    for i, chunk in enumerate(report.chunks, start=1):
        console.print(
            Panel.fit(
                f"[italic]{chunk.summary}[/italic]\n\n"
                f"Typ: [cyan]{chunk.category.value}[/cyan]   "
                f"Konfidenz: {chunk.confidence:.0%}",
                title=f"Chunk {i}/{report.total_chunks}",
            )
        )
        for point in chunk.key_points:
            console.print(f"  • {point}")

    console.rule("Gesamtzusammenfassung")
    console.print(report.overall_summary)


if __name__ == "__main__":
    main()
