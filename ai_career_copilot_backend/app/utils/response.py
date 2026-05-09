from flask import jsonify
from typing import Any


def success(data: Any = None, message: str = "Success", status: int = 200):
    body = {"success": True, "message": message}
    if data is not None:
        body.update(data if isinstance(data, dict) else {"data": data})
    return jsonify(body), status


def error(message: str = "Error", status: int = 400, code: str = None):
    body = {"success": False, "message": message}
    if code:
        body["error"] = code
    return jsonify(body), status
