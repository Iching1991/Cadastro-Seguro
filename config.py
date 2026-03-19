import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:

    # ==============================
    # 🔐 SEGURANÇA
    # ==============================
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key"


    # ==============================
    # 🗄️ BANCO (ANTI-CRASH TOTAL)
    # ==============================
    raw_db_url = os.environ.get("DATABASE_URL")

    if raw_db_url:
        raw_db_url = raw_db_url.strip()

    # 🔥 validação forte
    if not raw_db_url or raw_db_url in ["", "None", "null"]:
        print("⚠️ DATABASE_URL inválida → usando SQLite")
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "vetclinic.db")

    else:
        # Corrige Railway
        if raw_db_url.startswith("postgres://"):
            raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)

        try:
            from sqlalchemy.engine.url import make_url
            make_url(raw_db_url)  # valida

            SQLALCHEMY_DATABASE_URI = raw_db_url
            print("✅ Banco configurado com sucesso")

        except Exception as e:
            print("❌ DATABASE_URL inválida:", raw_db_url)
            print("⚠️ Erro:", e)
            print("➡️ Usando SQLite como fallback")

            SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "vetclinic.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }


    # ==============================
    # 📁 UPLOADS
    # ==============================
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    LOGO_FOLDER   = os.path.join(UPLOAD_FOLDER, "logos")

    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024


    # ==============================
    # 🍪 SESSÃO
    # ==============================
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("RAILWAY_ENVIRONMENT") == "production"


    # ==============================
    # ⚙️ AMBIENTE
    # ==============================
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
    TESTING = False
