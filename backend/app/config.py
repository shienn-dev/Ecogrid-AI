import os

class Config:
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() in ("true", "1", "yes")
    TESTING = False
    # CORS: comma-separated origins, default allow localhost Vite/Flask
    CORS_ORIGINS = [o.strip() for o in os.getenv(
        "CORS_ORIGINS",
        "http://127.0.0.1:5000,http://localhost:5000,http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:8000,http://localhost:8000,http://127.0.0.1:3000,http://localhost:3000"
    ).split(",") if o.strip()]
    # Support wildcard via env "CORS_ALLOW_ALL=true" for dev
    CORS_ALLOW_ALL = os.getenv("CORS_ALLOW_ALL", "false").lower() in ("true", "1")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(16 * 1024)))  # 16KB
    MAX_DEVICES = int(os.getenv("MAX_DEVICES", "50"))
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database/energy.db")
    DEFAULT_TARIFF = float(os.getenv("DEFAULT_TARIFF", "1444.70"))
    DEFAULT_EMISSION_FACTOR = float(os.getenv("DEFAULT_EMISSION_FACTOR", "0.87"))
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")


class TestingConfig(Config):
    TESTING = True
    DATABASE_URL = "sqlite:///:memory:"
    CORS_ALLOW_ALL = True
