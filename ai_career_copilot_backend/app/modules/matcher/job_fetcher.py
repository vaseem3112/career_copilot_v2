"""
Fetches live jobs from Adzuna and JSearch APIs.
Normalizes results into a standard schema.
"""
import requests
from flask import current_app


def fetch_adzuna_jobs(query: str = "", location: str = "", page: int = 1) -> list[dict]:
    """Fetch jobs from Adzuna API."""
    app_id  = current_app.config.get("ADZUNA_APP_ID")
    app_key = current_app.config.get("ADZUNA_APP_KEY")
    country = current_app.config.get("ADZUNA_COUNTRY", "in")

    if not app_id or not app_key:
        current_app.logger.warning("Adzuna API keys not configured")
        return []

    params = {
        "app_id":   app_id,
        "app_key":  app_key,
        "results_per_page": 20,
        "page":     page,
        "content-type": "application/json",
    }
    if query:    params["what"] = query
    if location: params["where"] = location

    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return _normalize_adzuna(data.get("results", []))
    except Exception as e:
        current_app.logger.error(f"Adzuna fetch failed: {e}")
        return []


def fetch_jsearch_jobs(query: str = "", location: str = "") -> list[dict]:
    """Fetch jobs from JSearch (RapidAPI)."""
    api_key = current_app.config.get("JSEARCH_API_KEY")
    if not api_key:
        current_app.logger.warning("JSearch API key not configured")
        return []

    headers = {
        "X-RapidAPI-Key":  api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    }
    params = {"query": f"{query} {location}".strip(), "page": "1", "num_pages": "1"}

    try:
        resp = requests.get(
            "https://jsearch.p.rapidapi.com/search",
            headers = headers,
            params  = params,
            timeout = 10,
        )
        resp.raise_for_status()
        data = resp.json()
        return _normalize_jsearch(data.get("data", []))
    except Exception as e:
        current_app.logger.error(f"JSearch fetch failed: {e}")
        return []


def _normalize_adzuna(results: list) -> list[dict]:
    normalized = []
    for r in results:
        normalized.append({
            "external_id":  str(r.get("id", "")),
            "source":       "adzuna",
            "title":        r.get("title", ""),
            "company":      r.get("company", {}).get("display_name", ""),
            "location":     r.get("location", {}).get("display_name", ""),
            "description":  r.get("description", ""),
            "salary_min":   r.get("salary_min"),
            "salary_max":   r.get("salary_max"),
            "apply_url":    r.get("redirect_url", ""),
            "posted_at":    r.get("created", ""),
        })
    return normalized


def _normalize_jsearch(results: list) -> list[dict]:
    normalized = []
    for r in results:
        normalized.append({
            "external_id":  r.get("job_id", ""),
            "source":       "jsearch",
            "title":        r.get("job_title", ""),
            "company":      r.get("employer_name", ""),
            "location":     f"{r.get('job_city', '')} {r.get('job_country', '')}".strip(),
            "description":  r.get("job_description", ""),
            "salary_min":   r.get("job_min_salary"),
            "salary_max":   r.get("job_max_salary"),
            "apply_url":    r.get("job_apply_link", ""),
            "posted_at":    r.get("job_posted_at_datetime_utc", ""),
            "job_type":     r.get("job_employment_type", ""),
        })
    return normalized
