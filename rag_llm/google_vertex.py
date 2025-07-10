import os, json, vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from sqlalchemy import create_engine, text
from sentence_transformers import SentenceTransformer

# ── DB connection ───────────────────────────────────
DB_URI = "cockroachdb://root@localhost:26257/defaultdb?sslmode=disable"
engine = create_engine(DB_URI)

# ── Embedding helpers ───────────────────────────────
def numpy_vector_to_pg_vector(vec):
    return json.dumps(vec.flatten().tolist())        # exactly what insert_data.py writes

def get_query_embedding(text: str) -> str:
    model = SentenceTransformer("all-MiniLM-L6-v2")  # keep SAME model as ingest
    return numpy_vector_to_pg_vector(model.encode(text))

# ── Vector search ───────────────────────────────────
def search_expenses(query: str, limit: int = 5):
    search_embedding = get_query_embedding(query)
    sql = text("""
        SELECT
            expense_id,
            description,
            expense_amount,
            merchant,
            shopping_type,
            payment_method,
            embedding <-> :search_embedding AS similarity_score
        FROM expenses
        ORDER BY embedding <-> :search_embedding
        LIMIT :limit
    """)
    with engine.connect() as conn:
        rows = conn.execute(sql,
                            {"search_embedding": search_embedding,
                             "limit": limit}).fetchall()
    return [dict(row._mapping) for row in rows]

# ── RAG generation ─────────────────────────────────
def RAG_response(prompt: str,
                 search_results=None,
                 project_id=os.getenv("GCP_PROJECT_ID"),
                 location=os.getenv("GCP_LOCATION", "us-central1")):
    vertexai.init(project=project_id, location=location)
    model = GenerativeModel("gemini-1.0-pro")        # GA model name

    context_block = ""
    if search_results:
        context_block = "\n".join(
            f"Description: {r['description']}, Merchant: {r['merchant']}, "
            f"Amount: ${r['expense_amount']}, Type: {r['shopping_type']}"
            for r in search_results
        )

    cfg = GenerationConfig(temperature=1.0, top_p=0.95,
                           top_k=40, max_output_tokens=1024)

    resp = model.generate_content(
        f"{prompt}\n\nSearch Results:\n{context_block}", generation_config=cfg
    )
    return resp.candidates[0].text
