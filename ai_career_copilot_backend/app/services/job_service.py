"""
Fetches live jobs from APIs, normalises, deduplicates and stores them.
"""
from datetime import datetime, timezone
from flask import current_app

from app.extensions import db
from app.models.job import Job, JobSource
from app.modules.matcher.job_fetcher import fetch_adzuna_jobs, fetch_jsearch_jobs
from app.modules.matcher.embedder    import embed_job, dump_vector


def fetch_and_store_jobs(query: str = "", location: str = "") -> int:
    """
    Fetch from all configured sources, deduplicate by external_id, store new jobs.
    Returns count of new jobs added.
    """
    sources = [
        ("adzuna",  lambda: fetch_adzuna_jobs(query, location)),
        ("jsearch", lambda: fetch_jsearch_jobs(query, location)),
    ]

    total_new = 0

    for source_name, fetcher in sources:
        source = _get_or_create_source(source_name)

        try:
            jobs_data = fetcher()
            current_app.logger.info(f"Fetched {len(jobs_data)} jobs from {source_name}")
        except Exception as e:
            current_app.logger.error(f"Fetch failed [{source_name}]: {e}")
            continue

        for jd in jobs_data:
            ext_id = str(jd.get("external_id", "")).strip()
            if not ext_id or not jd.get("title"):
                continue

            # Skip if already exists
            if Job.query.filter_by(external_id=ext_id).first():
                continue

            job = Job(
                source_id        = source.id,
                external_id      = ext_id,
                title            = jd["title"],
                company          = jd.get("company"),
                location         = jd.get("location"),
                description      = jd.get("description"),
                salary_min       = jd.get("salary_min"),
                salary_max       = jd.get("salary_max"),
                apply_url        = jd.get("apply_url"),
                job_type         = jd.get("job_type"),
            )

            # Parse posted_at
            posted_raw = jd.get("posted_at")
            if posted_raw:
                try:
                    job.posted_at = datetime.fromisoformat(
                        posted_raw.replace("Z", "+00:00")
                    )
                except Exception:
                    pass

            # Pre-compute embedding for faster matching later
            try:
                vec = embed_job(jd)
                job.embedding_json = dump_vector(vec)
            except Exception as e:
                current_app.logger.warning(f"Embedding failed for job {ext_id}: {e}")

            db.session.add(job)
            total_new += 1

        source.last_fetch = datetime.now(timezone.utc)

    db.session.commit()
    current_app.logger.info(f"Job fetch complete: {total_new} new jobs stored")
    return total_new


def _get_or_create_source(name: str) -> JobSource:
    source = JobSource.query.filter_by(name=name).first()
    if not source:
        source = JobSource(name=name)
        db.session.add(source)
        db.session.flush()
    return source


def paginate_jobs(
    page: int = 1,
    limit: int = 20,
    domain: str = "",
    location: str = "",
    experience: str = "",
    job_type: str = "",
) -> dict:
    """Return paginated, filtered job list."""
    query = Job.query.filter_by(is_active=True)

    if domain:     query = query.filter(Job.domain.ilike(f"%{domain}%"))
    if location:   query = query.filter(Job.location.ilike(f"%{location}%"))
    if experience: query = query.filter(Job.experience_level == experience)
    if job_type:   query = query.filter(Job.job_type == job_type)

    total = query.count()
    jobs  = (
        query
        .order_by(Job.fetched_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "jobs":  [j.to_dict() for j in jobs],
        "total": total,
        "page":  page,
        "pages": (total + limit - 1) // limit,
    }
