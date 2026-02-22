# Functions for ingesting financial data
import pandas as pd

def load_transactions(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.str.lower().str.strip()

    # Normalize common fields
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])

    if "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    return df