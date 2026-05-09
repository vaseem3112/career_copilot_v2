from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions     import db
from app.models.resume  import Resume
from app.models.analysis import ResumeAnalysis
from app.utils.response import success, error

ats_bp = Blueprint("ats", __name__)


# ─────────────────────────────────────────
# POST /api/v1/ats/generate
# ─────────────────────────────────────────
@ats_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate_ats():
    user_id = get_jwt_identity()
    data    = request.get_json(silent=True) or {}

    resume_id        = data.get("resume_id")
    target_job_title = (data.get("target_job_title") or "").strip()
    job_description  = (data.get("job_description")  or "").strip()
    company          = (data.get("company")           or "").strip()

    if not resume_id:
        return error("resume_id is required", 400)
    if not target_job_title:
        return error("target_job_title is required", 400)
    if not job_description:
        return error("job_description is required", 400)

    # ── Verify resume ownership ──
    resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
    if not resume:
        return error("Resume not found", 404)

    if not resume.raw_text:
        return error("Resume has not been parsed yet. Please wait for analysis to complete.", 400)

    # ── Run ATS generation (sync for now — move to Celery for prod) ──
    try:
        from app.modules.ats.generator import generate_ats_resume
        from app.modules.ats.scorer    import calculate_ats_score

        ats_text  = generate_ats_resume(
            resume_text      = resume.raw_text,
            job_description  = job_description,
            target_job_title = target_job_title,
            company          = company,
        )

        ats_score, matched_kw, missing_kw = calculate_ats_score(
            resume_text     = ats_text,
            job_description = job_description,
        )

        # ── Persist to analysis table ──
        analysis = ResumeAnalysis.query.filter_by(resume_id=resume_id).first()
        if analysis:
            analysis.ats_resume_text = ats_text
            db.session.commit()

        # ── Update ATS score on resume ──
        resume.ats_score = ats_score
        db.session.commit()

        # ── Save generated resume record ──
        from app.utils.file_handler import save_output
        filepath = save_output(ats_text, user_id, suffix="ats")
        gen_resume = Resume(
            user_id   = user_id,
            filename  = f"ATS_{target_job_title.replace(' ', '_')[:30]}.txt",
            filepath  = filepath,
            file_type = "txt",
            type      = "generated",
            status    = "analyzed",
            ats_score = ats_score,
            raw_text  = ats_text,
        )
        db.session.add(gen_resume)
        db.session.commit()

        return success({
            "ats": {
                "ats_score":        ats_score,
                "matched_keywords": matched_kw,
                "missing_keywords": missing_kw,
                "ats_resume":       ats_text,
                "resume_id":        gen_resume.id,
            }
        }, message="ATS resume generated")

    except Exception as e:
        current_app.logger.error(f"ATS generation failed: {e}")
        return error("ATS generation failed. Please try again.", 500)


# ─────────────────────────────────────────
# GET /api/v1/ats/score/<resume_id>
# ─────────────────────────────────────────
@ats_bp.route("/score/<resume_id>", methods=["GET"])
@jwt_required()
def get_ats_score(resume_id: str):
    user_id = get_jwt_identity()
    resume  = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
    if not resume:
        return error("Resume not found", 404)
    return success({"ats_score": resume.ats_score})
