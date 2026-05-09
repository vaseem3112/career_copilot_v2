import uuid
from datetime import datetime, timezone
from app.extensions import db


class JobMatch(db.Model):
    __tablename__ = "job_matches"

    id           = db.Column(db.String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id      = db.Column(db.String(36),  db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id       = db.Column(db.String(36),  db.ForeignKey("jobs.id",  ondelete="CASCADE"), nullable=False)
    resume_id    = db.Column(db.String(36),  db.ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True)

    match_score  = db.Column(db.Integer,     nullable=False)   # 0-100 cosine similarity score
    reason       = db.Column(db.Text,        nullable=True)    # short explanation
    computed_at  = db.Column(db.DateTime,    default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint("user_id", "job_id", name="uq_user_job_match"),
    )

    user = db.relationship("User", back_populates="job_matches")
    job  = db.relationship("Job",  back_populates="matches")

    def to_dict(self) -> dict:
        job_data = self.job.to_dict(match_score=self.match_score) if self.job else {}
        job_data["reason"] = self.reason
        return job_data

    def __repr__(self):
        return f"<JobMatch user={self.user_id} job={self.job_id} score={self.match_score}>"
