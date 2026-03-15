import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # ─────────────────────────────────────────────
    # SEGURANÇA
    # ─────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "troque-em-producao-use-variavel-de-ambiente")

    # ─────────────────────────────────────────────
    # BANCO DE DADOS
    # Usa PostgreSQL no Railway se DATABASE_URL
    # estiver definida, senão cai para SQLite local
    # ─────────────────────────────────────────────
    _db_url = os.environ.get("DATABASE_URL", "")

    # Railway retorna URLs postgres:// (legado),
    # SQLAlchemy exige postgresql://
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = _db_url or (
        "sqlite:///" + os.path.join(BASE_DIR, "vetclinic.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,   # reconecta se a conexão cair
        "pool_recycle":  300,    # recicla conexões a cada 5 min
    }

    # ─────────────────────────────────────────────
    # UPLOADS
    # ─────────────────────────────────────────────
    UPLOAD_FOLDER      = os.path.join(BASE_DIR, "uploads")
    LOGO_FOLDER        = os.path.join(UPLOAD_FOLDER, "logos")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB máximo por upload

    # ─────────────────────────────────────────────
    # SESSÃO
    # ─────────────────────────────────────────────
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE   = os.environ.get("RAILWAY_ENVIRONMENT") == "production"

    # ─────────────────────────────────────────────
    # AMBIENTE
    # ─────────────────────────────────────────────
    DEBUG   = os.environ.get("FLASK_DEBUG", "0") == "1"
    TESTING = False
