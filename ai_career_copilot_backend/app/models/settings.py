import uuid
import json
from datetime import datetime, timezone
from app.extensions import db


class UserSettings(db.Model):
    __tablename__ = "user_settings"

    id      = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"),
                        unique=True, nullable=False)

    # ── Notification toggles ──
    notif_job_alerts        = db.Column(db.Boolean, default=True)
    notif_analysis_complete = db.Column(db.Boolean, default=True)
    notif_weekly_digest     = db.Column(db.Boolean, default=False)
    notif_product_updates   = db.Column(db.Boolean, default=False)

    # ── Privacy ──
    visible_to_recruiters   = db.Column(db.Boolean, default=False)
    allow_data_use          = db.Column(db.Boolean, default=True)

    # ── Additional phone (settings-level) ──
    phone                   = db.Column(db.String(30), nullable=True)

    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="settings")

    @classmethod
    def get_or_create(cls, user_id: str):
        """Get existing settings or create defaults."""
        s = cls.query.filter_by(user_id=user_id).first()
        if not s:
            s = cls(user_id=user_id)
            db.session.add(s)
            db.session.commit()
        return s

    def to_dict(self) -> dict:
        return {
            "notifications": {
                "jobAlerts":        self.notif_job_alerts,
                "analysisComplete": self.notif_analysis_complete,
                "weeklyDigest":     self.notif_weekly_digest,
                "productUpdates":   self.notif_product_updates,
            },
            "privacy": {
                "visibleToRecruiters": self.visible_to_recruiters,
                "allowDataUse":        self.allow_data_use,
            },
            "phone": self.phone,
        }

    def __repr__(self):
        return f"<UserSettings user_id={self.user_id}>"
