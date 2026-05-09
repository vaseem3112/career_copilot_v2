import uuid
from datetime import datetime, timezone
from app.extensions import db


class Education(db.Model):
    __tablename__ = "education"

    id           = db.Column(db.String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id   = db.Column(db.String(36),  db.ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    degree       = db.Column(db.String(120), nullable=True)
    field        = db.Column(db.String(120), nullable=True)
    institution  = db.Column(db.String(200), nullable=True)
    start_year   = db.Column(db.String(10),  nullable=True)
    end_year     = db.Column(db.String(10),  nullable=True)
    grade        = db.Column(db.String(20),  nullable=True)

    profile = db.relationship("UserProfile", back_populates="education")

    def to_dict(self):
        return {
            "id":          self.id,
            "degree":      self.degree,
            "field":       self.field,
            "institution": self.institution,
            "startYear":   self.start_year,
            "endYear":     self.end_year,
            "grade":       self.grade,
        }


class Experience(db.Model):
    __tablename__ = "experience"

    id          = db.Column(db.String(36),   primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id  = db.Column(db.String(36),   db.ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    title       = db.Column(db.String(150),  nullable=True)
    company     = db.Column(db.String(150),  nullable=True)
    start       = db.Column(db.String(20),   nullable=True)
    end         = db.Column(db.String(20),   nullable=True)
    current     = db.Column(db.Boolean,      default=False)
    description = db.Column(db.Text,         nullable=True)

    profile = db.relationship("UserProfile", back_populates="experience")

    def to_dict(self):
        return {
            "id":          self.id,
            "title":       self.title,
            "company":     self.company,
            "start":       self.start,
            "end":         self.end,
            "current":     self.current,
            "description": self.description,
        }


class UserProfile(db.Model):
    __tablename__ = "user_profiles"

    id                   = db.Column(db.String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id              = db.Column(db.String(36),  db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    # ── Basic ──
    phone                = db.Column(db.String(30),  nullable=True)
    city                 = db.Column(db.String(100), nullable=True)
    state                = db.Column(db.String(100), nullable=True)
    country              = db.Column(db.String(100), nullable=True)
    linkedin             = db.Column(db.String(255), nullable=True)
    github               = db.Column(db.String(255), nullable=True)
    summary              = db.Column(db.Text,        nullable=True)

    # ── Skills stored as comma-separated string ──
    skills_raw           = db.Column(db.Text,        nullable=True)

    # ── Preferences ──
    preferred_roles_raw      = db.Column(db.Text,    nullable=True)
    preferred_locations_raw  = db.Column(db.Text,    nullable=True)
    salary_min           = db.Column(db.Integer,     nullable=True)
    salary_max           = db.Column(db.Integer,     nullable=True)

    # ── Embedding vector stored as JSON string ──
    embedding_json       = db.Column(db.Text,        nullable=True)

    # ── Timestamps ──
    created_at           = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at           = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                                     onupdate=lambda: datetime.now(timezone.utc))

    # ── Relationships ──
    user            = db.relationship("User",       back_populates="profile")
    education       = db.relationship("Education",  back_populates="profile", cascade="all, delete-orphan")
    experience      = db.relationship("Experience", back_populates="profile", cascade="all, delete-orphan")
    skills          = db.relationship("Skill",      back_populates="profile", cascade="all, delete-orphan")
    certifications  = db.relationship("Certification", back_populates="profile", cascade="all, delete-orphan")
    projects        = db.relationship("Project",    back_populates="profile", cascade="all, delete-orphan")

    # ── Skill helpers ──
    @property
    def skills_list(self):
        return [s.strip() for s in self.skills_raw.split(",")] if self.skills_raw else []

    @skills_list.setter
    def skills_list(self, lst):
        self.skills_raw = ",".join(lst) if lst else ""

    @property
    def preferred_roles(self):
        return [r.strip() for r in self.preferred_roles_raw.split(",")] if self.preferred_roles_raw else []

    @preferred_roles.setter
    def preferred_roles(self, lst):
        self.preferred_roles_raw = ",".join(lst) if lst else ""

    @property
    def preferred_locations(self):
        return [l.strip() for l in self.preferred_locations_raw.split(",")] if self.preferred_locations_raw else []

    @preferred_locations.setter
    def preferred_locations(self, lst):
        self.preferred_locations_raw = ",".join(lst) if lst else ""

    def completion_score(self) -> int:
        """
        Calculate profile completion percentage.
        Weights are assigned per section importance.
        """
        score = 0
        if self.user and self.user.name:  score += 10
        if self.phone:                    score += 5
        if self.city:                     score += 5
        if self.summary:                  score += 10
        if self.skills_raw:               score += 20
        if self.education:                score += 15
        if self.experience:               score += 20
        if self.linkedin:                 score += 5
        if self.certifications:           score += 5
        if self.projects:                 score += 5
        return min(score, 100)

    def to_dict(self) -> dict:
        return {
            "id":                  self.id,
            "user_id":             self.user_id,
            "phone":               self.phone,
            "city":                self.city,
            "state":               self.state,
            "country":             self.country,
            "linkedin":            self.linkedin,
            "github":              self.github,
            "summary":             self.summary,
            "skills":              self.skills_list,
            "preferredRoles":      self.preferred_roles,
            "preferredLocations":  self.preferred_locations,
            "salaryMin":           self.salary_min,
            "salaryMax":           self.salary_max,
            "education":           [e.to_dict() for e in self.education],
            "experience":          [e.to_dict() for e in self.experience],
            "certifications":      [c.to_dict() for c in self.certifications],
            "projects":            [p.to_dict() for p in self.projects],
            "name":                self.user.name  if self.user else None,
            "email":               self.user.email if self.user else None,
        }

    def __repr__(self):
        return f"<UserProfile user_id={self.user_id}>"


class Certification(db.Model):
    __tablename__ = "certifications"

    id         = db.Column(db.String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = db.Column(db.String(36),  db.ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    name       = db.Column(db.String(200), nullable=True)
    issuer     = db.Column(db.String(200), nullable=True)
    year       = db.Column(db.String(10),  nullable=True)

    profile = db.relationship("UserProfile", back_populates="certifications")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "issuer": self.issuer, "year": self.year}


class Project(db.Model):
    __tablename__ = "projects"

    id          = db.Column(db.String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id  = db.Column(db.String(36),  db.ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    name        = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text,        nullable=True)
    stack       = db.Column(db.String(500), nullable=True)
    link        = db.Column(db.String(500), nullable=True)

    profile = db.relationship("UserProfile", back_populates="projects")

    def to_dict(self):
        return {
            "id":          self.id,
            "name":        self.name,
            "description": self.description,
            "stack":       self.stack,
            "link":        self.link,
        }
