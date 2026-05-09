from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from celery import Celery

db   = SQLAlchemy()
jwt  = JWTManager()
cors = CORS()
mail = Mail()

celery = Celery()


def init_celery(app, celery_instance):
    celery_instance.conf.update(
        broker_url         = app.config["CELERY_BROKER_URL"],
        result_backend     = app.config["CELERY_RESULT_BACKEND"],
        task_serializer    = "json",
        result_serializer  = "json",
        accept_content     = ["json"],
        timezone           = "UTC",
        task_track_started = True,
        task_time_limit    = 300,
        beat_schedule      = {
            "fetch-jobs-every-6-hours": {
                "task":     "app.tasks.email_task.send_job_fetch_task",
                "schedule": 21600,  # 6 hours in seconds
            },
        },
    )

    class ContextTask(celery_instance.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_instance.Task = ContextTask
    return celery_instance


def register_jwt_callbacks(jwt_instance):

    @jwt_instance.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        from flask import jsonify
        return jsonify({"success": False, "error": "token_expired",
                        "message": "Session expired. Please log in again."}), 401

    @jwt_instance.invalid_token_loader
    def invalid_token(error):
        from flask import jsonify
        return jsonify({"success": False, "error": "invalid_token",
                        "message": "Invalid token. Please log in again."}), 401

    @jwt_instance.unauthorized_loader
    def missing_token(error):
        from flask import jsonify
        return jsonify({"success": False, "error": "authorization_required",
                        "message": "No token provided. Please log in."}), 401

    @jwt_instance.revoked_token_loader
    def revoked_token(jwt_header, jwt_payload):
        from flask import jsonify
        return jsonify({"success": False, "error": "token_revoked",
                        "message": "Token revoked. Please log in again."}), 401
