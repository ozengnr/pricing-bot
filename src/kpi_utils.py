from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "clean_metrics.parquet"

def load_metrics() -> pd.DataFrame:
    """Load the latest cleaned Parquet file."""
    return pd.read_parquet(DATA)

def monthly_mrr(df: pd.DataFrame) -> pd.DataFrame:
    mrr = (df.assign(mrr_usd = df.arr_usd / 12)
             .groupby("month", as_index=False)["mrr_usd"]
             .sum())
    return mrr

def latest_mrr(df: pd.DataFrame) -> float:
    last_month = df["month"].max()
    return df.loc[df.month == last_month, "arr_usd"].sum() / 12

def overall_nrr(df: pd.DataFrame) -> float:
    pivot = df.pivot(index="company_name", columns="month", values="arr_usd").fillna(0)
    return pivot.iloc[:, -1].sum() / pivot.iloc[:, 0].sum() - 1
