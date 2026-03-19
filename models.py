from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# =====================================================
# INIT DB
# =====================================================

db = SQLAlchemy()


# =====================================================
# USER
# =====================================================

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(
        db.String(120),
        unique=True,
        nullable=False,
        index=True
    )

    senha = db.Column(
        db.String(256),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False,
        default="user",  # user | owner | dev
        index=True
    )

    criado_em = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # RELAÇÃO
    clinics = db.relationship(
        "Clinic",
        backref="owner",
        lazy=True,
        cascade="all, delete-orphan"
    )

    # PERMISSÕES
    def is_owner(self):
        return self.role == "owner"

    def is_dev(self):
        return self.role == "dev"

    def is_user(self):
        return self.role == "user"

    def __repr__(self):
        return f"<User {self.nome} ({self.role})>"


# =====================================================
# CLINIC / VETERINÁRIO
# =====================================================

class Clinic(db.Model):
    __tablename__ = "clinics"

    id = db.Column(db.Integer, primary_key=True)

    # 🔥 NOME PRINCIPAL
    nome = db.Column(
        db.String(150),
        nullable=False,
        index=True
    )

    # 🔥 NOVO: RESPONSÁVEL
    responsavel = db.Column(
        db.String(150),
        nullable=False,
        index=True
    )

    # 🔥 NOVO: TIPO
    tipo = db.Column(
        db.String(20),
        nullable=False,  # "clinica" ou "veterinario"
        index=True
    )

    email = db.Column(
        db.String(120),
        nullable=False,
        index=True
    )

    telefone = db.Column(
        db.String(30),
        nullable=False
    )

    endereco = db.Column(
        db.String(255),
        nullable=False
    )

    criado_em = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # =====================================================

    def is_clinic(self):
        return self.tipo == "clinica"

    def is_vet(self):
        return self.tipo == "veterinario"

    def __repr__(self):
        return f"<Clinic {self.nome} ({self.tipo})>"
