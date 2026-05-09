import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from .config     import config_map
from .extensions import db, jwt, cors, mail, celery, init_celery, register_jwt_callbacks


def create_app(env: str = "development") -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_map[env])

    _create_directories(app)

    # Extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    cors.init_app(app, resources={
        r"/api/*": {
            "origins":       app.config["CORS_ORIGINS"],
            "methods":       ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    })

    init_celery(app, celery)
    register_jwt_callbacks(jwt)

    _register_blueprints(app)
    _register_error_handlers(app)
    _setup_logging(app)

    with app.app_context():
        _import_models()
        db.create_all()
        app.logger.info(f"DB initialised — env={env}")

    return app


def _register_blueprints(app):
    from .api.v1.auth          import auth_bp
    from .api.v1.profile       import profile_bp
    from .api.v1.parser        import parser_bp
    from .api.v1.resume        import resume_bp
    from .api.v1.analysis      import analysis_bp
    from .api.v1.ats           import ats_bp
    from .api.v1.jobs          import jobs_bp
    from .api.v1.match         import match_bp
    from .api.v1.dashboard     import dashboard_bp
    from .api.v1.notifications import notifications_bp
    from .api.v1.settings      import settings_bp

    for bp, prefix in [
        (auth_bp,          "/api/v1/auth"),
        (profile_bp,       "/api/v1/profile"),
        (parser_bp,        "/api/v1/parser"),
        (resume_bp,        "/api/v1/resume"),
        (analysis_bp,      "/api/v1/analysis"),
        (ats_bp,           "/api/v1/ats"),
        (jobs_bp,          "/api/v1/jobs"),
        (match_bp,         "/api/v1/match"),
        (dashboard_bp,     "/api/v1/dashboard"),
        (notifications_bp, "/api/v1/notifications"),
        (settings_bp,      "/api/v1/settings"),
    ]:
        app.register_blueprint(bp, url_prefix=prefix)


def _import_models():
    from .models import (
        user, otp, profile, skill, resume,
        analysis, job, saved_job, match,
        notification, settings,
    )


def _register_error_handlers(app):
    from flask import jsonify

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"success": False, "error": "bad_request", "message": str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"success": False, "error": "unauthorized", "message": "Authentication required."}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"success": False, "error": "forbidden", "message": "Permission denied."}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "not_found", "message": "Resource not found."}), 404

    @app.errorhandler(413)
    def file_too_large(e):
        return jsonify({"success": False, "error": "file_too_large", "message": "File exceeds 5MB limit."}), 413

    @app.errorhandler(422)
    def unprocessable(e):
        return jsonify({"success": False, "error": "unprocessable", "message": "Invalid or missing fields."}), 422

    @app.errorhandler(429)
    def rate_limited(e):
        return jsonify({"success": False, "error": "rate_limited", "message": "Too many requests."}), 429

    @app.errorhandler(500)
    def internal(e):
        app.logger.error(f"500: {e}")
        return jsonify({"success": False, "error": "server_error", "message": "Something went wrong."}), 500


def _setup_logging(app):
    log_level = getattr(logging, app.config["LOG_LEVEL"].upper(), logging.DEBUG)
    log_file  = app.config["LOG_FILE"]

    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    fh = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)
    fh.setFormatter(fmt)
    fh.setLevel(log_level)

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    ch.setLevel(log_level)

    app.logger.setLevel(log_level)
    app.logger.addHandler(fh)
    app.logger.addHandler(ch)


def _create_directories(app):
    for d in [
        app.config["UPLOAD_FOLDER"],
        app.config["OUTPUT_FOLDER"],
        os.path.dirname(app.config["LOG_FILE"]),
        "instance",
        "ml_models/training_data",
    ]:
        if d:
            os.makedirs(d, exist_ok=True)
