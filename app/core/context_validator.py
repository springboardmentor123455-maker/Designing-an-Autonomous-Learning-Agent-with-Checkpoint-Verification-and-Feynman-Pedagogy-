# app/core/context_validator.py
import json
import os
import re
import time
from typing import List, Tuple, Optional

from app.config import HF_MODEL_REPO_ID, HUGGINGFACEHUB_API_TOKEN

# Optional Document type from langchain_core
try:
    from langchain_core.documents import Document
except Exception:
    class Document:
        def __init__(self, page_content: str, metadata: dict = None):
            self.page_content = page_content
            self.metadata = metadata or {}

# -----------------------------
# Configurable small-model fallback
# -----------------------------
SMALL_MODEL_REPO_ID = os.getenv("SMALL_MODEL_REPO_ID", "distilgpt2")
# If primary local model takes more than this (seconds) to initialize, fallback to SMALL_MODEL_REPO_ID
MAX_LOCAL_LOAD_SECONDS = int(os.getenv("MAX_LOCAL_LOAD_SECONDS", "30"))

# -----------------------------
# Prompt template
# -----------------------------
VALIDATION_PROMPT_TEMPLATE = """
You are a strict evaluator for a learning agent. Read the context and the objectives and decide how sufficient the context is.

Instructions (very important):
- Do NOT repeat the prompt, the context, or any example.
- Respond with VALID JSON **only**, exactly one JSON object, nothing else.
- JSON keys: "score" (integer 1-5) and "feedback" (one short sentence).
- Example structure (do NOT copy exact words): {{ "score": 4, "feedback": "brief explanation" }}

Now evaluate.

Checkpoint topic:
{topic}

Checkpoint learning objectives:
{objectives}

Candidate context (snippets from notes or web):
{context_snippets}

Return the JSON now.
"""

# -----------------------------
# Local transformers pipeline loader (supports per-model caching)
# -----------------------------
_local_pipes = {}  # model_name -> pipeline
try:
    from transformers import pipeline as _transformers_pipeline  # type: ignore
except Exception:
    _transformers_pipeline = None


def _get_local_pipeline_for_model(model_repo_id: str):
    """
    Return a cached transformers pipeline for model_repo_id.
    Raises RuntimeError if transformers is missing.
    """
    if _transformers_pipeline is None:
        raise RuntimeError("transformers.pipeline is not available. Install 'transformers'.")

    if model_repo_id in _local_pipes:
        return _local_pipes[model_repo_id]

    # create pipeline, may be slow
    pipe = _transformers_pipeline("text-generation", model=model_repo_id, device=-1)
    _local_pipes[model_repo_id] = pipe
    return pipe


# -----------------------------
# Hugging Face inference client (remote)
# -----------------------------
_inference_client = None
try:
    from huggingface_hub import InferenceClient  # type: ignore
except Exception:
    InferenceClient = None


def _get_hf_client():
    global _inference_client
    if _inference_client is not None:
        return _inference_client
    if InferenceClient is None:
        raise RuntimeError("huggingface_hub.InferenceClient is not available. Install 'huggingface_hub'.")
    if not HUGGINGFACEHUB_API_TOKEN:
        raise RuntimeError("HUGGINGFACEHUB_API_TOKEN is not set in environment/.env")
    _inference_client = InferenceClient(HF_MODEL_REPO_ID, token=HUGGINGFACEHUB_API_TOKEN)
    return _inference_client


# -----------------------------
# Helpers for robust output cleaning & parsing
# -----------------------------
def _clean_model_output(raw: str) -> str:
    if not raw:
        return ""
    s = re.sub(r"```(?:json|text)?\n.*?\n```", "", raw, flags=re.S)
    s = re.sub(r"`+", "", s)
    return s.strip()


def _extract_score_and_feedback_from_text(raw: str) -> Tuple[float, str]:
    clean = _clean_model_output(raw)
    if not clean:
        return 2.0, "Model returned empty response."

    last_open = clean.rfind("{")
    last_close = clean.rfind("}")
    candidate = clean[last_open:last_close + 1] if last_open != -1 and last_close != -1 and last_close > last_open else clean

    try:
        data = json.loads(candidate)
        score = float(data.get("score", 2.0))
        feedback = str(data.get("feedback", "")).strip() or "No feedback text returned."
        return max(1.0, min(5.0, score)), feedback
    except Exception:
        score_match = re.search(r'"?score"?\s*:\s*([0-9]+(?:\.[0-9]+)?)', candidate)
        score = float(score_match.group(1)) if score_match else 2.0
        feedback_match = re.search(r'"?feedback"?\s*:\s*"([^"]+)"', candidate)
        feedback = feedback_match.group(1).strip() if feedback_match else "Model did not return clear feedback."
        return max(1.0, min(5.0, score)), feedback


# -----------------------------
# Heuristic fallback
# -----------------------------
_STOPWORDS = {"the", "is", "of", "and", "to", "for", "a", "an", "in", "on", "with", "as", "this", "that", "it", "be", "are", "can", "from", "by", "at"}


def _heuristic_score(topic: str, objectives: List[str], docs: List[Document]) -> Tuple[float, str]:
    text_body = " ".join(d.page_content for d in docs).lower()
    text_tokens = set(re.findall(r"\w+", text_body))
    all_text = (topic + " " + " ".join(objectives)).lower()
    cand_tokens = re.findall(r"\w+", all_text)
    keywords = [t for t in cand_tokens if t not in _STOPWORDS]
    if not keywords:
        return 2.0, "Heuristic: no meaningful keywords found; treating relevance as low."
    matches = sum(1 for k in keywords if k in text_tokens)
    coverage = matches / len(keywords)
    if coverage >= 0.8:
        score = 5.0
    elif coverage >= 0.6:
        score = 4.0
    elif coverage >= 0.4:
        score = 3.0
    elif coverage >= 0.2:
        score = 2.0
    else:
        score = 1.0
    feedback = f"Heuristic validation: {matches}/{len(keywords)} key terms appeared (coverage={coverage:.2f})."
    return score, feedback


# -----------------------------
# Local validation with auto-fallback to small model
# -----------------------------
def _validate_with_local_and_autofallback(prompt: str) -> Tuple[str, Optional[str], Optional[Exception]]:
    """
    Try to generate using HF_MODEL_REPO_ID locally. If load fails or initialization time exceeds
    MAX_LOCAL_LOAD_SECONDS, fall back to SMALL_MODEL_REPO_ID. Returns:
      (generated_text, fallback_note_or_None, exception_or_None)
    """
    primary = HF_MODEL_REPO_ID
    small = SMALL_MODEL_REPO_ID
    fallback_note = None

    # Try primary model
    try:
        t0 = time.time()
        pipe = _get_local_pipeline_for_model(primary)
        load_time = time.time() - t0
        if load_time > MAX_LOCAL_LOAD_SECONDS:
            # consider this a slow load and try the small model instead
            fallback_note = f"Primary model load_time {load_time:.1f}s > {MAX_LOCAL_LOAD_SECONDS}s; falling back to {small}"
            # attempt small model below
        else:
            # run generation with primary
            out = pipe(prompt, max_new_tokens=256, do_sample=False)
            text = out[0].get("generated_text") if isinstance(out, list) else str(out)
            return text, None, None
    except Exception as e_primary:
        # primary failed to initialize or generate; we'll try small
        e_primary = e_primary

    # Try small model as fallback
    try:
        if fallback_note is None:
            # we fell into except branch (primary errored) — record it
            fallback_note = f"Primary model failed; falling back to {small}"
        t0 = time.time()
        small_pipe = _get_local_pipeline_for_model(small)
        small_load_time = time.time() - t0
        out = small_pipe(prompt, max_new_tokens=200, do_sample=False)
        text = out[0].get("generated_text") if isinstance(out, list) else str(out)
        # annotate the generated text with fallback note so caller can see it (parser ignores JSON and picks last JSON)
        annotated = (f"<!-- FALLBACK:{small} -->\n" + text) if fallback_note else text
        return annotated, fallback_note, None
    except Exception as e_small:
        # Both failed; return empty and exception info (prefer small exception)
        return "", fallback_note or None, e_small


# -----------------------------
# HF remote validation
# -----------------------------
def _validate_with_hf(prompt: str) -> Tuple[str, Optional[Exception]]:
    try:
        client = _get_hf_client()
        text = client.text_generation(prompt, max_new_tokens=256, temperature=0.2)
        return str(text), None
    except Exception as e:
        return "", e


# -----------------------------
# Main dispatcher + validate_context API
# -----------------------------
def validate_context(topic: str, objectives: List[str], docs: List[Document], user_query: Optional[str] = None, backend: str = None) -> Tuple[float, str]:

    """
    backend: 'local', 'hf', 'heuristic', or 'auto' (default auto tries local -> hf -> heuristic)
    """
    if backend is None:
        backend = os.getenv("VALIDATION_BACKEND", "auto").lower()

    if not docs:
        return 1.0, "No context gathered; relevance automatically very low."

    joined = "\n\n---\n\n".join(d.page_content[:500] for d in docs[:5])
    prompt = VALIDATION_PROMPT_TEMPLATE.format(
        topic=topic,
        objectives="\n".join(f"- {obj}" for obj in objectives),
        context_snippets=joined,
    )

    tried = []

    def try_local():
        text, fallback_note, err = _validate_with_local_and_autofallback(prompt)
        if err is None and text:
            score, fb = _extract_score_and_feedback_from_text(text)
            if fallback_note:
                fb = fb + f" (auto-fallback used: {fallback_note})"
            return score, fb, None
        return None, None, err or Exception("local backend failed")

    def try_hf():
        text, err = _validate_with_hf(prompt)
        if err is None and text:
            score, fb = _extract_score_and_feedback_from_text(text)
            return score, fb, None
        return None, None, err or Exception("hf backend failed")

    order = []
    if backend == "auto":
        order = ["local", "hf", "heuristic"]
    else:
        order = [backend]

    for b in order:
        if b == "local":
            score, fb, err = try_local()
            if err is None:
                return score, fb
            tried.append(("local", err))
        elif b == "hf":
            score, fb, err = try_hf()
            if err is None:
                return score, fb
            tried.append(("hf", err))
        elif b == "heuristic":
            return _heuristic_score(topic, objectives, docs)
        else:
            return _heuristic_score(topic, objectives, docs)

    # All model backends failed — fall back to heuristic
    score, fb = _heuristic_score(topic, objectives, docs)
    err_summ = "; ".join(f"{k}:{str(e)}" for k, e in tried if e)
    if err_summ:
        fb = fb + f" (model backends failed: {err_summ})"
    return score, fb
