import os

def env_bool(key: str, default: bool = False) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")

    # JWT
    JWT_ISSUER = os.getenv("JWT_ISSUER", "ztna-demo")
    JWT_TTL_SECONDS = int(os.getenv("JWT_TTL_SECONDS", "3600"))

    # OPA
    OPA_URL = os.getenv("OPA_URL", "http://localhost:8181/v1/data/ztna/allow")
    OPA_TIMEOUT_SECONDS = float(os.getenv("OPA_TIMEOUT_SECONDS", "2.0"))

    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))

    # Debug
    DEBUG = env_bool("DEBUG", True)
