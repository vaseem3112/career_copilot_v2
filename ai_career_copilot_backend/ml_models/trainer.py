"""
Train shortlist probability ML model on real feature vectors.
Run this once you have enough user data.

Usage:
    cd ai_career_copilot_backend
    python ml_models/trainer.py
"""
import os
import sys
import numpy as np
import joblib
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# ── Bootstrap Flask app context ──
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from run import app

MODEL_PATH = "ml_models/shortlist_model.pkl"


def generate_synthetic_training_data(n: int = 1000):
    """
    Generate synthetic training data based on realistic distributions.
    Replace this with real labeled data when available.

    Features: [skill_overlap, exp_years, level_match, has_edu, skill_count, density]
    Label:    1 = shortlisted, 0 = not shortlisted
    """
    rng = np.random.default_rng(42)
    X, y = [], []

    for _ in range(n):
        skill_overlap = rng.beta(2, 3)
        exp_years     = rng.beta(2, 5)
        level_match   = rng.choice([0.0, 0.5, 1.0])
        has_edu       = rng.choice([0.0, 1.0], p=[0.2, 0.8])
        skill_count   = rng.beta(3, 4)
        density       = rng.beta(2, 4)

        features = [skill_overlap, exp_years, level_match, has_edu, skill_count, density]

        # Label: higher overlap + experience = more likely shortlisted
        score = (
            0.40 * skill_overlap +
            0.25 * exp_years     +
            0.15 * level_match   +
            0.10 * has_edu       +
            0.10 * density
        )
        label = 1 if score > 0.40 + rng.normal(0, 0.08) else 0

        X.append(features)
        y.append(label)

    return np.array(X), np.array(y)


def train():
    print("Generating training data...")
    X, y = generate_synthetic_training_data(2000)
    print(f"Dataset: {X.shape[0]} samples, {y.sum()} positive ({y.mean():.1%})")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training GradientBoostingClassifier...")
    model = GradientBoostingClassifier(
        n_estimators   = 200,
        max_depth      = 4,
        learning_rate  = 0.05,
        min_samples_leaf = 10,
        random_state   = 42,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"\n✅ Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    with app.app_context():
        train()
