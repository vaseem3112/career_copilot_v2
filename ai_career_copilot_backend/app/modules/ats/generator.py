"""
ATS Resume Generator.
Claude rewrites the actual resume to match the actual JD.
Never fabricates experience — only rewords and restructures.
"""
from app.modules.ai.llm_client import call_claude
from app.modules.ai.prompts    import build_ats_generation_prompt


def generate_ats_resume(
    resume_text:      str,
    job_description:  str,
    target_job_title: str,
    company:          str = "",
) -> str:
    """
    Rewrite resume text to be ATS-optimized for the given JD.
    Returns plain text resume.
    """
    if not resume_text.strip():
        raise ValueError("Resume text is empty")
    if not job_description.strip():
        raise ValueError("Job description is empty")

    system_prompt = build_ats_generation_prompt(target_job_title, company)

    user_message = f"""TARGET JOB TITLE: {target_job_title}
{"COMPANY: " + company if company else ""}

JOB DESCRIPTION:
{job_description}

ORIGINAL RESUME:
{resume_text}

Rewrite the resume above to be ATS-optimized for this role.
Use ONLY information from the original resume — do not add fake experience."""

    return call_claude(
        system_prompt = system_prompt,
        user_message  = user_message,
        max_tokens    = 3000,
    )
