from __future__ import annotations
from pathlib import Path
import typer
from rich import print
import pandas as pd

from finance_tracker.io import append_parquet, read_parquet
from finance_tracker.transform.normalize import normalize
from finance_tracker.transform.consolidate import monthly_rollup
from finance_tracker.viz.monthly import plot_monthly

from finance_tracker.ingest.pdf_base import parse_boh_statement
from finance_tracker.ingest.pdf_base import parse_boa_statement
from finance_tracker.ingest.csv_ingest import parse_discover_csv

app = typer.Typer(add_completion=False)

DATA_CURATED = Path("data/curated/transactions.parquet")
REPORTS = Path("reports")
REPORTS.mkdir(exist_ok=True)

@app.command()
def ingest(path: str, kind: str, account: str):
    """
    Ingest one file.
    kind: boh_pdf | boa_pdf | discover_csv
    """
    p = Path(path)
    if not p.exists():
        raise typer.BadParameter(f"File not found: {p}")

    if kind == "boh_pdf":
        df = parse_boh_statement(str(p), account=account)
    elif kind == "boa_pdf":
        df = parse_boa_statement(str(p), account=account)
    elif kind == "discover_csv":
        df = parse_discover_csv(str(p), account=account)
    else:
        raise typer.BadParameter("kind must be one of: boh_pdf, boa_pdf, discover_csv")

    df = normalize(df)
    append_parquet(df, str(DATA_CURATED))
    print(f"[green]Ingested[/green] {len(df)} rows from {p.name} → {DATA_CURATED}")

@app.command()
def monthly():
    """Build monthly rollup CSV in reports/."""
    txn = read_parquet(str(DATA_CURATED))
    m = monthly_rollup(txn)
    out = REPORTS / "monthly_rollup.csv"
    m.to_csv(out, index=False)
    print(f"[green]Wrote[/green] {out}")

@app.command()
def viz():
    """Generate monthly plot in reports/."""
    txn = read_parquet(str(DATA_CURATED))
    m = monthly_rollup(txn)
    out = REPORTS / "monthly_plot.png"
    plot_monthly(m, str(out))
    print(f"[green]Wrote[/green] {out}")

if __name__ == "__main__":
    app()