from app.extensions import celery, mail
from flask import current_app, render_template_string
from flask_mail import Message


def _send(to: str, subject: str, html: str):
    try:
        msg = Message(subject=subject, recipients=[to], html=html)
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f"Email send failed to {to}: {e}")
        raise


@celery.task(bind=True, max_retries=3, default_retry_delay=30)
def send_otp_email(self, to_email: str, name: str, otp_code: str):
    html = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:auto;padding:32px">
      <h2 style="color:#4f8ef7">Verify your CareerCopilot account</h2>
      <p>Hi {name},</p>
      <p>Your verification code is:</p>
      <div style="font-size:36px;font-weight:bold;letter-spacing:12px;
                  background:#f0f4ff;padding:16px;border-radius:8px;
                  text-align:center;color:#4f8ef7;margin:16px 0">
        {otp_code}
      </div>
      <p style="color:#666">This code expires in {current_app.config.get('OTP_EXPIRES_MINUTES',10)} minutes.</p>
      <p style="color:#666">If you didn't create an account, you can safely ignore this email.</p>
      <hr style="border:none;border-top:1px solid #eee;margin:24px 0"/>
      <p style="color:#aaa;font-size:12px">CareerCopilot · AI-Powered Career Platform</p>
    </div>
    """
    try:
        _send(to_email, "Your CareerCopilot verification code", html)
    except Exception as exc:
        raise self.retry(exc=exc)


@celery.task(bind=True, max_retries=3, default_retry_delay=30)
def send_welcome_email(self, to_email: str, name: str):
    frontend_url = current_app.config.get("FRONTEND_URL", "http://localhost:3000")
    html = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:auto;padding:32px">
      <h2 style="color:#3ecf8e">Welcome to CareerCopilot! 🎉</h2>
      <p>Hi {name},</p>
      <p>Your account has been verified and is ready to use.</p>
      <p style="margin:16px 0">Here's how to get started:</p>
      <ol style="color:#444;line-height:2">
        <li>Complete your profile</li>
        <li>Upload your resume</li>
        <li>Get AI analysis and job matches</li>
      </ol>
      <a href="{frontend_url}/profile/setup"
         style="display:inline-block;background:#4f8ef7;color:white;
                padding:12px 24px;border-radius:8px;text-decoration:none;
                margin-top:16px;font-weight:bold">
        Complete Your Profile →
      </a>
      <hr style="border:none;border-top:1px solid #eee;margin:24px 0"/>
      <p style="color:#aaa;font-size:12px">CareerCopilot · AI-Powered Career Platform</p>
    </div>
    """
    try:
        _send(to_email, "Welcome to CareerCopilot! 🎉", html)
    except Exception as exc:
        raise self.retry(exc=exc)


@celery.task(bind=True, max_retries=3, default_retry_delay=30)
def send_password_reset_email(self, to_email: str, name: str, reset_link: str):
    html = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:auto;padding:32px">
      <h2 style="color:#4f8ef7">Reset your password</h2>
      <p>Hi {name},</p>
      <p>Click the button below to reset your CareerCopilot password:</p>
      <a href="{reset_link}"
         style="display:inline-block;background:#4f8ef7;color:white;
                padding:12px 24px;border-radius:8px;text-decoration:none;
                margin:16px 0;font-weight:bold">
        Reset Password
      </a>
      <p style="color:#666">This link expires in 15 minutes.</p>
      <p style="color:#666">If you didn't request a reset, please ignore this email.</p>
      <hr style="border:none;border-top:1px solid #eee;margin:24px 0"/>
      <p style="color:#aaa;font-size:12px">CareerCopilot · AI-Powered Career Platform</p>
    </div>
    """
    try:
        _send(to_email, "Reset your CareerCopilot password", html)
    except Exception as exc:
        raise self.retry(exc=exc)


@celery.task(bind=True, max_retries=2)
def send_job_fetch_task(self):
    """Periodic task — fetch fresh jobs every 6 hours."""
    from app.modules.matcher.job_fetcher import fetch_adzuna_jobs, fetch_jsearch_jobs
    from app.models.job import Job, JobSource
    from app.extensions import db

    sources = [
        ("adzuna",  fetch_adzuna_jobs),
        ("jsearch", fetch_jsearch_jobs),
    ]

    total_new = 0
    for source_name, fetcher in sources:
        source = JobSource.query.filter_by(name=source_name).first()
        if not source:
            source = JobSource(name=source_name)
            db.session.add(source)
            db.session.flush()

        try:
            jobs_data = fetcher()
            for jd in jobs_data:
                exists = Job.query.filter_by(external_id=jd["external_id"]).first()
                if not exists and jd.get("title"):
                    job = Job(
                        source_id   = source.id,
                        external_id = jd["external_id"],
                        title       = jd["title"],
                        company     = jd.get("company"),
                        location    = jd.get("location"),
                        description = jd.get("description"),
                        salary_min  = jd.get("salary_min"),
                        salary_max  = jd.get("salary_max"),
                        apply_url   = jd.get("apply_url"),
                        job_type    = jd.get("job_type"),
                    )
                    db.session.add(job)
                    total_new += 1

            from datetime import datetime, timezone
            source.last_fetch = datetime.now(timezone.utc)
        except Exception as e:
            current_app.logger.error(f"Job fetch failed for {source_name}: {e}")

    db.session.commit()
    current_app.logger.info(f"Job fetch complete: {total_new} new jobs added")
