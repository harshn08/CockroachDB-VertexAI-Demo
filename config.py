import os

# ── Google service-account JSON ───────────────────────────
# Usually exported in the shell:
#   export GOOGLE_APPLICATION_CREDENTIALS="$HOME/Documents/Gemini-Demo/keys/gemini-demo-key.json"
GOOGLE_APPLICATION_CREDENTIALS = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS",
    "<ADD-PATH-TO-JSON CREDENTIALS-HERE>",
)

# ── Vertex AI project details ─────────────────────────────
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "<GCP_PROJECT_ID>")
GCP_LOCATION   = os.getenv("GCP_LOCATION",   "<GCP_REGION_ID>")

# ── Optional: AI Studio key alternative ──────────

# ── CockroachDB connection string ────────────────────────
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "cockroachdb://root@localhost:26257/defaultdb?sslmode=disable",
)