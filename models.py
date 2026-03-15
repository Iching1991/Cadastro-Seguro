from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id        = db.Column(db.Integer, primary_key=True)
    nome      = db.Column(db.String(120), nullable=False)
    email     = db.Column(db.String(120), unique=True, nullable=False)
    senha     = db.Column(db.String(256), nullable=False)
    is_admin  = db.Column(db.Boolean, default=False, nullable=False)
    aprovado  = db.Column(db.Boolean, default=False, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    clinics = db.relationship(
        "Clinic",
        backref="owner",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email}>"


class Clinic(db.Model):
    __tablename__ = "clinics"

    id        = db.Column(db.Integer, primary_key=True)
    nome      = db.Column(db.String(150), nullable=False)
    email     = db.Column(db.String(120), nullable=False)
    telefone  = db.Column(db.String(30),  nullable=False)
    endereco  = db.Column(db.String(255), nullable=False)
    logo      = db.Column(db.String(255), nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    user_id   = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    def __repr__(self):
        return f"<Clinic {self.nome}>"
