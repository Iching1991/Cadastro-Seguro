from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_bcrypt import Bcrypt
from functools import wraps
import os

from config import Config
from models import db, User, Clinic

# =====================================================
# INIT APP
# =====================================================

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt = Bcrypt(app)


# =====================================================
# INIT DATABASE (SEMPRE ATUALIZA SENHA)
# =====================================================

def init_db():
    db.create_all()

    users = [
        ("Mhayara Reushing", "123456", "owner"),
        ("Agnaldo Angelico", "123456", "user"),
        ("Gabriela Saidel", "123456", "user"),
        ("Flávia Prado", "123456", "user"),
        ("Karine Onuki", "123456", "user"),
        ("Agnaldo Baldissera", "123456", "dev"),
    ]

    for nome, senha, role in users:

        senha_hash = bcrypt.generate_password_hash(senha).decode()

        user = User.query.filter_by(nome=nome).first()

        if user:
            user.senha = senha_hash
            user.role = role
        else:
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
    user_id = session.get("user_id")
    return db.session.get(User, user_id) if user_id else None


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not get_current_user():
            session.clear()
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

        nome = request.form.get("nome", "").strip()
        senha = request.form.get("senha", "")

        if not nome or not senha:
            flash("Preencha todos os campos", "warning")
            return redirect(url_for("login"))

        user = User.query.filter_by(nome=nome).first()

        if not user:
            flash("Usuário não encontrado", "danger")
            return redirect(url_for("login"))

        if not bcrypt.check_password_hash(user.senha, senha):
            flash("Senha incorreta", "danger")
            return redirect(url_for("login"))

        session["user_id"] = user.id

        # 🔥 DIRETO PARA DASHBOARD
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
# DASHBOARD (PRINCIPAL)
# =====================================================

@app.route("/dashboard")
@login_required
def dashboard():

    user = get_current_user()

    # 🔒 controle simples
    if user.is_dev():
        clinics = []
    elif user.is_owner():
        clinics = Clinic.query.order_by(Clinic.id.desc()).all()
    else:
        clinics = Clinic.query.filter_by(user_id=user.id)\
                              .order_by(Clinic.id.desc()).all()

    return render_template(
        "dashboard.html",
        user=user,
        clinics=clinics
    )


# =====================================================
# CREATE PARCEIRO (CLINICA / VET)
# =====================================================

@app.route("/clinics/create", methods=["POST"])
@login_required
def create_clinic():

    user = get_current_user()

    if user.is_dev():
        flash("Sem permissão", "danger")
        return redirect(url_for("dashboard"))

    tipo = request.form.get("tipo")

    nome_clinica = request.form.get("nome_clinica", "").strip()
    nome_vet = request.form.get("nome_vet", "").strip()
    responsavel = request.form.get("responsavel", "").strip()

    email = request.form.get("email", "").strip()
    telefone = request.form.get("telefone", "").strip()
    endereco = request.form.get("endereco", "").strip()

    # validação básica
    if not all([tipo, email, telefone, endereco]):
        flash("Preencha todos os campos", "warning")
        return redirect(url_for("dashboard"))

    if tipo == "clinica":
        if not nome_clinica or not responsavel:
            flash("Informe nome da clínica e responsável", "warning")
            return redirect(url_for("dashboard"))

        nome = nome_clinica

    else:
        if not nome_vet:
            flash("Informe o nome do veterinário", "warning")
            return redirect(url_for("dashboard"))

        nome = nome_vet
        responsavel = nome_vet

    clinic = Clinic(
        nome=nome,
        responsavel=responsavel,
        tipo=tipo,
        email=email,
        telefone=telefone,
        endereco=endereco,
        user_id=user.id
    )

    db.session.add(clinic)
    db.session.commit()

    flash("Cadastro realizado com sucesso", "success")
    return redirect(url_for("dashboard"))


# =====================================================
# INIT (SAFE RAILWAY)
# =====================================================

@app.before_request
def initialize_once():
    if not hasattr(app, "initialized"):
        with app.app_context():
            init_db()
        app.initialized = True


# =====================================================
# RUN LOCAL
# =====================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
