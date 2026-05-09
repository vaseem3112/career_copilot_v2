from flask import Blueprint, request, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity,
)
from datetime import datetime, timezone

from app.extensions import db
from app.models.user     import User
from app.models.otp      import OTPToken
from app.models.settings import UserSettings
from app.utils.response  import success, error
from app.utils.validators import is_valid_email, is_strong_password
from app.utils.otp_helpers import generate_otp, get_otp_expiry
from app.tasks.email_task  import (
    send_otp_email, send_welcome_email, send_password_reset_email
)

auth_bp = Blueprint("auth", __name__)


# ─────────────────────────────────────────
# POST /api/v1/auth/register
# ─────────────────────────────────────────
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    name     = (data.get("name")     or "").strip()
    email    = (data.get("email")    or "").strip().lower()
    password = (data.get("password") or "")

    # ── Validation ──
    if not name:
        return error("Name is required", 400)
    if not is_valid_email(email):
        return error("Invalid email address", 400)
    if not is_strong_password(password):
        return error("Password must be at least 8 characters", 400)

    # ── Duplicate check ──
    if User.query.filter_by(email=email).first():
        return error("An account with this email already exists", 409)

    # ── Create user ──
    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()   # get user.id before commit

    # ── Create default settings ──
    db.session.add(UserSettings(user_id=user.id))

    # ── Generate OTP ──
    otp_code = generate_otp()
    otp      = OTPToken.create(
        user_id         = user.id,
        code            = otp_code,
        purpose         = "email_verification",
        expires_minutes = get_otp_expiry(),
    )
    db.session.add(otp)
    db.session.commit()

    # ── Send OTP email (async via Celery) ──
    try:
        send_otp_email.delay(
            to_email = email,
            name     = name,
            otp_code = otp_code,
        )
    except Exception as e:
        current_app.logger.warning(f"Email task failed: {e}")

    return success(
        {"email": email},
        message = "Account created. Please verify your email with the OTP sent.",
        status  = 201,
    )


# ─────────────────────────────────────────
# POST /api/v1/auth/verify-otp
# ─────────────────────────────────────────
@auth_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    data  = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    code  = (data.get("otp")   or "").strip()

    if not email or not code:
        return error("Email and OTP are required", 400)

    user = User.query.filter_by(email=email).first()
    if not user:
        return error("User not found", 404)

    if user.is_verified:
        # Already verified — just log them in
        token = create_access_token(identity=user.id)
        return success({"token": token, "user": user.to_dict()}, message="Already verified")

    # ── Find valid OTP ──
    otp = (
        OTPToken.query
        .filter_by(user_id=user.id, code=code, purpose="email_verification")
        .order_by(OTPToken.created_at.desc())
        .first()
    )

    if not otp or not otp.is_valid():
        return error("Invalid or expired OTP. Please request a new one.", 400)

    # ── Mark verified ──
    otp.mark_used()
    user.is_verified = True
    user.update_last_login()
    db.session.commit()

    # ── Send welcome email ──
    try:
        send_welcome_email.delay(to_email=user.email, name=user.name)
    except Exception as e:
        current_app.logger.warning(f"Welcome email failed: {e}")

    token         = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return success({
        "token":         token,
        "refresh_token": refresh_token,
        "user":          user.to_dict(),
    }, message="Email verified successfully")


# ─────────────────────────────────────────
# POST /api/v1/auth/resend-otp
# ─────────────────────────────────────────
@auth_bp.route("/resend-otp", methods=["POST"])
def resend_otp():
    data  = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()

    if not email:
        return error("Email is required", 400)

    user = User.query.filter_by(email=email).first()
    if not user:
        return error("User not found", 404)

    if user.is_verified:
        return error("Email is already verified", 400)

    # ── Invalidate all previous OTPs ──
    OTPToken.query.filter_by(
        user_id = user.id,
        purpose = "email_verification",
        is_used = False,
    ).update({"is_used": True})

    # ── New OTP ──
    otp_code = generate_otp()
    otp      = OTPToken.create(
        user_id         = user.id,
        code            = otp_code,
        purpose         = "email_verification",
        expires_minutes = get_otp_expiry(),
    )
    db.session.add(otp)
    db.session.commit()

    try:
        send_otp_email.delay(
            to_email = email,
            name     = user.name,
            otp_code = otp_code,
        )
    except Exception as e:
        current_app.logger.warning(f"Resend OTP email failed: {e}")

    return success(message="OTP resent successfully")


# ─────────────────────────────────────────
# POST /api/v1/auth/login
# ─────────────────────────────────────────
@auth_bp.route("/login", methods=["POST"])
def login():
    data     = request.get_json(silent=True) or {}
    email    = (data.get("email")    or "").strip().lower()
    password = (data.get("password") or "")

    if not email or not password:
        return error("Email and password are required", 400)

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return error("Invalid email or password", 401)

    if not user.is_active:
        return error("Your account has been deactivated", 403)

    if not user.is_verified:
        # Resend OTP automatically
        otp_code = generate_otp()
        OTPToken.query.filter_by(user_id=user.id, is_used=False).update({"is_used": True})
        otp = OTPToken.create(user_id=user.id, code=otp_code, purpose="email_verification")
        db.session.add(otp)
        db.session.commit()
        try:
            send_otp_email.delay(to_email=email, name=user.name, otp_code=otp_code)
        except Exception:
            pass
        return error("Please verify your email. A new OTP has been sent.", 403)

    user.update_last_login()

    token         = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return success({
        "token":         token,
        "refresh_token": refresh_token,
        "user":          user.to_dict(),
    }, message="Login successful")


# ─────────────────────────────────────────
# POST /api/v1/auth/logout
# ─────────────────────────────────────────
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    # Stateless JWT — client drops token
    # For token blocklist, add JWT to a Redis set here
    return success(message="Logged out successfully")


# ─────────────────────────────────────────
# POST /api/v1/auth/forgot-password
# ─────────────────────────────────────────
@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data  = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()

    if not email:
        return error("Email is required", 400)

    user = User.query.filter_by(email=email).first()
    # Always return success to prevent email enumeration
    if not user:
        return success(message="If that email exists, a reset link has been sent.")

    # ── Generate reset OTP ──
    OTPToken.query.filter_by(user_id=user.id, purpose="password_reset", is_used=False).update({"is_used": True})
    otp_code = generate_otp()
    otp = OTPToken.create(user_id=user.id, code=otp_code, purpose="password_reset", expires_minutes=15)
    db.session.add(otp)
    db.session.commit()

    reset_link = f"{current_app.config['FRONTEND_URL']}/reset-password?token={otp_code}&email={email}"

    try:
        send_password_reset_email.delay(to_email=email, name=user.name, reset_link=reset_link)
    except Exception as e:
        current_app.logger.warning(f"Reset email failed: {e}")

    return success(message="If that email exists, a reset link has been sent.")


# ─────────────────────────────────────────
# POST /api/v1/auth/reset-password
# ─────────────────────────────────────────
@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data         = request.get_json(silent=True) or {}
    email        = (data.get("email")        or "").strip().lower()
    token        = (data.get("token")        or "").strip()
    new_password = (data.get("new_password") or "")

    if not all([email, token, new_password]):
        return error("Email, token and new_password are required", 400)

    if not is_strong_password(new_password):
        return error("Password must be at least 8 characters", 400)

    user = User.query.filter_by(email=email).first()
    if not user:
        return error("Invalid reset request", 400)

    otp = (
        OTPToken.query
        .filter_by(user_id=user.id, code=token, purpose="password_reset")
        .order_by(OTPToken.created_at.desc())
        .first()
    )

    if not otp or not otp.is_valid():
        return error("Invalid or expired reset token", 400)

    otp.mark_used()
    user.set_password(new_password)
    db.session.commit()

    return success(message="Password reset successfully. Please log in.")


# ─────────────────────────────────────────
# DELETE /api/v1/auth/account
# ─────────────────────────────────────────
@auth_bp.route("/account", methods=["DELETE"])
@jwt_required()
def delete_account():
    user_id = get_jwt_identity()
    user    = User.query.get(user_id)
    if not user:
        return error("User not found", 404)

    db.session.delete(user)
    db.session.commit()
    return success(message="Account permanently deleted")
