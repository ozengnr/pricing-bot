# src/ingest.py
import pandas as pd
from pathlib import Path
import json, datetime, os, textwrap, requests

# Resolve paths whether run as script or inside Jupyter
if "__file__" in globals():
    BASE = Path(__file__).resolve().parent.parent
else:
    BASE = Path.cwd().parent

RAW   = BASE / "raw"  / "dummy_arr_data.csv"
CLEAN = BASE / "data" / "clean_metrics.parquet"
LOG   = BASE / "logs" / "ingest.log"
LOG.parent.mkdir(parents=True, exist_ok=True)

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def notify_slack(latest_mrr: float, rows: int) -> None:
    if not SLACK_WEBHOOK_URL:
        print("ℹ️  No SLACK_WEBHOOK_URL set — skipping Slack notify.")
        return
    msg = textwrap.dedent(f"""
        :white_check_mark: *Pricing-bot ingest complete*
        • Rows processed: `{rows:,}`
        • Latest month MRR: `${latest_mrr:,.0f}`
    """)
    r = requests.post(SLACK_WEBHOOK_URL, json={"text": msg})
    if r.status_code != 200:
        raise RuntimeError(f"Slack webhook failed → {r.text}")

def main() -> None:
    df = (pd.read_csv(RAW, parse_dates=["month"])
            .dropna(subset=["company_name", "arr_usd"])
            .assign(year   = lambda d: d.month.dt.year,
                    yyyymm = lambda d: d.month.dt.strftime("%Y-%m")))
    CLEAN.parent.mkdir(exist_ok=True)
    df.to_parquet(CLEAN, index=False)

    latest_month = df["month"].max()
    latest_mrr   = df.loc[df.month == latest_month, "arr_usd"].sum() / 12

    log_line = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "raw_rows": len(df),
        "latest_month": latest_month.strftime("%Y-%m"),
        "latest_mrr": round(latest_mrr, 2),
        "file": str(CLEAN)
    }
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(log_line) + "\n")

    notify_slack(latest_mrr, len(df))
    print(f"✓ Ingest complete — {len(df):,} rows → {CLEAN}")

if __name__ == "__main__":
    main()
