import re


def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


def is_strong_password(pwd: str) -> bool:
    return len(pwd) >= 8


def sanitize_string(s: str, max_len: int = 500) -> str:
    if not s:
        return ""
    return str(s).strip()[:max_len]
