# diagnose_models.py

import traceback

from flask import Flask

from config import Config
from models import db, User, Clinic


# ─────────────────────────────────────────────
# APP TEMPORÁRIO
# ─────────────────────────────────────────────
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def print_section(title):

    print("\n" + "─" * 50)
    print(title)
    print("─" * 50)


def safe_run(title, func):

    print_section(title)

    try:
        func()
        print("✅ OK")

    except Exception:
        print("❌ ERRO")
        traceback.print_exc()
        db.session.rollback()


# ─────────────────────────────────────────────
# TESTES
# ─────────────────────────────────────────────
def test_connection():

    engine = db.engine

    print(f"📡 Conectado em: {engine.url}")


def test_create_tables():

    db.create_all()

    print("🧱 Tabelas criadas")


def test_list_tables():

    tables = list(db.metadata.tables.keys())

    if not tables:
        print("⚠️ Nenhuma tabela encontrada")

    for table in tables:
        print(f"• {table}")


def test_user_insert():

    user = User(
        nome="Teste",
        email="teste@teste.com",
        senha="123",
        aprovado=True
    )

    db.session.add(user)
    db.session.commit()

    print(f"👤 User criado ID={user.id}")

    return user


def test_clinic_insert(user):

    clinic = Clinic(
        nome="Clínica Teste",
        email="clinic@test.com",
        telefone="0000",
        endereco="Rua Teste",
        user_id=user.id
    )

    db.session.add(clinic)
    db.session.commit()

    print(f"🏥 Clinic criada ID={clinic.id}")


# ─────────────────────────────────────────────
# DIAGNÓSTICO
# ─────────────────────────────────────────────
def diagnose():

    print("\n🔍 DIAGNÓSTICO DO BANCO")
    print("=" * 50)

    with app.app_context():

        safe_run(
            "📡 Testando conexão com banco",
            test_connection
        )

        safe_run(
            "🧱 Criando tabelas",
            test_create_tables
        )

        safe_run(
            "📋 Listando tabelas",
            test_list_tables
        )

        user = None

        try:

            print_section("👤 Testando model User")

            user = test_user_insert()

            print("✅ Insert User OK")

        except Exception:

            print("❌ ERRO no model User")

            traceback.print_exc()

            db.session.rollback()

        if user:

            try:

                print_section("🏥 Testando model Clinic")

                test_clinic_insert(user)

                print("✅ Insert Clinic OK")

            except Exception:

                print("❌ ERRO no model Clinic")

                traceback.print_exc()

                db.session.rollback()

        print("\n🎯 DIAGNÓSTICO FINALIZADO")


# ─────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────
if __name__ == "__main__":

    diagnose()
