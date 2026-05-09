from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.profile  import UserProfile
from app.models.resume   import Resume
from app.models.analysis import ResumeAnalysis
from app.models.match    import JobMatch
from app.models.notification import Notification
from app.utils.response  import success

dashboard_bp = Blueprint("dashboard", __name__)


# ─────────────────────────────────────────
# GET /api/v1/dashboard/stats
# ─────────────────────────────────────────
@dashboard_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_stats():
    user_id = get_jwt_identity()

    # ── Profile score ──
    profile      = UserProfile.query.filter_by(user_id=user_id).first()
    profile_score = profile.completion_score() if profile else 0

    # ── Latest analyzed resume ──
    latest_resume = (
        Resume.query
        .filter_by(user_id=user_id, type="uploaded", status="analyzed")
        .order_by(Resume.created_at.desc())
        .first()
    )

    ats_score          = latest_resume.ats_score or 0 if latest_resume else 0
    shortlist_chance   = 0
    resume_health      = None
    suggested_roles    = []

    # ── Pull analysis data ──
    if latest_resume:
        analysis = ResumeAnalysis.query.filter_by(resume_id=latest_resume.id).first()
        if analysis:
            shortlist_chance = analysis.shortlist_probability or 0

            # Top 3 improvement suggestions for resume health card
            weaknesses = analysis.weaknesses[:3] if analysis.weaknesses else []
            resume_health = {
                "atsScore":     ats_score,
                "improvements": weaknesses,
            }

            # Suggested roles for dashboard
            for role in (analysis.suggested_roles or [])[:5]:
                suggested_roles.append({
                    "name":  role.get("role", ""),
                    "score": role.get("match_score", 0),
                })

    # ── Job matches count + top 3 ──
    top_matches = (
        JobMatch.query
        .filter_by(user_id=user_id)
        .order_by(JobMatch.match_score.desc())
        .limit(3)
        .all()
    )
    job_matches_count = JobMatch.query.filter_by(user_id=user_id).count()

    recent_jobs = []
    for m in top_matches:
        if m.job:
            recent_jobs.append({
                "title":    m.job.title,
                "company":  m.job.company,
                "location": m.job.location,
                "score":    m.match_score,
            })

    # ── Recent activity (last 5 notifications) ──
    notifications = (
        Notification.query
        .filter_by(user_id=user_id)
        .order_by(Notification.created_at.desc())
        .limit(5)
        .all()
    )
    recent_activity = [
        {"text": n.message, "time": n._time_ago()}
        for n in notifications
    ]

    return success({
        "stats": {
            "profile_score":    profile_score,
            "ats_score":        ats_score,
            "job_matches":      job_matches_count,
            "shortlist_chance": shortlist_chance,
            "recent_jobs":      recent_jobs,
            "suggested_roles":  suggested_roles,
            "resume_health":    resume_health,
            "recent_activity":  recent_activity,
        }
    })
