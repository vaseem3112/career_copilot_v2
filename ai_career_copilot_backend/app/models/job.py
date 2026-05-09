import uuid
from datetime import datetime, timezone
from app.extensions import db


class JobSource(db.Model):
    __tablename__ = "job_sources"

    id         = db.Column(db.String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    name       = db.Column(db.String(100), unique=True, nullable=False)
    # e.g. adzuna | jsearch | remoteok
    is_active  = db.Column(db.Boolean,    default=True)
    last_fetch = db.Column(db.DateTime,   nullable=True)

    jobs = db.relationship("Job", back_populates="source")

    def __repr__(self):
        return f"<JobSource {self.name}>"


class Job(db.Model):
    __tablename__ = "jobs"

    id               = db.Column(db.String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id        = db.Column(db.String(36),  db.ForeignKey("job_sources.id"), nullable=True)
    external_id      = db.Column(db.String(255), nullable=True, index=True)
    # external_id = ID from Adzuna/JSearch to avoid duplicates

    # ── Core fields ──
    title            = db.Column(db.String(255), nullable=False)
    company          = db.Column(db.String(200), nullable=True)
    location         = db.Column(db.String(200), nullable=True)
    salary_min       = db.Column(db.Integer,     nullable=True)
    salary_max       = db.Column(db.Integer,     nullable=True)
    salary_display   = db.Column(db.String(100), nullable=True)
    job_type         = db.Column(db.String(50),  nullable=True)  # full-time|part-time|contract|remote
    domain           = db.Column(db.String(100), nullable=True)
    experience_level = db.Column(db.String(50),  nullable=True)  # fresher|junior|mid|senior

    # ── Full content ──
    description      = db.Column(db.Text,        nullable=True)
    requirements_raw = db.Column(db.Text,        nullable=True)  # newline-separated
    apply_url        = db.Column(db.String(500), nullable=True)

    # ── Embedding for similarity matching ──
    embedding_json   = db.Column(db.Text,        nullable=True)

    # ── Meta ──
    posted_at        = db.Column(db.DateTime,    nullable=True)
    fetched_at       = db.Column(db.DateTime,    default=lambda: datetime.now(timezone.utc))
    is_active        = db.Column(db.Boolean,     default=True)

    # ── Relationships ──
    source      = db.relationship("JobSource",  back_populates="jobs")
    saved_by    = db.relationship("SavedJob",   back_populates="job", cascade="all, delete-orphan")
    matches     = db.relationship("JobMatch",   back_populates="job", cascade="all, delete-orphan")

    @property
    def requirements(self):
        if not self.requirements_raw:
            return []
        return [r.strip() for r in self.requirements_raw.split("\n") if r.strip()]

    @requirements.setter
    def requirements(self, lst):
        self.requirements_raw = "\n".join(lst) if lst else ""

    def salary_string(self) -> str:
        if self.salary_display:
            return self.salary_display
        if self.salary_min and self.salary_max:
            return f"₹{self.salary_min:,} – ₹{self.salary_max:,}"
        return ""

    def to_dict(self, match_score: int = None) -> dict:
        return {
            "id":              self.id,
            "title":           self.title,
            "company":         self.company,
            "location":        self.location,
            "salary":          self.salary_string(),
            "type":            self.job_type,
            "domain":          self.domain,
            "experience":      self.experience_level,
            "description":     self.description,
            "requirements":    self.requirements,
            "applyUrl":        self.apply_url,
            "posted":          self.posted_at.strftime("%b %d, %Y") if self.posted_at else None,
            "matchScore":      match_score,
        }

    def __repr__(self):
        return f"<Job {self.title} @ {self.company}>"
