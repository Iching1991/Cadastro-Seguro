from flask import (
    Flask, render_template, request,
    redirect, session, url_for,
    flash, send_from_directory
)
from flask_bcrypt import Bcrypt
from functools import wraps
import os

from config import Config
from models import db, User, Clinic
from werkzeug.utils import secure_filename

# ─────────────────────────────────────────────
# INICIALIZAÇÃO
# ─────────────────────────────────────────────
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt = Bcrypt(app)


# ─────────────────────────────────────────────
# DECORATORS
# ─────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Faça login para continuar.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Faça login para continuar.", "warning")
            return redirect(url_for("login"))
        user = db.session.get(User, session["user_id"])
        if not user or not user.is_admin:
            flash("Acesso restrito ao administrador.", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated


def allowed_file(filename: str) -> bool:
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower()
        in app.config.get("ALLOWED_EXTENSIONS", {"png", "jpg", "jpeg", "gif", "webp"})
    )


def get_current_user() -> User | None:
    return db.session.get(User, session.get("user_id"))


# ─────────────────────────────────────────────
# HOME
# ─────────────────────────────────────────────
@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# ─────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        if not email or not senha:
            flash("Preencha todos os campos.", "warning")
            return redirect(url_for("login"))

        user = User.query.filter_by(email=email).first()

        if not user or not bcrypt.check_password_hash(user.senha, senha):
            flash("E-mail ou senha incorretos.", "danger")
            return redirect(url_for("login"))

        if not user.aprovado:
            flash("Sua conta ainda não foi aprovada pelo administrador.", "warning")
            return redirect(url_for("login"))

        session["user_id"]   = user.id
        session["user_nome"] = user.nome
        session["is_admin"]  = user.is_admin

        flash(f"Bem-vindo, {user.nome}!", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


# ─────────────────────────────────────────────
# LOGOUT
# ─────────────────────────────────────────────
@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Sessão encerrada com sucesso.", "info")
    return redirect(url_for("login"))


# ─────────────────────────────────────────────
# REGISTRO
# ─────────────────────────────────────────────
@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        nome  = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        conf  = request.form.get("confirmar_senha", "")

        # Validações
        if not all([nome, email, senha, conf]):
            flash("Preencha todos os campos.", "warning")
            return redirect(url_for("register"))

        if senha != conf:
            flash("As senhas não conferem.", "danger")
            return redirect(url_for("register"))

        if len(senha) < 6:
            flash("Senha mínima: 6 caracteres.", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("E-mail já cadastrado.", "danger")
            return redirect(url_for("register"))

        senha_hash = bcrypt.generate_password_hash(senha).decode("utf-8")

        user = User(
            nome=nome,
            email=email,
            senha=senha_hash,
            aprovado=False,
            is_admin=False
        )

        db.session.add(user)
        db.session.commit()

        flash("Cadastro realizado! Aguarde a aprovação do administrador.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────
@app.route("/dashboard")
@login_required
def dashboard():
    user  = get_current_user()
    total = Clinic.query.count()

    # Admin vê todas; operador vê só as suas
    if user.is_admin:
        recentes = Clinic.query.order_by(Clinic.id.desc()).limit(5).all()
    else:
        recentes = (
            Clinic.query
            .filter_by(user_id=user.id)
            .order_by(Clinic.id.desc())
            .limit(5)
            .all()
        )

    return render_template(
        "dashboard.html",
        user=user,
        total=total,
        recentes=recentes
    )


# ─────────────────────────────────────────────
# LISTAR PARCEIROS
# ─────────────────────────────────────────────
@app.route("/clinics")
@login_required
def clinics():
    user = get_current_user()

    if user.is_admin:
        data = Clinic.query.order_by(Clinic.nome).all()
    else:
        data = (
            Clinic.query
            .filter_by(user_id=user.id)
            .order_by(Clinic.nome)
            .all()
        )

    return render_template("clinics.html", clinics=data, user=user)


# ─────────────────────────────────────────────
# CRIAR PARCEIRO
# ─────────────────────────────────────────────
@app.route("/clinics/create", methods=["GET", "POST"])
@login_required
def create_clinic():
    if request.method == "POST":
        nome     = request.form.get("nome", "").strip()
        email    = request.form.get("email", "").strip().lower()
        telefone = request.form.get("telefone", "").strip()
        endereco = request.form.get("endereco", "").strip()

        if not all([nome, email, telefone, endereco]):
            flash("Preencha todos os campos obrigatórios.", "warning")
            return redirect(url_for("create_clinic"))

        # Logo (opcional)
        filename = None
        file = request.files.get("logo")

        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            logo_folder = app.config.get("LOGO_FOLDER", "uploads/logos")
            os.makedirs(logo_folder, exist_ok=True)
            file.save(os.path.join(logo_folder, filename))

        clinic = Clinic(
            nome=nome,
            email=email,
            telefone=telefone,
            endereco=endereco,
            logo=filename,
            user_id=session["user_id"]
        )

        db.session.add(clinic)
        db.session.commit()

        flash(f"Parceiro '{nome}' cadastrado com sucesso!", "success")
        return redirect(url_for("clinics"))

    return render_template("create_clinic.html")


# ─────────────────────────────────────────────
# EDITAR PARCEIRO
# ─────────────────────────────────────────────
@app.route("/clinics/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_clinic(id):
    clinic = db.session.get(Clinic, id)
    user   = get_current_user()

    if not clinic:
        flash("Parceiro não encontrado.", "danger")
        return redirect(url_for("clinics"))

    # Só o dono ou admin pode editar
    if clinic.user_id != user.id and not user.is_admin:
        flash("Sem permissão para editar este parceiro.", "danger")
        return redirect(url_for("clinics"))

    if request.method == "POST":
        clinic.nome     = request.form.get("nome", clinic.nome).strip()
        clinic.email    = request.form.get("email", clinic.email).strip().lower()
        clinic.telefone = request.form.get("telefone", clinic.telefone).strip()
        clinic.endereco = request.form.get("endereco", clinic.endereco).strip()

        file = request.files.get("logo")
        if file and file.filename and allowed_file(file.filename):
            filename    = secure_filename(file.filename)
            logo_folder = app.config.get("LOGO_FOLDER", "uploads/logos")
            os.makedirs(logo_folder, exist_ok=True)
            file.save(os.path.join(logo_folder, filename))
            clinic.logo = filename

        db.session.commit()
        flash(f"Parceiro '{clinic.nome}' atualizado!", "success")
        return redirect(url_for("clinics"))

    return render_template("edit_clinic.html", clinic=clinic)


# ─────────────────────────────────────────────
# DELETAR PARCEIRO
# ─────────────────────────────────────────────
@app.route("/clinics/delete/<int:id>", methods=["POST"])
@login_required
def delete_clinic(id):
    clinic = db.session.get(Clinic, id)
    user   = get_current_user()

    if not clinic:
        flash("Parceiro não encontrado.", "danger")
        return redirect(url_for("clinics"))

    if clinic.user_id != user.id and not user.is_admin:
        flash("Sem permissão para excluir este parceiro.", "danger")
        return redirect(url_for("clinics"))

    db.session.delete(clinic)
    db.session.commit()

    flash("Parceiro removido com sucesso.", "success")
    return redirect(url_for("clinics"))


# ─────────────────────────────────────────────
# PAINEL DO ADMIN — USUÁRIOS PENDENTES
# ─────────────────────────────────────────────
@app.route("/admin/users")
@admin_required
def admin_users():
    pendentes = User.query.filter_by(aprovado=False, is_admin=False).all()
    todos     = User.query.filter_by(is_admin=False).order_by(User.nome).all()

    return render_template(
        "admin_users.html",
        pendentes=pendentes,
        todos=todos
    )


@app.route("/admin/users/approve/<int:id>", methods=["POST"])
@admin_required
def approve_user(id):
    user = db.session.get(User, id)

    if not user:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for("admin_users"))

    user.aprovado = True
    db.session.commit()

    flash(f"Usuário '{user.nome}' aprovado com sucesso!", "success")
    return redirect(url_for("admin_users"))


@app.route("/admin/users/delete/<int:id>", methods=["POST"])
@admin_required
def delete_user(id):
    user = db.session.get(User, id)

    if not user:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for("admin_users"))

    db.session.delete(user)
    db.session.commit()

    flash("Usuário removido.", "success")
    return redirect(url_for("admin_users"))


# ─────────────────────────────────────────────
# SERVIR LOGOS
# ─────────────────────────────────────────────
@app.route("/uploads/logos/<filename>")
def get_logo(filename):
    return send_from_directory(
        app.config.get("LOGO_FOLDER", "uploads/logos"),
        filename
    )


# ─────────────────────────────────────────────
# START
# ─────────────────────────────────────────────
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
