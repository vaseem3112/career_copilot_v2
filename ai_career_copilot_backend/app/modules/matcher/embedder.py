"""
Sentence-transformer embeddings for semantic job matching.
Vectors are stored in DB as JSON — computed once, reused many times.
"""
import json
import numpy as np

_model = None


def get_model():
    """Lazy-load the embedding model (downloads once on first use)."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        from flask import current_app
        model_name = current_app.config.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        _model = SentenceTransformer(model_name)
    return _model


def embed_text(text: str) -> list[float]:
    """Convert text to embedding vector."""
    model  = get_model()
    vector = model.encode(text, convert_to_numpy=True)
    return vector.tolist()


def embed_profile(profile_dict: dict) -> list[float]:
    """
    Build a rich profile text and embed it.
    Combines skills, experience, education for a dense representation.
    """
    parts = []

    skills = profile_dict.get("skills", [])
    if isinstance(skills, list):
        parts.append("Skills: " + ", ".join(skills))

    experience = profile_dict.get("experience", [])
    for exp in experience:
        if isinstance(exp, dict):
            parts.append(f"{exp.get('title', '')} at {exp.get('company', '')}: {exp.get('description', '')}")

    education = profile_dict.get("education", [])
    for edu in education:
        if isinstance(edu, dict):
            parts.append(f"{edu.get('degree', '')} in {edu.get('field', '')} from {edu.get('institution', '')}")

    summary = profile_dict.get("summary", "")
    if summary:
        parts.append(summary)

    text = " | ".join(filter(None, parts))
    if not text.strip():
        text = "No profile information"

    return embed_text(text)


def embed_job(job_dict: dict) -> list[float]:
    """Build job embedding from title + description + requirements."""
    parts = [
        job_dict.get("title", ""),
        job_dict.get("description", "")[:1000],
        " ".join(job_dict.get("requirements", [])[:10]),
    ]
    text = " ".join(filter(None, parts))
    return embed_text(text)


def cosine_similarity(vec_a: list, vec_b: list) -> float:
    """Compute cosine similarity between two vectors."""
    a = np.array(vec_a)
    b = np.array(vec_b)
    dot   = np.dot(a, b)
    norms = np.linalg.norm(a) * np.linalg.norm(b)
    if norms == 0:
        return 0.0
    return float(dot / norms)


def similarity_to_score(sim: float) -> int:
    """Convert cosine similarity (-1 to 1) to 0-100 integer score."""
    # Map 0.0–1.0 range to 0–100, clip negatives to 0
    return max(0, min(100, int(sim * 100)))


def load_vector(json_str: str) -> list[float]:
    if not json_str:
        return []
    return json.loads(json_str)


def dump_vector(vec: list[float]) -> str:
    return json.dumps(vec)
