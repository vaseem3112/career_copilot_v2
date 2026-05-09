import uuid
from datetime import datetime, timezone
from app.extensions import db


class Resume(db.Model):
    __tablename__ = "resumes"

    id          = db.Column(db.String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id     = db.Column(db.String(36),  db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    filename    = db.Column(db.String(255), nullable=False)
    filepath    = db.Column(db.String(500), nullable=False)       # path on disk / S3 key
    file_type   = db.Column(db.String(10),  nullable=False)       # pdf | doc | docx
    file_size   = db.Column(db.Integer,     nullable=True)        # bytes

    type        = db.Column(db.String(20),  nullable=False, default="uploaded")
    # type: uploaded | generated

    status      = db.Column(db.String(30),  nullable=False, default="pending")
    # status: pending | processing | analyzed | failed

    raw_text    = db.Column(db.Text,        nullable=True)        # extracted text
    ats_score   = db.Column(db.Integer,     nullable=True)        # 0-100
    version     = db.Column(db.Integer,     default=1)

    created_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                            onupdate=lambda: datetime.now(timezone.utc))

    # ── Relationships ──
    user     = db.relationship("User",           back_populates="resumes")
    analysis = db.relationship("ResumeAnalysis", back_populates="resume",
                               uselist=False, cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "filename":    self.filename,
            "type":        self.type,
            "status":      self.status,
            "atsScore":    self.ats_score,
            "version":     self.version,
            "uploadedAt":  self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Resume {self.filename} ({self.type})>"
