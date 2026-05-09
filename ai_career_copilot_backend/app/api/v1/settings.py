import json
from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions      import db
from app.models.settings import UserSettings
from app.models.user     import User
from app.models.profile  import UserProfile
from app.models.resume   import Resume
from app.models.analysis import ResumeAnalysis
from app.models.match    import JobMatch
from app.models.notification import Notification
from app.utils.response  import success, error
from app.utils.validators import is_strong_password

settings_bp = Blueprint("settings", __name__)


# ─────────────────────────────────────────
# GET /api/v1/settings
# ─────────────────────────────────────────
@settings_bp.route("", methods=["GET"])
@jwt_required()
def get_settings():
    user_id  = get_jwt_identity()
    settings = UserSettings.get_or_create(user_id)
    return success({"settings": settings.to_dict()})


# ─────────────────────────────────────────
# PATCH /api/v1/settings
# ─────────────────────────────────────────
@settings_bp.route("", methods=["PATCH"])
@jwt_required()
def update_settings():
    user_id  = get_jwt_identity()
    data     = request.get_json(silent=True) or {}
    settings = UserSettings.get_or_create(user_id)

    # ── Notification toggles ──
    notifs = data.get("notifications", {})
    if "jobAlerts"        in notifs: settings.notif_job_alerts        = bool(notifs["jobAlerts"])
    if "analysisComplete" in notifs: settings.notif_analysis_complete = bool(notifs["analysisComplete"])
    if "weeklyDigest"     in notifs: settings.notif_weekly_digest     = bool(notifs["weeklyDigest"])
    if "productUpdates"   in notifs: settings.notif_product_updates   = bool(notifs["productUpdates"])

    # ── Privacy ──
    privacy = data.get("privacy", {})
    if "visibleToRecruiters" in privacy: settings.visible_to_recruiters = bool(privacy["visibleToRecruiters"])
    if "allowDataUse"        in privacy: settings.allow_data_use        = bool(privacy["allowDataUse"])

    # ── Account fields ──
    user = User.query.get(user_id)
    if user:
        if "name"  in data: user.name  = data["name"].strip()
        if "email" in data: user.email = data["email"].strip().lower()
    if "phone" in data: settings.phone = data["phone"]

    db.session.commit()
    return success({"settings": settings.to_dict()}, message="Settings saved")


# ─────────────────────────────────────────
# PATCH /api/v1/settings/password
# ─────────────────────────────────────────
@settings_bp.route("/password", methods=["PATCH"])
@jwt_required()
def change_password():
    user_id  = get_jwt_identity()
    data     = request.get_json(silent=True) or {}
    current  = data.get("current_password", "")
    new_pwd  = data.get("new_password", "")

    if not current or not new_pwd:
        return error("current_password and new_password are required", 400)

    if not is_strong_password(new_pwd):
        return error("New password must be at least 8 characters", 400)

    user = User.query.get(user_id)
    if not user:
        return error("User not found", 404)

    if not user.check_password(current):
        return error("Current password is incorrect", 401)

    user.set_password(new_pwd)
    db.session.commit()
    return success(message="Password changed successfully")


# ─────────────────────────────────────────
# GET /api/v1/settings/export
# Returns all user data as JSON for download
# ─────────────────────────────────────────
@settings_bp.route("/export", methods=["GET"])
@jwt_required()
def export_data():
    user_id = get_jwt_identity()
    user    = User.query.get(user_id)
    if not user:
        return error("User not found", 404)

    profile  = UserProfile.query.filter_by(user_id=user_id).first()
    resumes  = Resume.query.filter_by(user_id=user_id).all()
    analyses = ResumeAnalysis.query.filter_by(user_id=user_id).all()
    matches  = JobMatch.query.filter_by(user_id=user_id).all()

    export = {
        "user":     user.to_dict(),
        "profile":  profile.to_dict() if profile else None,
        "resumes":  [r.to_dict() for r in resumes],
        "analyses": [a.to_dict() for a in analyses],
        "matches":  [{"job_id": m.job_id, "score": m.match_score} for m in matches],
    }

    from flask import Response
    return Response(
        json.dumps(export, indent=2),
        mimetype    = "application/json",
        headers     = {"Content-Disposition": "attachment; filename=careercopilot_data.json"},
    )
