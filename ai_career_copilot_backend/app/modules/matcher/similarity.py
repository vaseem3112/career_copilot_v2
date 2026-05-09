"""
Runs cosine similarity between user profile embedding and all job embeddings.
Returns ranked list of job matches with scores.
"""
from app.modules.matcher.embedder import (
    cosine_similarity, similarity_to_score,
    load_vector, dump_vector, embed_profile, embed_job,
)
from app.models.job     import Job
from app.models.profile import UserProfile
from app.extensions     import db


def match_profile_to_jobs(user_id: str, top_n: int = 50) -> list[dict]:
    """
    Embed user profile and compare against all active job embeddings.
    Returns top_n matches sorted by score descending.
    """
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return []

    profile_dict = profile.to_dict()

    # ── Get or compute profile embedding ──
    if profile.embedding_json:
        profile_vec = load_vector(profile.embedding_json)
    else:
        profile_vec = embed_profile(profile_dict)
        profile.embedding_json = dump_vector(profile_vec)
        db.session.commit()

    # ── Load all active jobs ──
    jobs = Job.query.filter_by(is_active=True).all()
    if not jobs:
        return []

    results = []
    for job in jobs:
        # ── Get or compute job embedding ──
        if job.embedding_json:
            job_vec = load_vector(job.embedding_json)
        else:
            job_vec = embed_job(job.to_dict())
            job.embedding_json = dump_vector(job_vec)

        if not job_vec or not profile_vec:
            continue

        sim   = cosine_similarity(profile_vec, job_vec)
        score = similarity_to_score(sim)

        if score >= 30:  # only store meaningful matches
            results.append({
                "job_id": job.id,
                "score":  score,
                "reason": _build_reason(job, score),
            })

    db.session.commit()  # save any new embeddings
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_n]


def _build_reason(job: Job, score: int) -> str:
    """Generate a short human-readable reason for the match."""
    level = (
        "Strong match"     if score >= 80 else
        "Good match"       if score >= 60 else
        "Moderate match"   if score >= 45 else
        "Partial match"
    )
    return f"{level} based on your skills and experience with {job.company or 'this company'}'s requirements."
