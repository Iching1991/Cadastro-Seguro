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

# =====================================================

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt = Bcrypt(app)

# =====================================================
# HELPERS
# =====================================================

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated


def allowed_file(filename):
    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() \
        in app.config["ALLOWED_EXTENSIONS"]

# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")

# =====================================================
# LOGIN
# =====================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        senha = request.form["senha"]

        user = User.query.filter_by(email=email).first()

        if not user or \
           not bcrypt.check_password_hash(user.senha, senha):

            flash("Credenciais inválidas")
            return redirect("/login")

        session["user"] = user.id
        return redirect("/dashboard")

    return render_template("login.html")

# =====================================================
# LOGOUT
# =====================================================

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# =====================================================
# REGISTER
# =====================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        senha_hash = bcrypt.generate_password_hash(
            request.form["senha"]
        ).decode()

        user = User(
            nome=request.form["nome"],
            email=request.form["email"],
            senha=senha_hash
        )

        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")

# =====================================================
# DASHBOARD
# =====================================================

@app.route("/dashboard")
@login_required
def dashboard():

    total = Clinic.query.count()

    return render_template(
        "dashboard.html",
        total=total
    )

# =====================================================
# LIST CLINICS
# =====================================================

@app.route("/clinics")
@login_required
def clinics():

    data = Clinic.query.all()

    return render_template(
        "clinics.html",
        clinics=data
    )

# =====================================================
# CREATE CLINIC + LOGO
# =====================================================

@app.route("/clinics/create", methods=["POST"])
@login_required
def create_clinic():

    file = request.files.get("logo")
    filename = None

    if file and allowed_file(file.filename):

        filename = secure_filename(file.filename)

        path = os.path.join(
            app.config["LOGO_FOLDER"],
            filename
        )

        os.makedirs(
            app.config["LOGO_FOLDER"],
            exist_ok=True
        )

        file.save(path)

    clinic = Clinic(
        nome=request.form["nome"],
        email=request.form["email"],
        telefone=request.form["telefone"],
        endereco=request.form["endereco"],
        logo=filename,
        user_id=session["user"]
    )

    db.session.add(clinic)
    db.session.commit()

    return redirect("/clinics")

# =====================================================
# DELETE
# =====================================================

@app.route("/clinics/delete/<id>")
@login_required
def delete_clinic(id):

    clinic = Clinic.query.get_or_404(id)

    db.session.delete(clinic)
    db.session.commit()

    return redirect("/clinics")

# =====================================================
# SERVE LOGOS
# =====================================================

@app.route("/uploads/logos/<filename>")
def get_logo(filename):
    return send_from_directory(
        app.config["LOGO_FOLDER"],
        filename
    )

# =====================================================
# START
# =====================================================

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)
