from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions      import db
from app.models.resume   import Resume
from app.utils.response  import success, error
from app.utils.file_handler import save_upload, allowed_file
from app.tasks.analysis_task import run_resume_analysis

parser_bp = Blueprint("parser", __name__)


# ─────────────────────────────────────────
# POST /api/v1/parser/upload
# ─────────────────────────────────────────
@parser_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_resume():
    user_id = get_jwt_identity()

    if "resume" not in request.files:
        return error("No file provided. Field name must be 'resume'", 400)

    file = request.files["resume"]

    if not file.filename:
        return error("Empty filename", 400)

    if not allowed_file(file.filename):
        return error("Only PDF, DOC and DOCX files are allowed", 400)

    # ── Check file size (also enforced by Flask MAX_CONTENT_LENGTH) ──
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > current_app.config["MAX_CONTENT_LENGTH"]:
        return error("File exceeds 5MB limit", 413)

    # ── Save to disk ──
    try:
        filepath, original_name, ext = save_upload(file, user_id)
    except Exception as e:
        current_app.logger.error(f"File save failed: {e}")
        return error("Failed to save file", 500)

    # ── Create resume record ──
    resume = Resume(
        user_id   = user_id,
        filename  = original_name,
        filepath  = filepath,
        file_type = ext,
        file_size = size,
        type      = "uploaded",
        status    = "pending",
    )
    db.session.add(resume)
    db.session.commit()

    # ── Trigger async AI analysis ──
    try:
        run_resume_analysis.delay(resume.id, user_id)
        resume.status = "processing"
        db.session.commit()
    except Exception as e:
        current_app.logger.warning(f"Analysis task dispatch failed: {e}")

    return success(
        {"resume": resume.to_dict()},
        message = "Resume uploaded. AI analysis started.",
        status  = 201,
    )


# ─────────────────────────────────────────
# POST /api/v1/parser/analyze/:resume_id
# ─────────────────────────────────────────
@parser_bp.route("/analyze/<resume_id>", methods=["POST"])
@jwt_required()
def analyze_resume(resume_id: str):
    user_id = get_jwt_identity()
    resume  = Resume.query.filter_by(id=resume_id, user_id=user_id).first()

    if not resume:
        return error("Resume not found", 404)

    if resume.status == "processing":
        return success(
            {"resume_id": resume_id, "status": "processing"},
            message = "Analysis already in progress"
        )

    # ── Re-trigger analysis ──
    try:
        run_resume_analysis.delay(resume.id, user_id)
        resume.status = "processing"
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Analysis dispatch failed: {e}")
        return error("Failed to start analysis", 500)

    return success(
        {"resume_id": resume_id, "status": "processing"},
        message = "Analysis started"
    )
