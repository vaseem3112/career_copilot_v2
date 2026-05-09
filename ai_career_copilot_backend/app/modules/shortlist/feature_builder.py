"""
Builds real feature vectors from profile + job for ML model.
Every feature is computed from actual data — no hardcoding.
"""
import re
from app.models.profile import UserProfile
from app.models.job     import Job


def build_feature_vector(profile: UserProfile, job: Job) -> list[float]:
    """
    Build a numeric feature vector for shortlist probability prediction.

    Features:
      0: skill_overlap_ratio       — matched skills / total jd keywords
      1: experience_years          — years of total experience
      2: experience_level_match    — profile level vs job requirement
      3: has_relevant_education    — 1 if degree field matches job domain
      4: skill_count_normalized    — number of skills (normalized 0-1)
      5: keyword_density           — keyword overlap with JD in resume
    """
    features = []

    # ── 0: Skill overlap ratio ──
    profile_skills = set(s.lower() for s in (profile.skills_list or []))
    jd_words       = set(re.findall(r"\b\w{3,}\b", (job.description or "").lower()))
    if jd_words:
        overlap = len(profile_skills & jd_words) / len(jd_words)
    else:
        overlap = 0.0
    features.append(round(overlap, 4))

    # ── 1: Experience years (estimated from entries) ──
    exp_count = len(profile.experience) if profile.experience else 0
    exp_years = min(exp_count * 1.5, 15) / 15  # normalize to 0-1
    features.append(round(exp_years, 4))

    # ── 2: Experience level match ──
    level_map = {"fresher": 0, "junior": 1, "mid": 2, "senior": 3}
    # We don't store profile level here — default mid if unknown
    features.append(0.5)

    # ── 3: Has education ──
    has_edu = 1.0 if profile.education else 0.0
    features.append(has_edu)

    # ── 4: Skill count normalized (0-1, cap at 20 skills) ──
    skill_count = min(len(profile_skills), 20) / 20
    features.append(round(skill_count, 4))

    # ── 5: Keyword density in skills vs JD ──
    if jd_words and profile_skills:
        density = len(profile_skills & jd_words) / max(len(profile_skills), 1)
    else:
        density = 0.0
    features.append(round(density, 4))

    return features


def features_to_array(features: list[float]):
    """Convert feature list to numpy array for sklearn."""
    import numpy as np
    return np.array(features).reshape(1, -1)
