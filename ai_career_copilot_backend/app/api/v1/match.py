from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.match    import JobMatch
from app.models.profile  import UserProfile
from app.utils.response  import success, error
from app.tasks.match_task import run_job_matching

match_bp = Blueprint("match", __name__)


# ─────────────────────────────────────────
# GET /api/v1/match/jobs
# Returns pre-computed matched jobs for the user
# ─────────────────────────────────────────
@match_bp.route("/jobs", methods=["GET"])
@jwt_required()
def get_matched_jobs():
    user_id = get_jwt_identity()

    # ── Check profile exists ──
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not profile or not profile.skills_raw:
        return success(
            {"jobs": []},
            message="Complete your profile to get job matches"
        )

    # ── Fetch stored matches ──
    matches = (
        JobMatch.query
        .filter_by(user_id=user_id)
        .order_by(JobMatch.match_score.desc())
        .limit(50)
        .all()
    )

    # ── If no matches yet, trigger matching async ──
    if not matches:
        try:
            run_job_matching.delay(user_id)
        except Exception:
            pass
        return success(
            {"jobs": [], "status": "matching_started"},
            message="Job matching started. Check back shortly."
        )

    jobs_data = []
    for m in matches:
        if m.job and m.job.is_active:
            d          = m.job.to_dict(match_score=m.match_score)
            d["reason"] = m.reason
            jobs_data.append(d)

    return success({"jobs": jobs_data, "total": len(jobs_data)})
