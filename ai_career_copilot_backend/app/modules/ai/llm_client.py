import anthropic
from flask import current_app


def get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=current_app.config["ANTHROPIC_API_KEY"])


def call_claude(system_prompt: str, user_message: str, max_tokens: int = 3000) -> str:
    """
    Single entry point for all Claude API calls.
    Returns raw text response.
    """
    client = get_client()
    model  = current_app.config.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")

    message = client.messages.create(
        model      = model,
        max_tokens = max_tokens,
        system     = system_prompt,
        messages   = [{"role": "user", "content": user_message}],
    )
    return message.content[0].text
