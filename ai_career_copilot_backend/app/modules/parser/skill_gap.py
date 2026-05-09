"""
Real skill gap analysis — compares actual resume skills vs actual JD requirements.
No AI for this step — pure set difference.
Claude is only used for generating improvement suggestions.
"""
import re
from app.modules.ai.llm_client      import call_claude
from app.modules.ai.prompts         import build_skill_gap_prompt
from app.modules.ai.response_parser import parse_json_response


def extract_keywords_from_jd(job_description: str) -> list[str]:
    """Extract key skill keywords from a job description using simple NLP."""
    # Common filler words to skip
    stopwords = {
        "the", "and", "or", "with", "for", "to", "in", "of", "a", "an",
        "is", "are", "we", "you", "your", "our", "their", "will", "be",
        "have", "has", "on", "at", "by", "as", "this", "that", "must",
        "should", "can", "who", "what", "how", "when", "where", "from",
        "experience", "ability", "strong", "good", "excellent", "skills",
        "knowledge", "working", "understanding", "years", "year", "least",
    }
    words  = re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#\.]{1,30}\b", job_description)
    result = []
    seen   = set()
    for w in words:
        lw = w.lower()
        if lw not in stopwords and lw not in seen and len(lw) > 2:
            result.append(w)
            seen.add(lw)
    return result[:60]  # cap at 60 keywords


def compute_skill_gap(
    resume_skills:   list[str],
    job_description: str,
    target_role:     str = "",
) -> dict:
    """
    Compare resume skills against JD keywords.
    Returns matched, missing, suggestions.
    """
    jd_keywords     = extract_keywords_from_jd(job_description)
    resume_lower    = {s.lower() for s in resume_skills}
    jd_lower        = {k.lower() for k in jd_keywords}

    matched = [k for k in jd_keywords if k.lower() in resume_lower]
    missing = [k for k in jd_keywords if k.lower() not in resume_lower]

    # Claude generates improvement suggestions for ONLY the missing skills
    suggestions = []
    if missing and target_role:
        try:
            prompt = build_skill_gap_prompt(target_role)
            msg    = (
                f"Candidate skills: {', '.join(resume_skills)}\n"
                f"Missing skills:   {', '.join(missing[:15])}\n"
                f"Target role:      {target_role}"
            )
            raw  = call_claude(prompt, msg, max_tokens=1000)
            data = parse_json_response(raw)
            suggestions = data.get("suggestions", [])
        except Exception:
            suggestions = [f"Consider learning {s}" for s in missing[:5]]

    return {
        "matched":     matched[:30],
        "missing":     missing[:30],
        "suggestions": suggestions[:10],
    }
