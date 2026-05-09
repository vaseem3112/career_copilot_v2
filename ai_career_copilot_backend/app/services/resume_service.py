"""
Resume orchestration — list, version management, delete.
"""
import os
from app.extensions    import db
from app.models.resume import Resume


def get_user_resumes(user_id: str) -> list:
    resumes = (
        Resume.query
        .filter_by(user_id=user_id)
        .order_by(Resume.created_at.desc())
        .all()
    )
    return [r.to_dict() for r in resumes]


def delete_resume(resume_id: str, user_id: str) -> bool:
    resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
    if not resume:
        return False

    # Remove file from disk
    try:
        if resume.filepath and os.path.exists(resume.filepath):
            os.remove(resume.filepath)
    except Exception:
        pass

    db.session.delete(resume)
    db.session.commit()
    return True


def get_latest_resume(user_id: str, type: str = "uploaded") -> Resume | None:
    return (
        Resume.query
        .filter_by(user_id=user_id, type=type, status="analyzed")
        .order_by(Resume.created_at.desc())
        .first()
    )
