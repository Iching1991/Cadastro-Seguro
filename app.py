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
def login():

    if request.method == "POST":

        email = request.form.get("email")
        senha = request.form.get("senha")

        user = User.query.filter_by(email=email).first()

        if not user or not bcrypt.check_password_hash(user.senha, senha):
            flash("Login inválido", "danger")
            return redirect("/")

        session["user_id"] = user.id
        session["role"] = user.role

        return redirect("/dashboard")

    return render_template("login.html")


# =====================================================
# LOGOUT
# =====================================================

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# =====================================================
# DASHBOARD
# =====================================================

@app.route("/dashboard")
@login_required
def dashboard():

    user = get_current_user()

    return render_template("dashboard.html", user=user)


# =====================================================
# CLINICS
# =====================================================

@app.route("/clinics")
@login_required
def clinics():

    user = get_current_user()

    # DEV NÃO PODE VER DADOS
    if user.is_dev():
        flash("Acesso restrito aos dados.", "danger")
        return redirect("/dashboard")

    # OWNER vê tudo
    if user.is_owner():
        data = Clinic.query.all()
    else:
        data = Clinic.query.filter_by(user_id=user.id).all()

    return render_template("clinics.html", clinics=data)


# =====================================================
# CREATE CLINIC
# =====================================================

@app.route("/clinics/create", methods=["POST"])
@login_required
def create_clinic():

    user = get_current_user()

    clinic = Clinic(
        nome=request.form.get("nome"),
        email=request.form.get("email"),
        telefone=request.form.get("telefone"),
        endereco=request.form.get("endereco"),
        user_id=user.id
    )

    db.session.add(clinic)
    db.session.commit()

    return redirect("/clinics")


# =====================================================
# SEED USERS (IMPORTANTÍSSIMO)
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
# START
# =====================================================

if __name__ == "__main__":

    with app.app_context():
        db.create_all()
        seed_users()

        # cria pasta de uploads
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        os.makedirs(app.config["LOGO_FOLDER"], exist_ok=True)

    app.run(debug=True)
