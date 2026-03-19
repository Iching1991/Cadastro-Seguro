from flask import Flask, render_template, request, redirect, session, url_for, flash, Response
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
# INIT DATABASE (CORRIGIDO E FORÇADO)
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

        user = User.query.filter_by(nome=nome).first()
        senha_hash = bcrypt.generate_password_hash(senha).decode()

        if user:
            # 🔥 FORÇA ATUALIZAÇÃO SEMPRE (CORREÇÃO DO SEU BUG)
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
    if not user_id:
        return None
    return db.session.get(User, user_id)


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
# EXPORTAR CSV (CORRIGIDO)
# =====================================================

@app.route("/export")
@login_required
def export_data():

    user = get_current_user()

    # 🔥 PROTEÇÃO REAL
    if not user or user.role.lower() != "owner":
        flash("Acesso restrito", "danger")
        return redirect(url_for("dashboard"))

    clinics = Clinic.query.all()

    output = "Nome,Responsavel,Tipo,Email,Telefone,Endereco\n"

    for c in clinics:
        output += f"{c.nome},{c.responsavel},{c.tipo},{c.email},{c.telefone},{c.endereco}\n"

    return Response(
        output,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=parceiros.csv"
        }
    )


# =====================================================
# PAINEL DEV
# =====================================================

@app.route("/dev")
@login_required
def dev_panel():

    user = get_current_user()

    if not user or user.role.lower() != "dev":
        flash("Acesso restrito", "danger")
        return redirect(url_for("dashboard"))

    total_users = User.query.count()
    total_clinics = Clinic.query.count()

    return render_template(
        "dev.html",
        total_users=total_users,
        total_clinics=total_clinics
    )


# =====================================================
# ALTERAR SENHA
# =====================================================

@app.route("/change-password", methods=["POST"])
@login_required
def change_password():

    user = get_current_user()

    atual = request.form.get("senha_atual", "")
    nova = request.form.get("nova_senha", "")

    if not atual or not nova:
        flash("Preencha os campos", "warning")
        return redirect(url_for("dashboard"))

    if not bcrypt.check_password_hash(user.senha, atual):
        flash("Senha atual incorreta", "danger")
        return redirect(url_for("dashboard"))

    user.senha = bcrypt.generate_password_hash(nova).decode()
    db.session.commit()

    flash("Senha alterada com sucesso", "success")
    return redirect(url_for("dashboard"))


# =====================================================
# CREATE PARCEIRO
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
# INIT (CORRIGIDO - EXECUTA UMA VEZ)
# =====================================================

with app.app_context():
    init_db()


# =====================================================
# RUN LOCAL
# =====================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
