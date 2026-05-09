"""
Async Celery task — runs full AI analysis pipeline after resume upload.
"""
from app.extensions import celery, db
from flask import current_app


@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def run_resume_analysis(self, resume_id: str, user_id: str):
    """
    Full pipeline:
    1. Extract text from file
    2. Send to Claude for analysis
    3. Compute shortlist probability (ML)
    4. Store results in DB
    5. Send notification to user
    6. Trigger job matching
    """
    from app.models.resume   import Resume
    from app.models.analysis import ResumeAnalysis
    from app.models.profile  import UserProfile
    from app.models.notification import Notification

    from app.modules.parser.extractor      import extract_text
    from app.modules.parser.profile_builder import analyze_resume_text
    from app.modules.shortlist.feature_builder import build_feature_vector
    from app.modules.shortlist.ml_predictor    import predict_probability

    resume = Resume.query.get(resume_id)
    if not resume:
        current_app.logger.error(f"Resume {resume_id} not found")
        return

    try:
        resume.status = "processing"
        db.session.commit()

        # ── Step 1: Extract text ──
        raw_text = extract_text(resume.filepath, resume.file_type)
        if not raw_text or len(raw_text.strip()) < 50:
            raise ValueError("Extracted text is too short — file may be empty or image-based")

        resume.raw_text = raw_text
        db.session.commit()

        # ── Step 2: Claude analysis ──
        analysis_data = analyze_resume_text(raw_text)

        # ── Step 3: Shortlist probability via ML ──
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        shortlist_prob = 0
        if profile:
            try:
                # Use first suggested role for feature building
                fake_job = type("J", (), {
                    "description": " ".join(analysis_data.get("skills", [])),
                    "experience":  [], "to_dict": lambda self: {},
                })()
                features       = build_feature_vector(profile, fake_job)
                shortlist_prob = predict_probability(features)
            except Exception as e:
                current_app.logger.warning(f"ML prediction failed: {e}")
                shortlist_prob = analysis_data.get("shortlist_probability", 40)
        else:
            shortlist_prob = analysis_data.get("shortlist_probability", 40)

        # ── Step 4: Store results ──
        existing = ResumeAnalysis.query.filter_by(resume_id=resume_id).first()
        if not existing:
            existing = ResumeAnalysis(resume_id=resume_id, user_id=user_id)
            db.session.add(existing)

        existing.profile_summary      = analysis_data.get("profile_summary", "")
        existing.experience_level     = analysis_data.get("experience_level", "")
        existing.skills               = analysis_data.get("skills", [])
        existing.domains              = analysis_data.get("domains", [])
        existing.suggested_roles      = analysis_data.get("suggested_roles", [])
        existing.strengths            = analysis_data.get("resume_analysis", {}).get("strengths", [])
        existing.weaknesses           = analysis_data.get("resume_analysis", {}).get("weaknesses", [])
        existing.missing_skills       = analysis_data.get("resume_analysis", {}).get("missing_skills", [])
        existing.matched_skills       = analysis_data.get("skill_gap", {}).get("matched", [])
        existing.gap_skills           = analysis_data.get("skill_gap", {}).get("missing", [])
        existing.suggestions          = analysis_data.get("skill_gap", {}).get("suggestions", [])
        existing.ats_resume_text      = analysis_data.get("ats_resume", "")
        existing.shortlist_probability = shortlist_prob

        # Update ATS score on resume
        from app.modules.ats.scorer import calculate_ats_score
        if existing.ats_resume_text:
            ats_score, _, _ = calculate_ats_score(existing.ats_resume_text, raw_text)
            resume.ats_score = ats_score

        resume.status = "analyzed"
        db.session.commit()

        # ── Step 5: Notify user ──
        notif = Notification.create(
            user_id = user_id,
            message = f"Your resume '{resume.filename}' has been analyzed. Shortlist probability: {shortlist_prob}%",
            type    = "analysis_done",
        )
        db.session.add(notif)
        db.session.commit()

        # ── Step 6: Trigger job matching ──
        run_job_matching_after_analysis.delay(user_id)

        current_app.logger.info(f"Analysis complete: resume={resume_id} prob={shortlist_prob}%")

    except Exception as exc:
        current_app.logger.error(f"Analysis failed for resume {resume_id}: {exc}")
        resume.status = "failed"
        db.session.commit()
        raise self.retry(exc=exc)


@celery.task
def run_job_matching_after_analysis(user_id: str):
    """Trigger job matching after analysis completes."""
    from app.tasks.match_task import run_job_matching
    run_job_matching.delay(user_id)
