import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # =====================================================
    # 🔐 SEGURANÇA
    # =====================================================
    SECRET_KEY = os.environ.get("SECRET_KEY", "troque-em-producao")


    # =====================================================
    # 🗄️ BANCO DE DADOS
    # =====================================================
    DATABASE_URL = os.environ.get("DATABASE_URL", "")

    # Railway usa postgres:// → corrigir para SQLAlchemy
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = DATABASE_URL or (
        "sqlite:///" + os.path.join(BASE_DIR, "vetclinic.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }


    # =====================================================
    # 📁 UPLOADS
    # =====================================================
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    LOGO_FOLDER   = os.path.join(UPLOAD_FOLDER, "logos")

    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB


    # =====================================================
    # 🍪 SESSÃO / COOKIES
    # =====================================================
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Só ativa HTTPS cookie em produção (Railway)
    SESSION_COOKIE_SECURE = os.environ.get("RAILWAY_ENVIRONMENT") == "production"


    # =====================================================
    # ⚙️ AMBIENTE
    # =====================================================
    DEBUG   = os.environ.get("FLASK_DEBUG", "0") == "1"
    TESTING = False
