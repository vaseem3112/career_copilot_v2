"""
Creates and stores notifications.
Called from tasks and API routes — never directly from models.
"""
from app.extensions          import db
from app.models.notification import Notification
from app.models.settings     import UserSettings


def notify(user_id: str, message: str, type: str = "system") -> Notification:
    """
    Create a notification for a user.
    Respects their notification preferences from settings.
    """
    settings = UserSettings.query.filter_by(user_id=user_id).first()

    # ── Check preferences before creating ──
    if settings:
        if type == "job_match"     and not settings.notif_job_alerts:        return None
        if type == "analysis_done" and not settings.notif_analysis_complete: return None

    notif = Notification.create(user_id=user_id, message=message, type=type)
    db.session.add(notif)
    db.session.commit()
    return notif


def notify_job_matches(user_id: str, count: int) -> None:
    if count <= 0:
        return
    msg = f"🎯 Found {count} new job matches based on your profile!"
    notify(user_id, msg, type="job_match")


def notify_analysis_done(user_id: str, filename: str, probability: int) -> None:
    msg = (
        f"✅ Resume '{filename}' analyzed. "
        f"Your shortlist probability: {probability}%"
    )
    notify(user_id, msg, type="analysis_done")


def notify_profile_reminder(user_id: str, completion: int) -> None:
    msg = (
        f"📋 Your profile is {completion}% complete. "
        f"Complete it to get better job matches!"
    )
    notify(user_id, msg, type="profile_reminder")


def notify_welcome(user_id: str, name: str) -> None:
    msg = f"👋 Welcome to CareerCopilot, {name}! Start by uploading your resume."
    notify(user_id, msg, type="welcome")
