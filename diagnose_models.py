# diagnose_models.py

import traceback

from flask import Flask
from config import Config
from models import db, User, Clinic

# =====================================================
# APP TEMPORÁRIO
# =====================================================

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# =====================================================
# DIAGNÓSTICO
# =====================================================

def diagnose():

    print("\n🔍 DIAGNÓSTICO DO MODELS.PY")
    print("=" * 50)

    with app.app_context():

        try:
            print("📡 Testando conexão com banco...")
            engine = db.engine
            print(f"✅ Conectado em: {engine.url}")

        except Exception as e:
            print("❌ ERRO na conexão:")
            traceback.print_exc()
            return

        # -------------------------------------------------

        try:
            print("\n🧱 Criando tabelas...")
            db.create_all()
            print("✅ Tabelas criadas com sucesso")

        except Exception:
            print("❌ ERRO ao criar tabelas:")
            traceback.print_exc()
            return

        # -------------------------------------------------

        try:
            print("\n📋 Listando tabelas...")

            tables = db.metadata.tables.keys()

            for t in tables:
                print(f"   • {t}")

            if not tables:
                print("⚠️ Nenhuma tabela encontrada")

        except Exception:
            print("❌ ERRO ao listar tabelas:")
            traceback.print_exc()

        # -------------------------------------------------

        try:
            print("\n👤 Testando model User...")

            user = User(
                nome="Teste",
                email="teste@teste.com",
                senha="123"
            )

            db.session.add(user)
            db.session.commit()

            print("✅ Insert User OK")

        except Exception:
            print("❌ ERRO no model User:")
            traceback.print_exc()
            db.session.rollback()

        # -------------------------------------------------

        try:
            print("\n🏥 Testando model Clinic...")

            clinic = Clinic(
                nome="Clínica Teste",
                email="clinic@test.com",
                telefone="0000",
                endereco="Rua Teste"
            )

            db.session.add(clinic)
            db.session.commit()

            print("✅ Insert Clinic OK")

        except Exception:
            print("❌ ERRO no model Clinic:")
            traceback.print_exc()
            db.session.rollback()

        # -------------------------------------------------

        print("\n✅ DIAGNÓSTICO FINALIZADO")


# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":
    diagnose()
