from __future__ import annotations
import pandas as pd

REQUIRED_COLS = ["date", "amount", "description", "institution", "account", "source_file"]

def normalize(df: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    out = df.copy()
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out["amount"] = pd.to_numeric(out["amount"], errors="coerce")
    out["description"] = out["description"].astype(str).str.strip()
    out = out[(out["date"].dt.year >= 2000) & (out["date"].dt.year <= 2100)]
    out = out.dropna(subset=["date", "amount"])
    out["month"] = out["date"].dt.to_period("M").astype(str)
    return out[REQUIRED_COLS + ["month"]]