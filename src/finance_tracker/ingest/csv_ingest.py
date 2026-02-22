from __future__ import annotations
import os
import pandas as pd

def parse_discover_csv(path: str, account: str = "Discover", institution: str = "Discover") -> pd.DataFrame:
    df = pd.read_csv(path)

    # Discover statement CSV: Amount is "effect on balance"
    # Convert to cashflow: cashflow = -Amount
    out = pd.DataFrame(
        {
            "date": pd.to_datetime(df["Post Date"], format="%m/%d/%Y", errors="coerce"),
            "amount": -pd.to_numeric(df["Amount"], errors="coerce"),
            "description": df["Description"].astype(str),
            "institution": institution,
            "account": account,
            "source_file": os.path.basename(path),
        }
    )
    return out.dropna(subset=["date", "amount"])