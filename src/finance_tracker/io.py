from __future__ import annotations
from pathlib import Path
import pandas as pd

def append_parquet(df: pd.DataFrame, path: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        old = pd.read_parquet(p)
        df = pd.concat([old, df], ignore_index=True)
        df = df.drop_duplicates(subset=["date", "amount", "description", "account", "institution", "source_file"])
    df.to_parquet(p, index=False)

def read_parquet(path: str) -> pd.DataFrame:
    return pd.read_parquet(path)