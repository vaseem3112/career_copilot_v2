"""
Sends raw resume text to Claude and gets back structured analysis.
Claude sees ONLY the actual resume — no hardcoded assumptions.
"""
from app.modules.ai.llm_client      import call_claude
from app.modules.ai.prompts         import build_resume_analysis_prompt
from app.modules.ai.response_parser import parse_json_response


def analyze_resume_text(resume_text: str) -> dict:
    """
    Full resume analysis via Claude.
    Returns structured dict matching ResumeAnalysis fields.
    """
    if not resume_text or len(resume_text.strip()) < 50:
        raise ValueError("Resume text is too short to analyze")

    system_prompt = build_resume_analysis_prompt()

    user_message  = f"""Please analyze this resume and return the structured JSON response:

--- RESUME START ---
{resume_text}
--- RESUME END ---"""

    raw_response  = call_claude(
        system_prompt = system_prompt,
        user_message  = user_message,
        max_tokens    = 4000,
    )

    result = parse_json_response(raw_response)

    if not result:
        raise ValueError("Claude returned an unparseable response")

    return result


def analyze_profile_data(profile_dict: dict) -> dict:
    """
    Analyze structured profile data (when no resume is uploaded).
    Used when user fills profile manually.
    """
    from app.modules.ai.prompts import build_profile_analysis_prompt

    system_prompt = build_profile_analysis_prompt()
    user_message  = f"Analyze this career profile:\n\n{profile_dict}"

    raw_response  = call_claude(
        system_prompt = system_prompt,
        user_message  = user_message,
        max_tokens    = 3000,
    )

    return parse_json_response(raw_response)
