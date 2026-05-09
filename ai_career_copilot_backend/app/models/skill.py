import uuid
from app.extensions import db


class Skill(db.Model):
    __tablename__ = "skills"

    id         = db.Column(db.String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = db.Column(db.String(36),  db.ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    name       = db.Column(db.String(100), nullable=False)
    category   = db.Column(db.String(50),  nullable=True)
    # categories: technical | soft | domain | tool

    profile = db.relationship("UserProfile", back_populates="skills")

    def to_dict(self):
        return {
            "id":       self.id,
            "name":     self.name,
            "category": self.category,
        }

    def __repr__(self):
        return f"<Skill {self.name}>"
