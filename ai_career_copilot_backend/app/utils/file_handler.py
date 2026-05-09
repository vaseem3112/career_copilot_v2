import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename


def allowed_file(filename: str) -> bool:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config.get("ALLOWED_EXTENSIONS", {"pdf", "doc", "docx"})


def save_upload(file, user_id: str) -> tuple[str, str, str]:
    """
    Save uploaded file to disk.
    Returns: (filepath, filename, file_type)
    """
    original  = secure_filename(file.filename)
    ext       = original.rsplit(".", 1)[-1].lower()
    unique    = f"{user_id}_{uuid.uuid4().hex}.{ext}"
    folder    = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    filepath  = os.path.join(folder, unique)
    file.save(filepath)
    return filepath, original, ext


def save_output(content: str, user_id: str, suffix: str = "ats") -> str:
    """Save AI-generated resume text to outputs folder."""
    folder   = current_app.config["OUTPUT_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    filename = f"{user_id}_{suffix}_{uuid.uuid4().hex[:8]}.txt"
    filepath = os.path.join(folder, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath
