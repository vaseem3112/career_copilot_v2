import os
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions     import db
from app.models.resume  import Resume
from app.utils.response import success, error

resume_bp = Blueprint("resume", __name__)


# ─────────────────────────────────────────
# GET /api/v1/resume/list
# ─────────────────────────────────────────
@resume_bp.route("/list", methods=["GET"])
@jwt_required()
def list_resumes():
    user_id = get_jwt_identity()
    resumes = (
        Resume.query
        .filter_by(user_id=user_id)
        .order_by(Resume.created_at.desc())
        .all()
    )
    return success({"resumes": [r.to_dict() for r in resumes]})


# ─────────────────────────────────────────
# DELETE /api/v1/resume/<resume_id>
# ─────────────────────────────────────────
@resume_bp.route("/<resume_id>", methods=["DELETE"])
@jwt_required()
def delete_resume(resume_id: str):
    user_id = get_jwt_identity()
    resume  = Resume.query.filter_by(id=resume_id, user_id=user_id).first()

    if not resume:
        return error("Resume not found", 404)

    # ── Delete file from disk ──
    try:
        if resume.filepath and os.path.exists(resume.filepath):
            os.remove(resume.filepath)
    except Exception:
        pass  # don't block deletion if file missing

    db.session.delete(resume)
    db.session.commit()
    return success(message="Resume deleted")
