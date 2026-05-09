import random
import string
from flask import current_app


def generate_otp() -> str:
    length = current_app.config.get("OTP_LENGTH", 6)
    return "".join(random.choices(string.digits, k=length))


def get_otp_expiry() -> int:
    return current_app.config.get("OTP_EXPIRES_MINUTES", 10)
