import uuid
from datetime import datetime, timezone
from app.extensions import db
import bcrypt


class User(db.Model):
    __tablename__ = "users"

    id            = db.Column(db.String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    name          = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_verified   = db.Column(db.Boolean,     default=False,  nullable=False)
    is_active     = db.Column(db.Boolean,     default=True,   nullable=False)
    created_at    = db.Column(db.DateTime,    default=lambda: datetime.now(timezone.utc))
    updated_at    = db.Column(db.DateTime,    default=lambda: datetime.now(timezone.utc),
                              onupdate=lambda: datetime.now(timezone.utc))
    last_login    = db.Column(db.DateTime,    nullable=True)

    # ── Relationships ──
    profile       = db.relationship("UserProfile",   back_populates="user", uselist=False, cascade="all, delete-orphan")
    resumes       = db.relationship("Resume",        back_populates="user", cascade="all, delete-orphan")
    otp_tokens    = db.relationship("OTPToken",      back_populates="user", cascade="all, delete-orphan")
    notifications = db.relationship("Notification",  back_populates="user", cascade="all, delete-orphan")
    settings      = db.relationship("UserSettings",  back_populates="user", uselist=False, cascade="all, delete-orphan")
    saved_jobs    = db.relationship("SavedJob",      back_populates="user", cascade="all, delete-orphan")
    job_matches   = db.relationship("JobMatch",      back_populates="user", cascade="all, delete-orphan")

    # ── Password helpers ──
    def set_password(self, raw: str):
        self.password_hash = bcrypt.hashpw(raw.encode(), bcrypt.gensalt()).decode()

    def check_password(self, raw: str) -> bool:
        return bcrypt.checkpw(raw.encode(), self.password_hash.encode())

    def update_last_login(self):
        self.last_login = datetime.now(timezone.utc)
        db.session.commit()

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "name":        self.name,
            "email":       self.email,
            "is_verified": self.is_verified,
            "created_at":  self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<User {self.email}>"
