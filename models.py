from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# =====================================================
# USER
# =====================================================

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(
        db.String(120),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        index=True,
        nullable=False
    )

    senha = db.Column(
        db.String(256),
        nullable=False
    )

    # 🔥 NOVO SISTEMA DE ROLES
    role = db.Column(
        db.String(20),
        default="user",   # user | owner | dev
        nullable=False,
        index=True
    )

    criado_em = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # RELAÇÃO COM CLINICS
    clinics = db.relationship(
        "Clinic",
        backref="owner",
        lazy="select",
        cascade="all, delete-orphan"
    )

    # =====================================================
    # PERMISSÕES
    # =====================================================

    def is_owner(self):
        return self.role == "owner"

    def is_dev(self):
        return self.role == "dev"

    def is_user(self):
        return self.role == "user"

    # =====================================================

    def __repr__(self):
        return f"<User id={self.id} email={self.email} role={self.role}>"



# =====================================================
# CLINIC
# =====================================================

class Clinic(db.Model):
    __tablename__ = "clinics"

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(
        db.String(150),
        nullable=False
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

    logo = db.Column(
        db.String(255),
        nullable=True
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

    def __repr__(self):
        return f"<Clinic id={self.id} nome={self.nome}>"
