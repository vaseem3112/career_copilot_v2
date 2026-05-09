import uuid
from datetime import datetime, timezone, timedelta
from app.extensions import db


class OTPToken(db.Model):
    __tablename__ = "otp_tokens"

    id         = db.Column(db.String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id    = db.Column(db.String(36),  db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    code       = db.Column(db.String(10),  nullable=False)
    purpose    = db.Column(db.String(50),  nullable=False, default="email_verification")
    # purposes: email_verification | password_reset
    is_used    = db.Column(db.Boolean,     default=False,  nullable=False)
    expires_at = db.Column(db.DateTime,    nullable=False)
    created_at = db.Column(db.DateTime,    default=lambda: datetime.now(timezone.utc))

    # ── Relationship ──
    user = db.relationship("User", back_populates="otp_tokens")

    @classmethod
    def create(cls, user_id: str, code: str, purpose: str = "email_verification", expires_minutes: int = 10):
        return cls(
            user_id    = user_id,
            code       = code,
            purpose    = purpose,
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes),
        )

    def is_valid(self) -> bool:
        """Returns True if OTP is not used and not expired."""
        return (
            not self.is_used
            and datetime.now(timezone.utc) < self.expires_at.replace(tzinfo=timezone.utc)
        )

    def mark_used(self):
        self.is_used = True
        db.session.commit()

    def __repr__(self):
        return f"<OTPToken user={self.user_id} purpose={self.purpose} used={self.is_used}>"
