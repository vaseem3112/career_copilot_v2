import uuid
import json
from datetime import datetime, timezone
from app.extensions import db


class ResumeAnalysis(db.Model):
    __tablename__ = "resume_analysis"

    id            = db.Column(db.String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id     = db.Column(db.String(36),  db.ForeignKey("resumes.id", ondelete="CASCADE"),
                              unique=True, nullable=False, index=True)
    user_id       = db.Column(db.String(36),  db.ForeignKey("users.id",   ondelete="CASCADE"),
                              nullable=False, index=True)

    # ── Core AI output stored as JSON strings ──
    profile_summary         = db.Column(db.Text,    nullable=True)
    experience_level        = db.Column(db.String(30), nullable=True)  # fresher|junior|mid|senior

    skills_json             = db.Column(db.Text,    nullable=True)  # list[str]
    domains_json            = db.Column(db.Text,    nullable=True)  # list[str]
    suggested_roles_json    = db.Column(db.Text,    nullable=True)  # list[{role, match_score, reason}]

    # ── Resume analysis ──
    strengths_json          = db.Column(db.Text,    nullable=True)  # list[str]
    weaknesses_json         = db.Column(db.Text,    nullable=True)  # list[str]
    missing_skills_json     = db.Column(db.Text,    nullable=True)  # list[str]

    # ── Skill gap ──
    matched_skills_json     = db.Column(db.Text,    nullable=True)  # list[str]
    gap_skills_json         = db.Column(db.Text,    nullable=True)  # list[str]
    suggestions_json        = db.Column(db.Text,    nullable=True)  # list[str]

    # ── ATS resume ──
    ats_resume_text         = db.Column(db.Text,    nullable=True)

    # ── Shortlist probability — computed by ML model, not AI ──
    shortlist_probability   = db.Column(db.Integer, nullable=True)  # 0-100

    created_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                            onupdate=lambda: datetime.now(timezone.utc))

    # ── Relationship ──
    resume = db.relationship("Resume", back_populates="analysis")

    # ── JSON helpers ──
    def _load(self, field): return json.loads(field) if field else []
    def _dump(self, val):   return json.dumps(val)

    @property
    def skills(self):             return self._load(self.skills_json)
    @skills.setter
    def skills(self, v):          self.skills_json = self._dump(v)

    @property
    def domains(self):            return self._load(self.domains_json)
    @domains.setter
    def domains(self, v):         self.domains_json = self._dump(v)

    @property
    def suggested_roles(self):    return self._load(self.suggested_roles_json)
    @suggested_roles.setter
    def suggested_roles(self, v): self.suggested_roles_json = self._dump(v)

    @property
    def strengths(self):          return self._load(self.strengths_json)
    @strengths.setter
    def strengths(self, v):       self.strengths_json = self._dump(v)

    @property
    def weaknesses(self):         return self._load(self.weaknesses_json)
    @weaknesses.setter
    def weaknesses(self, v):      self.weaknesses_json = self._dump(v)

    @property
    def missing_skills(self):     return self._load(self.missing_skills_json)
    @missing_skills.setter
    def missing_skills(self, v):  self.missing_skills_json = self._dump(v)

    @property
    def matched_skills(self):     return self._load(self.matched_skills_json)
    @matched_skills.setter
    def matched_skills(self, v):  self.matched_skills_json = self._dump(v)

    @property
    def gap_skills(self):         return self._load(self.gap_skills_json)
    @gap_skills.setter
    def gap_skills(self, v):      self.gap_skills_json = self._dump(v)

    @property
    def suggestions(self):        return self._load(self.suggestions_json)
    @suggestions.setter
    def suggestions(self, v):     self.suggestions_json = self._dump(v)

    def to_dict(self) -> dict:
        return {
            "id":                   self.id,
            "resume_id":            self.resume_id,
            "profile_summary":      self.profile_summary,
            "experience_level":     self.experience_level,
            "skills":               self.skills,
            "domains":              self.domains,
            "suggested_roles":      self.suggested_roles,
            "resume_analysis": {
                "strengths":        self.strengths,
                "weaknesses":       self.weaknesses,
                "missing_skills":   self.missing_skills,
            },
            "skill_gap": {
                "matched":          self.matched_skills,
                "missing":          self.gap_skills,
                "suggestions":      self.suggestions,
            },
            "ats_resume":           self.ats_resume_text,
            "shortlist_probability": self.shortlist_probability,
        }

    def __repr__(self):
        return f"<ResumeAnalysis resume_id={self.resume_id}>"
