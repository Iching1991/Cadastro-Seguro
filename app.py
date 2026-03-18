from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_bcrypt import Bcrypt
from functools import wraps
import os

from config import Config
from models import db, User, Clinic

# =====================================================
# INIT
# =====================================================

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt = Bcrypt(app)


# =====================================================
# HELPERS
# =====================================================

def get_current_user():
    return db.session.get(User, session.get("user_id"))


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# =====================================================
# LOGIN
# =====================================================

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        senha = request.form.get("senha")

        user = User.query.filter_by(email=email).first()

        if not user or not bcrypt.check_password_hash(user.senha, senha):
            flash("Login inválido", "danger")
            return redirect(url_for("login"))

        session["user_id"] = user.id
        session["role"] = user.role

        return redirect(url_for("dashboard"))

    return render_template("login.html")


# =====================================================
# LOGOUT
# =====================================================

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# =====================================================
# DASHBOARD (CENTRO DO SISTEMA)
# =====================================================

@app.route("/dashboard")
@login_required
def dashboard():

    user = get_current_user()

    # DEV não pode ver dados
    if user.is_dev():
        clinics = []

    # OWNER vê tudo
    elif user.is_owner():
        clinics = Clinic.query.order_by(Clinic.id.desc()).all()

    # USER vê apenas os seus
    else:
        clinics = (
            Clinic.query
            .filter_by(user_id=user.id)
            .order_by(Clinic.id.desc())
            .all()
        )

    return render_template(
        "dashboard.html",
        user=user,
        clinics=clinics
    )


# =====================================================
# CREATE CLINIC
# =====================================================

@app.route("/clinics/create", methods=["POST"])
@login_required
def create_clinic():

    user = get_current_user()

    # DEV não pode cadastrar
    if user.is_dev():
        flash("Você não tem permissão para cadastrar.", "danger")
        return redirect(url_for("dashboard"))

    nome = request.form.get("nome")
    email = request.form.get("email")
    telefone = request.form.get("telefone")
    endereco = request.form.get("endereco")

    if not all([nome, email, telefone, endereco]):
        flash("Preencha todos os campos.", "warning")
        return redirect(url_for("dashboard"))

    clinic = Clinic(
        nome=nome,
        email=email,
        telefone=telefone,
        endereco=endereco,
        user_id=user.id
    )

    db.session.add(clinic)
    db.session.commit()

    flash("Clínica cadastrada com sucesso!", "success")

    return redirect(url_for("dashboard"))


# =====================================================
# DELETE CLINIC (BONUS PROFISSIONAL)
# =====================================================

@app.route("/clinics/delete/<int:id>", methods=["POST"])
@login_required
def delete_clinic(id):

    user = get_current_user()
    clinic = db.session.get(Clinic, id)

    if not clinic:
        flash("Clínica não encontrada.", "danger")
        return redirect(url_for("dashboard"))

    # Permissão: owner ou dono da clínica
    if not (user.is_owner() or clinic.user_id == user.id):
        flash("Sem permissão.", "danger")
        return redirect(url_for("dashboard"))

    db.session.delete(clinic)
    db.session.commit()

    flash("Clínica removida.", "success")

    return redirect(url_for("dashboard"))


# =====================================================
# SEED USERS
# =====================================================

def seed_users():

    users = [
        ("Proprietário", "admin@admin.com", "123456", "owner"),
        ("Dev", "dev@dev.com", "123456", "dev"),
    ]

    for nome, email, senha, role in users:

        if not User.query.filter_by(email=email).first():

            senha_hash = bcrypt.generate_password_hash(senha).decode()

            user = User(
                nome=nome,
                email=email,
                senha=senha_hash,
                role=role
            )

            db.session.add(user)

    db.session.commit()


# =====================================================
# INIT AUTOMÁTICO (RAILWAY)
# =====================================================

with app.app_context():
    db.create_all()
    seed_users()

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["LOGO_FOLDER"], exist_ok=True)
