from __future__ import annotations

from flask import Blueprint, jsonify, request, current_app

from .auth import authenticate, issue_token

bp = Blueprint("routes", __name__)

@bp.get("/healthz")
def healthz():
    return jsonify({"status": "ok"})

@bp.post("/login")
def login():
    body = request.get_json(silent=True) or {}
    username = str(body.get("username", "")).strip()
    password = str(body.get("password", "")).strip()

    auth = authenticate(username, password)
    if not auth:
        return jsonify({"error": "invalid_credentials"}), 401

    token = issue_token(
        secret=current.app.config["SECRET_KEY"],
        issuer=current.app.config["JWT_ISSUER"],
        ttl_seconds=current.app.config["JWT_TTL_SECONDS"],
        username=auth["username"],
        role=auth["role"],
    )
    return jsonify({"access_token": token, "token_type": "Bearer"})

@bp.get("/whoami")
def whoami():
    user = getattr(request, "ztna_user", None)
    if not user:
        return jsonify({"authenticated": False})
    return jsonify({"authenticated": True, "user": user})

@bp.get("/apps/<app_id>")
def app_gateway(app_id: str):
    # If request reached here, it is authorized by the middleware.
    user = getattr(request, "ztna_user", None)
    return jsonify(
        {
            "message": "Access granted to protected app",
            "app": app_id,
            "user": user,
            "hint": "This endpoint simulates a private app behind a ZTNA gateway.",
        }
    )
