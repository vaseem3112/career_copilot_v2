"""
Orchestrates the full analysis pipeline.
Called by Celery task — not directly by API routes.
"""
from app.extensions      import db
from app.models.resume   import Resume
from app.models.analysis import ResumeAnalysis
from app.models.profile  import UserProfile
from app.modules.parser.extractor       import extract_text
from app.modules.parser.profile_builder import analyze_resume_text
from app.modules.ats.scorer             import calculate_ats_score
from app.modules.shortlist.feature_builder import build_feature_vector
from app.modules.shortlist.ml_predictor    import predict_probability
from flask import current_app


def run_full_analysis(resume_id: str, user_id: str) -> ResumeAnalysis:
    """
    Full pipeline:
    1. Extract raw text from file
    2. Send to Claude — get structured analysis
    3. Compute ATS score (algo)
    4. Compute shortlist probability (ML)
    5. Persist everything to DB
    """
    resume = Resume.query.get(resume_id)
    if not resume:
        raise ValueError(f"Resume {resume_id} not found")

    # ── Step 1: Extract text ──
    raw_text = extract_text(resume.filepath, resume.file_type)
    if not raw_text or len(raw_text.strip()) < 50:
        raise ValueError("Resume text too short — may be image-based or empty")

    resume.raw_text = raw_text
    db.session.flush()

    # ── Step 2: Claude analysis ──
    analysis_data = analyze_resume_text(raw_text)

    # ── Step 3: ATS score ──
    ats_text  = analysis_data.get("ats_resume", "")
    ats_score = 0
    if ats_text:
        ats_score, _, _ = calculate_ats_score(ats_text, raw_text)
        resume.ats_score = ats_score

    # ── Step 4: ML shortlist probability ──
    profile        = UserProfile.query.filter_by(user_id=user_id).first()
    shortlist_prob = analysis_data.get("shortlist_probability", 40)

    if profile:
        try:
            class _FakeJob:
                description = " ".join(analysis_data.get("skills", []))
                experience  = []
            features       = build_feature_vector(profile, _FakeJob())
            shortlist_prob = predict_probability(features)
        except Exception as e:
            current_app.logger.warning(f"ML prediction skipped: {e}")

    # Clamp to realistic range
    shortlist_prob = max(20, min(90, shortlist_prob))

    # ── Step 5: Persist ──
    existing = ResumeAnalysis.query.filter_by(resume_id=resume_id).first()
    if not existing:
        existing = ResumeAnalysis(resume_id=resume_id, user_id=user_id)
        db.session.add(existing)

    existing.profile_summary       = analysis_data.get("profile_summary", "")
    existing.experience_level      = analysis_data.get("experience_level", "")
    existing.skills                = analysis_data.get("skills", [])
    existing.domains               = analysis_data.get("domains", [])
    existing.suggested_roles       = analysis_data.get("suggested_roles", [])
    existing.strengths             = analysis_data.get("resume_analysis", {}).get("strengths", [])
    existing.weaknesses            = analysis_data.get("resume_analysis", {}).get("weaknesses", [])
    existing.missing_skills        = analysis_data.get("resume_analysis", {}).get("missing_skills", [])
    existing.matched_skills        = analysis_data.get("skill_gap", {}).get("matched", [])
    existing.gap_skills            = analysis_data.get("skill_gap", {}).get("missing", [])
    existing.suggestions           = analysis_data.get("skill_gap", {}).get("suggestions", [])
    existing.ats_resume_text       = ats_text
    existing.shortlist_probability = shortlist_prob

    resume.status = "analyzed"
    db.session.commit()

    current_app.logger.info(
        f"Analysis complete: resume={resume_id} "
        f"ats={ats_score} shortlist={shortlist_prob}%"
    )
    return existing
