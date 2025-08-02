# api/main.py
from fastapi import FastAPI, Form

app = FastAPI()

# ── 1. Health-check route ──────────────────────────────────────────────
@app.get("/")
async def health():
    return {"status": "ok"}

# ── 2. Slash-command route for Slack  ──────────────────────────────────
@app.post("/slash-kpi")
async def slash_kpi(text: str = Form("")):
    """Simple echo until we wire KPIs."""
    if text.strip() == "latest":
        return {
            "response_type": "in_channel",
            "text": "*Latest MRR*: `$123 456`\n*Overall NRR*: 108 %"
        }
    return {
        "response_type": "ephemeral",
        "text": "Try `/kpi latest`"
    }
