from app.extensions import celery, db
from flask import current_app


@celery.task(bind=True, max_retries=2)
def run_job_matching(self, user_id: str):
    """
    Compute cosine similarity between user profile and all active jobs.
    Stores top matches in job_matches table.
    """
    from app.models.match   import JobMatch
    from app.models.notification import Notification
    from app.modules.matcher.similarity import match_profile_to_jobs

    try:
        matches = match_profile_to_jobs(user_id, top_n=50)

        if not matches:
            return

        # ── Upsert matches ──
        for m in matches:
            existing = JobMatch.query.filter_by(
                user_id = user_id,
                job_id  = m["job_id"],
            ).first()

            if existing:
                existing.match_score = m["score"]
                existing.reason      = m["reason"]
            else:
                db.session.add(JobMatch(
                    user_id     = user_id,
                    job_id      = m["job_id"],
                    match_score = m["score"],
                    reason      = m["reason"],
                ))

        db.session.commit()

        # ── Notify user of new matches ──
        high_matches = [m for m in matches if m["score"] >= 75]
        if high_matches:
            notif = Notification.create(
                user_id = user_id,
                message = f"Found {len(high_matches)} strong job matches for you!",
                type    = "job_match",
            )
            db.session.add(notif)
            db.session.commit()

        current_app.logger.info(f"Job matching done for user={user_id}: {len(matches)} matches")

    except Exception as exc:
        current_app.logger.error(f"Job matching failed for user={user_id}: {exc}")
        raise self.retry(exc=exc)
