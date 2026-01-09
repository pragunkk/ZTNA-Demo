from __future__ import annotations

from typing import Any, Dict

from flask import Flask, jsonify, request
from flask_talisman import Talisman

from .config import Config
from .opa_client import OPAError, query_opa
from .auth import verify_token
from .routes import bp as routes_bp

def _parse_posture_headers() -> Dict[str, Any]:
    """
    Simulated device posture signals (normally provided by an agent / MDM / IdP):
    X-Device-Trusted: true/false
    X-MFA: true/false
    X-Geo: IN/US/etc
    """
    def as_bool(v: str | None) -> bool:
        if v is None:
            return False
        return v.strip().lower() in {"1", "true", "yes", "y", "on"}

    return {
        "device_trusted": as_bool(request.headers.get("X-Device-Trusted")),
        "mfa": as_bool(request.headers.get("X-MFA")),
        "geo": (request.headers.get("X-Geo") or "").strip().upper() or "UNKNOWN",
    }

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # Basic security headers (good resume signal)
    Talisman(app, content_security_policy=None)

    app.register_blueprint(routes_bp)

    @app.before_request
    def ztna_middleware():
        # Public endpoints
        if request.path in {"/healthz", "/login"}:
            return None

        # AuthN (JWT)
        auth_header = request.headers.get("Authorization", "")
        token = ""
        if auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1].strip()

        decoded = None
        if token:
            decoded = verify_token(
                secret=app.config["SECRET_KEY"],
                issuer=app.config["JWT_ISSUER"],
                token=token,
            )

        if not decoded:
            return jsonify({"error": "unauthorized"}), 401

        # Attach user context for routes
        request.ztna_user = {
            "username": decoded.get("sub"),
            "role": decoded.get("role"),
        }

        posture = _parse_posture_headers()

        # AuthZ via OPA (PDP)
        input_payload = {
            "user": {
                "is_authenticated": True,
                "name": request.ztna_user["username"],
                "role": request.ztna_user["role"],
            },
            "device": posture,
            "resource": {
                "path": request.path,
                "app": request.view_args.get("app_id") if request.view_args else None,
            },
            "action": request.method,
        }

        try:
            allowed = query_opa(
                url=app.config["OPA_URL"],
                timeout_seconds=app.config["OPA_TIMEOUT_SECONDS"],
                input_payload=input_payload,
            )
        except OPAError as exc:
            return jsonify({"error": "policy_engine_unavailable", "detail": str(exc)}), 503

        if not allowed:
            return jsonify({"error": "forbidden", "reason": "policy_denied"}), 403

        return None

    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "not_found"}), 404

    return app
