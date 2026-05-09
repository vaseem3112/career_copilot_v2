"""
ML-based shortlist probability predictor.
Falls back to rule-based scoring if model not trained yet.
"""
import os
import joblib
from flask import current_app


def load_model():
    path = current_app.config.get("MODEL_PATH", "ml_models/shortlist_model.pkl")
    if not os.path.exists(path):
        return None
    return joblib.load(path)


def predict_probability(feature_vector: list[float]) -> int:
    """
    Predict shortlist probability from feature vector.
    Returns int 0-100.
    Falls back to rule-based if no trained model found.
    """
    model = load_model()

    if model:
        try:
            from app.modules.shortlist.feature_builder import features_to_array
            arr   = features_to_array(feature_vector)
            proba = model.predict_proba(arr)[0][1]  # probability of class 1
            score = max(20, min(90, int(proba * 100)))
            return score
        except Exception as e:
            current_app.logger.warning(f"ML model prediction failed: {e}")

    # ── Rule-based fallback ──
    return _rule_based_score(feature_vector)


def _rule_based_score(features: list[float]) -> int:
    """
    Simple weighted rule-based scoring when ML model not available.
    Uses feature vector: [skill_overlap, exp_years, level_match, has_edu, skill_count, density]
    """
    weights = [0.35, 0.25, 0.10, 0.10, 0.10, 0.10]
    score   = sum(f * w for f, w in zip(features, weights))

    # Map 0-1 score to 20-85 range (realistic distribution)
    final = int(20 + (score * 65))
    return max(20, min(85, final))
