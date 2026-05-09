import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    SECRET_KEY                     = os.getenv("SECRET_KEY", "dev-secret-change-this")
    DEBUG                          = False
    TESTING                        = False

    # Database
    SQLALCHEMY_DATABASE_URI        = os.getenv("DATABASE_URL", "sqlite:///local.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS      = {"pool_pre_ping": True, "pool_recycle": 300}

    # JWT
    JWT_SECRET_KEY                 = os.getenv("JWT_SECRET_KEY", "jwt-secret-change-this")
    JWT_ACCESS_TOKEN_EXPIRES       = timedelta(hours=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_HOURS", 24)))
    JWT_REFRESH_TOKEN_EXPIRES      = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS", 30)))
    JWT_TOKEN_LOCATION             = ["headers"]
    JWT_HEADER_NAME                = "Authorization"
    JWT_HEADER_TYPE                = "Bearer"

    # Email
    MAIL_SERVER                    = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT                      = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS                   = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME                  = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD                  = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER            = os.getenv("MAIL_DEFAULT_SENDER", "CareerCopilot <noreply@careercopilot.com>")

    # AI
    ANTHROPIC_API_KEY              = os.getenv("ANTHROPIC_API_KEY")
    CLAUDE_MODEL                   = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")

    # Job APIs
    ADZUNA_APP_ID                  = os.getenv("ADZUNA_APP_ID")
    ADZUNA_APP_KEY                 = os.getenv("ADZUNA_APP_KEY")
    ADZUNA_COUNTRY                 = os.getenv("ADZUNA_COUNTRY", "in")
    JSEARCH_API_KEY                = os.getenv("JSEARCH_API_KEY")

    # Redis / Celery
    REDIS_URL                      = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL              = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND          = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

    # Files
    UPLOAD_FOLDER                  = os.getenv("UPLOAD_FOLDER", "uploads")
    OUTPUT_FOLDER                  = os.getenv("OUTPUT_FOLDER", "outputs")
    MAX_CONTENT_LENGTH             = int(os.getenv("MAX_CONTENT_LENGTH_MB", 5)) * 1024 * 1024
    ALLOWED_EXTENSIONS             = set(os.getenv("ALLOWED_EXTENSIONS", "pdf,doc,docx").split(","))

    # OTP
    OTP_EXPIRES_MINUTES            = int(os.getenv("OTP_EXPIRES_MINUTES", 10))
    OTP_LENGTH                     = int(os.getenv("OTP_LENGTH", 6))

    # ML
    MODEL_PATH                     = os.getenv("MODEL_PATH", "ml_models/shortlist_model.pkl")
    EMBEDDING_MODEL                = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # Frontend
    FRONTEND_URL                   = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # CORS
    CORS_ORIGINS                   = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://10.114.122.53:8080",
    ]

    # Logging
    LOG_LEVEL                      = os.getenv("LOG_LEVEL", "DEBUG")
    LOG_FILE                       = os.getenv("LOG_FILE", "logs/app.log")


class DevelopmentConfig(BaseConfig):
    DEBUG             = True
    SQLALCHEMY_ECHO   = True


class ProductionConfig(BaseConfig):
    DEBUG             = False
    SQLALCHEMY_ECHO   = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping":  True,
        "pool_recycle":   300,
        "pool_size":      10,
        "max_overflow":   20,
    }
    SESSION_COOKIE_SECURE   = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


class TestingConfig(BaseConfig):
    TESTING                 = True
    DEBUG                   = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    MAIL_SUPPRESS_SEND      = True


config_map = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "testing":     TestingConfig,
}
