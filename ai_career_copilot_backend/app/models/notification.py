import uuid
from datetime import datetime, timezone
from app.extensions import db


class Notification(db.Model):
    __tablename__ = "notifications"

    id         = db.Column(db.String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id    = db.Column(db.String(36),  db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    message    = db.Column(db.String(500), nullable=False)
    type       = db.Column(db.String(50),  nullable=True)
    # types: job_match | analysis_done | profile_reminder | welcome | system
    is_read    = db.Column(db.Boolean,     default=False)
    created_at = db.Column(db.DateTime,    default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="notifications")

    @classmethod
    def create(cls, user_id: str, message: str, type: str = "system"):
        return cls(user_id=user_id, message=message, type=type)

    def to_dict(self) -> dict:
        return {
            "id":         self.id,
            "message":    self.message,
            "type":       self.type,
            "read":       self.is_read,
            "created_at": self._time_ago(),
        }

    def _time_ago(self) -> str:
        if not self.created_at:
            return ""
        delta = datetime.now(timezone.utc) - self.created_at.replace(tzinfo=timezone.utc)
        s = int(delta.total_seconds())
        if s < 60:    return "just now"
        if s < 3600:  return f"{s // 60}m ago"
        if s < 86400: return f"{s // 3600}h ago"
        return f"{s // 86400}d ago"

    def __repr__(self):
        return f"<Notification user={self.user_id} type={self.type}>"
