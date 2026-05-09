"""
ATS Score Calculator — pure keyword overlap algorithm.
No AI involved — fast and deterministic.
"""
import re
from collections import Counter


def _tokenize(text: str) -> list[str]:
    words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#\.]{1,30}\b", text.lower())
    stopwords = {
        "the","and","or","with","for","to","in","of","a","an","is","are",
        "we","you","your","our","will","be","have","has","on","at","by",
        "as","this","that","must","should","can","from","experience","skills",
    }
    return [w for w in words if w not in stopwords and len(w) > 2]


def calculate_ats_score(
    resume_text:     str,
    job_description: str,
) -> tuple[int, list[str], list[str]]:
    """
    Calculate ATS score by measuring keyword overlap.

    Returns:
        score         : int 0-100
        matched_kw    : list of matched keywords
        missing_kw    : list of missing keywords
    """
    jd_tokens     = _tokenize(job_description)
    resume_tokens = set(_tokenize(resume_text))

    # Count keyword frequency in JD — more frequent = more important
    jd_freq      = Counter(jd_tokens)
    top_keywords = [w for w, _ in jd_freq.most_common(50)]

    matched = [kw for kw in top_keywords if kw in resume_tokens]
    missing = [kw for kw in top_keywords if kw not in resume_tokens]

    if not top_keywords:
        return 0, [], []

    # Score = (matched / total_top_keywords) * 100, capped at 100
    raw_score = int((len(matched) / len(top_keywords)) * 100)

    # Normalize: a perfect keyword match isn't 100 — cap at 95
    score = min(raw_score, 95)

    # Return display versions (title-cased)
    return score, matched[:20], missing[:20]


def format_score_label(score: int) -> str:
    if score >= 80: return "Excellent"
    if score >= 60: return "Good"
    if score >= 40: return "Fair"
    return "Needs Work"
