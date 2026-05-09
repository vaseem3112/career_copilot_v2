from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions          import db
from app.models.notification import Notification
from app.utils.response      import success, error

notifications_bp = Blueprint("notifications", __name__)


# ─────────────────────────────────────────
# GET /api/v1/notifications
# ─────────────────────────────────────────
@notifications_bp.route("", methods=["GET"])
@jwt_required()
def list_notifications():
    user_id = get_jwt_identity()
    notifs  = (
        Notification.query
        .filter_by(user_id=user_id)
        .order_by(Notification.created_at.desc())
        .limit(30)
        .all()
    )
    return success({
        "notifications": [n.to_dict() for n in notifs],
        "unread":        sum(1 for n in notifs if not n.is_read),
    })


# ─────────────────────────────────────────
# PATCH /api/v1/notifications/<id>/read
# ─────────────────────────────────────────
@notifications_bp.route("/<notif_id>/read", methods=["PATCH"])
@jwt_required()
def mark_read(notif_id: str):
    user_id = get_jwt_identity()
    notif   = Notification.query.filter_by(id=notif_id, user_id=user_id).first()
    if not notif:
        return error("Notification not found", 404)

    notif.is_read = True
    db.session.commit()
    return success(message="Marked as read")


# ─────────────────────────────────────────
# PATCH /api/v1/notifications/read-all
# ─────────────────────────────────────────
@notifications_bp.route("/read-all", methods=["PATCH"])
@jwt_required()
def mark_all_read():
    user_id = get_jwt_identity()
    Notification.query.filter_by(user_id=user_id, is_read=False).update({"is_read": True})
    db.session.commit()
    return success(message="All notifications marked as read")
