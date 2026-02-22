from __future__ import annotations
import pandas as pd

def monthly_rollup(txn: pd.DataFrame) -> pd.DataFrame:
    return (
        txn.groupby("month")
        .agg(
            net_cashflow=("amount", "sum"),
            income=("amount", lambda s: s[s > 0].sum()),
            spend=("amount", lambda s: -s[s < 0].sum()),
            n_txn=("amount", "size"),
        )
        .reset_index()
        .sort_values("month")
    )