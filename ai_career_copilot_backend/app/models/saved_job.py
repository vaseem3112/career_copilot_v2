import uuid
from datetime import datetime, timezone
from app.extensions import db


class SavedJob(db.Model):
    __tablename__ = "saved_jobs"

    id         = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id    = db.Column(db.String(36), db.ForeignKey("users.id",  ondelete="CASCADE"), nullable=False)
    job_id     = db.Column(db.String(36), db.ForeignKey("jobs.id",   ondelete="CASCADE"), nullable=False)
    saved_at   = db.Column(db.DateTime,   default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint("user_id", "job_id", name="uq_user_saved_job"),
    )

    user = db.relationship("User", back_populates="saved_jobs")
    job  = db.relationship("Job",  back_populates="saved_by")

    def __repr__(self):
        return f"<SavedJob user={self.user_id} job={self.job_id}>"
