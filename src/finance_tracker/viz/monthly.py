from __future__ import annotations
import matplotlib.pyplot as plt
import pandas as pd

def plot_monthly(monthly: pd.DataFrame, out_path: str) -> None:
    plt.figure(figsize=(9, 4))
    x = monthly["month"]
    plt.plot(x, monthly["spend"], marker="o", label="Spend")
    plt.plot(x, monthly["income"], marker="o", label="Income")
    plt.plot(x, monthly["net_cashflow"], marker="o", label="Net cashflow")
    plt.xticks(rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)