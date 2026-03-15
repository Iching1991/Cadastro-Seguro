from flask_sqlalchemy import SQLAlchemy
import datetime
import secrets

db = SQLAlchemy()

# =====================================================

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.String(32),
        primary_key=True,
        default=lambda: secrets.token_hex(16)
    )

    nome = db.Column(db.String(120), nullable=False)

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    senha = db.Column(db.String(255), nullable=False)

    criado_em = db.Column(
        db.DateTime,
        default=datetime.datetime.utcnow
    )

# =====================================================

class Clinic(db.Model):

    __tablename__ = "clinics"

    id = db.Column(
        db.String(32),
        primary_key=True,
        default=lambda: secrets.token_hex(16)
    )

    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    telefone = db.Column(db.String(50))
    endereco = db.Column(db.String(255))

    logo = db.Column(db.String(255))  # ← LOGO

    criado_em = db.Column(
        db.DateTime,
        default=datetime.datetime.utcnow
    )

    user_id = db.Column(db.String(32))
