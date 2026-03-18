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
# INIT BANCO (SEGURO PARA PRODUÇÃO)
# =====================================================

def init_db():
    db.create_all()

    users = [
        ("Mhayara Reushing", "123456", "owner"),
        ("Agnaldo Angelico", "123456", "user"),
        ("Gabriela Saidel", "123456", "user"),
        ("Flávia Prado", "123456", "user"),
        ("Kerine Onuki", "123456", "user"),
        ("Agnaldo Baldissera", "123456", "dev"),
    ]

    for nome, senha, role in users:

        user = User.query.filter_by(nome=nome).first()

        if not user:
            senha_hash = bcrypt.generate_password_hash(senha).decode()

            db.session.add(User(
                nome=nome,
                senha=senha_hash,
                role=role
            ))

    db.session.commit()


# =====================================================
# HELPERS
# =====================================================

def get_current_user():
    return db.session.get(User, session.get("user_id"))


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not get_current_user():
            session.clear()
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def owner_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user or not user.is_owner():
            flash("Acesso restrito", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated


# =====================================================
# LOGIN
# =====================================================

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        nome = request.form.get("nome")
        senha = request.form.get("senha")

        user = User.query.filter_by(nome=nome).first()

        if not user:
            flash("Usuário não encontrado", "danger")
            return redirect(url_for("login"))

        if not bcrypt.check_password_hash(user.senha, senha):
            flash("Senha incorreta", "danger")
            return redirect(url_for("login"))

        session["user_id"] = user.id

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
# DASHBOARD
# =====================================================

@app.route("/dashboard")
@login_required
def dashboard():

    user = get_current_user()

    # DEV NÃO VÊ DADOS
    if user.is_dev():
        clinics = []
    elif user.is_owner():
        clinics = Clinic.query.all()
    else:
        clinics = Clinic.query.filter_by(user_id=user.id).all()

    users = User.query.all() if user.is_owner() else []

    return render_template(
        "dashboard.html",
        user=user,
        clinics=clinics,
        users=users
    )


# =====================================================
# CRIAR USUÁRIO (ADMIN)
# =====================================================

@app.route("/users/create", methods=["POST"])
@login_required
@owner_required
def create_user():

    nome = request.form.get("nome")
    senha = request.form.get("senha")
    role = request.form.get("role")

    if User.query.filter_by(nome=nome).first():
        flash("Usuário já existe", "danger")
        return redirect(url_for("dashboard"))

    senha_hash = bcrypt.generate_password_hash(senha).decode()

    db.session.add(User(
        nome=nome,
        senha=senha_hash,
        role=role
    ))

    db.session.commit()

    flash("Usuário criado com sucesso", "success")
    return redirect(url_for("dashboard"))


# =====================================================
# ALTERAR SENHA
# =====================================================

@app.route("/change-password", methods=["POST"])
@login_required
def change_password():

    user = get_current_user()

    atual = request.form.get("senha_atual")
    nova = request.form.get("nova_senha")

    if not bcrypt.check_password_hash(user.senha, atual):
        flash("Senha atual incorreta", "danger")
        return redirect(url_for("dashboard"))

    user.senha = bcrypt.generate_password_hash(nova).decode()

    db.session.commit()

    flash("Senha alterada com sucesso", "success")
    return redirect(url_for("dashboard"))


# =====================================================
# CRIAR CLÍNICA
# =====================================================

@app.route("/clinics/create", methods=["POST"])
@login_required
def create_clinic():

    user = get_current_user()

    if user.is_dev():
        flash("Sem permissão", "danger")
        return redirect(url_for("dashboard"))

    clinic = Clinic(
        nome=request.form.get("nome"),
        email=request.form.get("email"),
        telefone=request.form.get("telefone"),
        endereco=request.form.get("endereco"),
        user_id=user.id
    )

    db.session.add(clinic)
    db.session.commit()

    flash("Clínica cadastrada", "success")

    return redirect(url_for("dashboard"))


# =====================================================
# START (RAILWAY SAFE)
# =====================================================

with app.app_context():
    init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
