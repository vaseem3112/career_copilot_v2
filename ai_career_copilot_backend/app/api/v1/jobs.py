from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions      import db
from app.models.job      import Job
from app.models.saved_job import SavedJob
from app.utils.response  import success, error

jobs_bp = Blueprint("jobs", __name__)


# ─────────────────────────────────────────
# GET /api/v1/jobs
# ─────────────────────────────────────────
@jobs_bp.route("", methods=["GET"])
@jwt_required()
def list_jobs():
    user_id    = get_jwt_identity()
    page       = int(request.args.get("page",   1))
    limit      = int(request.args.get("limit",  20))
    domain     = request.args.get("domain",     "").strip()
    location   = request.args.get("location",   "").strip()
    experience = request.args.get("experience", "").strip()
    job_type   = request.args.get("job_type",   "").strip()

    query = Job.query.filter_by(is_active=True)

    if domain:     query = query.filter(Job.domain.ilike(f"%{domain}%"))
    if location:   query = query.filter(Job.location.ilike(f"%{location}%"))
    if experience: query = query.filter(Job.experience_level == experience)
    if job_type:   query = query.filter(Job.job_type == job_type)

    total      = query.count()
    jobs       = query.order_by(Job.fetched_at.desc()).offset((page - 1) * limit).limit(limit).all()

    # ── Mark saved jobs for this user ──
    saved_ids  = {
        s.job_id for s in
        SavedJob.query.filter_by(user_id=user_id).all()
    }

    jobs_data  = []
    for j in jobs:
        d = j.to_dict()
        d["isSaved"] = j.id in saved_ids
        jobs_data.append(d)

    return success({
        "jobs":  jobs_data,
        "total": total,
        "page":  page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
    })


# ─────────────────────────────────────────
# GET /api/v1/jobs/saved
# ─────────────────────────────────────────
@jobs_bp.route("/saved", methods=["GET"])
@jwt_required()
def get_saved_jobs():
    user_id = get_jwt_identity()
    saved   = (
        SavedJob.query
        .filter_by(user_id=user_id)
        .order_by(SavedJob.saved_at.desc())
        .all()
    )
    jobs_data = []
    for s in saved:
        if s.job:
            d = s.job.to_dict()
            d["isSaved"] = True
            jobs_data.append(d)

    return success({"jobs": jobs_data})


# ─────────────────────────────────────────
# POST /api/v1/jobs/save/<job_id>
# ─────────────────────────────────────────
@jobs_bp.route("/save/<job_id>", methods=["POST"])
@jwt_required()
def save_job(job_id: str):
    user_id = get_jwt_identity()

    job = Job.query.get(job_id)
    if not job:
        return error("Job not found", 404)

    existing = SavedJob.query.filter_by(user_id=user_id, job_id=job_id).first()
    if existing:
        return success(message="Job already saved")

    db.session.add(SavedJob(user_id=user_id, job_id=job_id))
    db.session.commit()
    return success(message="Job saved")


# ─────────────────────────────────────────
# DELETE /api/v1/jobs/save/<job_id>
# ─────────────────────────────────────────
@jobs_bp.route("/save/<job_id>", methods=["DELETE"])
@jwt_required()
def unsave_job(job_id: str):
    user_id = get_jwt_identity()
    saved   = SavedJob.query.filter_by(user_id=user_id, job_id=job_id).first()
    if not saved:
        return error("Saved job not found", 404)

    db.session.delete(saved)
    db.session.commit()
    return success(message="Job removed from saved")
