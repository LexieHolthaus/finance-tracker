# Functions for analyzing financial data
import pandas as pd

def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    df["month"] = df["date"].dt.to_period("M")
    return df.groupby("month")["amount"].sum().reset_index()