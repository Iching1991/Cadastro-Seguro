import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:

    SECRET_KEY = "vetclinic-secret-key"

    SQLALCHEMY_DATABASE_URI = \
        "sqlite:///" + os.path.join(BASE_DIR, "vetclinic.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    LOGO_FOLDER = os.path.join(UPLOAD_FOLDER, "logos")

    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
