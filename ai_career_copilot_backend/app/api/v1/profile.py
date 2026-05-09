from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions       import db
from app.models.user      import User
from app.models.profile   import (
    UserProfile, Education, Experience, Certification, Project
)
from app.models.skill     import Skill
from app.utils.response   import success, error

profile_bp = Blueprint("profile", __name__)


def _get_or_create_profile(user_id: str) -> UserProfile:
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.session.add(profile)
        db.session.flush()
    return profile


# ─────────────────────────────────────────
# GET /api/v1/profile
# ─────────────────────────────────────────
@profile_bp.route("", methods=["GET","PUT"])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return success({"profile": None}, message="No profile yet")
    return success({"profile": profile.to_dict()})


# ─────────────────────────────────────────
# PATCH /api/v1/profile
# ─────────────────────────────────────────
@profile_bp.route("", methods=["PUT","PATCH"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user    = User.query.get(user_id)
    if not user:
        return error("User not found", 404)

    data    = request.get_json(silent=True) or {}
    profile = _get_or_create_profile(user_id)

    # ── Basic fields ──
    if "name"    in data: user.name       = data["name"].strip()
    if "phone"   in data: profile.phone   = data["phone"]
    if "city"    in data: profile.city    = data["city"]
    if "state"   in data: profile.state   = data["state"]
    if "country" in data: profile.country = data["country"]
    if "linkedin"in data: profile.linkedin= data["linkedin"]
    if "github"  in data: profile.github  = data["github"]
    if "summary" in data: profile.summary = data["summary"]

    # ── Skills ──
    if "skills" in data:
        raw_skills = data["skills"]
        if isinstance(raw_skills, list):
            profile.skills_list = [s.strip() for s in raw_skills if s.strip()]
            # Also sync skills table
            Skill.query.filter_by(profile_id=profile.id).delete()
            for sk in profile.skills_list:
                db.session.add(Skill(profile_id=profile.id, name=sk, category="technical"))
        elif isinstance(raw_skills, str):
            profile.skills_list = [s.strip() for s in raw_skills.split(",") if s.strip()]

    # ── Preferences ──
    if "preferred_roles"     in data:
        profile.preferred_roles     = data["preferred_roles"] if isinstance(data["preferred_roles"], list) else []
    if "preferred_locations" in data:
        profile.preferred_locations = data["preferred_locations"] if isinstance(data["preferred_locations"], list) else []
    if "salary_min"          in data: profile.salary_min = data["salary_min"]
    if "salary_max"          in data: profile.salary_max = data["salary_max"]

    # ── Education — full replace ──
    if "education" in data and isinstance(data["education"], list):
        Education.query.filter_by(profile_id=profile.id).delete()
        for edu in data["education"]:
            if any(edu.get(k) for k in ["degree", "institution", "field"]):
                db.session.add(Education(
                    profile_id  = profile.id,
                    degree      = edu.get("degree"),
                    field       = edu.get("field"),
                    institution = edu.get("institution"),
                    start_year  = edu.get("startYear") or edu.get("start_year"),
                    end_year    = edu.get("endYear")   or edu.get("end_year"),
                    grade       = edu.get("grade"),
                ))

    # ── Experience — full replace ──
    if "experience" in data and isinstance(data["experience"], list):
        Experience.query.filter_by(profile_id=profile.id).delete()
        for exp in data["experience"]:
            if any(exp.get(k) for k in ["title", "company"]):
                db.session.add(Experience(
                    profile_id  = profile.id,
                    title       = exp.get("title"),
                    company     = exp.get("company"),
                    start       = exp.get("start"),
                    end         = exp.get("end"),
                    current     = exp.get("current", False),
                    description = exp.get("description"),
                ))

    # ── Certifications — full replace ──
    if "certifications" in data and isinstance(data["certifications"], list):
        Certification.query.filter_by(profile_id=profile.id).delete()
        for cert in data["certifications"]:
            if cert.get("name"):
                db.session.add(Certification(
                    profile_id = profile.id,
                    name       = cert.get("name"),
                    issuer     = cert.get("issuer"),
                    year       = cert.get("year"),
                ))

    # ── Projects — full replace ──
    if "projects" in data and isinstance(data["projects"], list):
        Project.query.filter_by(profile_id=profile.id).delete()
        for proj in data["projects"]:
            if proj.get("name"):
                db.session.add(Project(
                    profile_id  = profile.id,
                    name        = proj.get("name"),
                    description = proj.get("description"),
                    stack       = proj.get("stack"),
                    link        = proj.get("link"),
                ))

    db.session.commit()

    # ── Trigger async re-matching after profile update ──
    try:
        from app.tasks.match_task import run_job_matching
        run_job_matching.delay(user_id)
    except Exception:
        pass

    return success({"profile": profile.to_dict()}, message="Profile updated")


# ─────────────────────────────────────────
# GET /api/v1/profile/completion
# ─────────────────────────────────────────
@profile_bp.route("/completion", methods=["GET"])
@jwt_required()
def get_completion():
    user_id = get_jwt_identity()
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    score   = profile.completion_score() if profile else 0
    return success({
        "completion_score": score,
        "score":            score,
    })
