from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.resume   import Resume
from app.models.analysis import ResumeAnalysis
from app.utils.response  import success, error

analysis_bp = Blueprint("analysis", __name__)


# ─────────────────────────────────────────
# GET /api/v1/analysis/<resume_id>
# ─────────────────────────────────────────
@analysis_bp.route("/<resume_id>", methods=["GET"])
@jwt_required()
def get_analysis(resume_id: str):
    user_id  = get_jwt_identity()

    # ── Verify ownership ──
    resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
    if not resume:
        return error("Resume not found", 404)

    # ── Status check ──
    if resume.status == "pending":
        return success(
            {"status": "pending", "resume_id": resume_id},
            message = "Analysis not started yet"
        )

    if resume.status == "processing":
        return success(
            {"status": "processing", "resume_id": resume_id},
            message = "Analysis is in progress. Please wait."
        )

    if resume.status == "failed":
        return error("Analysis failed. Please re-upload or try again.", 500)

    # ── Fetch result ──
    analysis = ResumeAnalysis.query.filter_by(resume_id=resume_id).first()
    if not analysis:
        return error("Analysis result not found", 404)

    return success({"analysis": analysis.to_dict()})
