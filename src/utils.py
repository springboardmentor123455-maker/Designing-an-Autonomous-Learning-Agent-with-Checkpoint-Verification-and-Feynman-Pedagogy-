import os
import json
from dotenv import load_dotenv
load_dotenv()

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
EMBED_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

_embed_model = None

def get_embed_model():
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer(EMBED_MODEL_NAME)
    return _embed_model

def embed_texts(texts):
    model = get_embed_model()
    return model.encode(texts, convert_to_numpy=True)

def avg_objective_context_similarity(objectives, ctx):
    if not objectives or not ctx:
        return 0.0
    obj_embs = embed_texts(objectives)
    ctx_emb = embed_texts([ctx])[0]
    sims = cosine_similarity(obj_embs, [ctx_emb]).flatten()
    return float(np.mean(sims))

def serpapi_search(query, num=3):
    if not SERPAPI_KEY:
        return {"error": "No SERPAPI key"}
    url = "https://serpapi.com/search"
    params = {"engine": "google", "q": query, "api_key": SERPAPI_KEY, "num": num}
    resp = requests.get(url, params=params)
    return resp.json()

def simple_web_search_text(queries):
    snippets = []
    for q in queries:
        try:
            result = serpapi_search(q)
            for item in result.get("organic_results", []):
                snippets.append(item.get("snippet") or "")
        except:
            pass
    return "\n".join(snippets)

def llm_relevance_score(obj, ctx, model="gpt-4o-mini"):
    prompt = f"""
You are an evaluator. Read the objectives and context, and return:

{{
    "llm_relevance": 0-1 score,
    "note": "short comment"
}}

Objectives:
{json.dumps(obj)}

Context:
{ctx[:1500]}
"""

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120
        )
        text = response.choices[0].message.content
        parsed = json.loads(text)
        return parsed.get("llm_relevance", 0.0), parsed.get("note", "")
    except:
        return 0.0, "LLM error or JSON parse error"
