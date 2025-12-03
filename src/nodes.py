import json
from pathlib import Path
from src.utils import (
    avg_objective_context_similarity,
    simple_web_search_text,
    llm_relevance_score
)

ROOT = Path(__file__).resolve().parent
CHECKPOINT_FILE = ROOT / "checkpoints" / "ckpts_sample.json"

def load_checkpoint(checkpoint_id):
    with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
        checkpoints = json.load(f)
    for cp in checkpoints:
        if cp["checkpoint_id"] == checkpoint_id:
            return cp
    raise KeyError(f"Checkpoint {checkpoint_id} not found")

def gather_context(user_notes, queries):
    if user_notes and len(user_notes.split()) > 20:
        return {"source": "user_notes", "context": user_notes}
    web = simple_web_search_text(queries)
    return {"source": "web_search", "context": web}

def validate_context(objectives, context):
    emb = avg_objective_context_similarity(objectives, context)
    llm, note = llm_relevance_score(objectives, context)
    combined = (emb + llm) / 2
    return {
        "embedding_similarity": emb,
        "llm_score": llm,
        "combined_score": combined,
        "relevant": combined > 0.35,
        "note": note
    }

def start_checkpoint(checkpoint_id, user_notes=""):
    cp = load_checkpoint(checkpoint_id)
    ctx = gather_context(user_notes, cp["resources"]["web_search_queries"])
    val = validate_context(cp["objectives"], ctx["context"])
    return {"checkpoint": cp, "context": ctx, "validation": val}
