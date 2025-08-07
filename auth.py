from flask import Blueprint, render_template, request, redirect, url_for, session
from functools import wraps
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("\u26a0\ufe0f Faltan SUPABASE_URL o SUPABASE_KEY en .env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

auth_bp = Blueprint("auth", __name__)

# -----------------------------
# Decorador para verificar rol
# -----------------------------


def requiere_rol(roles_permitidos):
    def decorador(f):
        @wraps(f)
        def funcion_envuelta(*args, **kwargs):
            usuario = session.get("usuario")
            if not usuario or usuario.get("rol") not in roles_permitidos:
                return redirect(url_for("auth.login"))
            return f(*args, **kwargs)
        return funcion_envuelta
    return decorador

# -------------------
# Ruta de Login
# -------------------


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        try:
            session_data = supabase.auth.sign_in_with_password(
                {"email": email, "password": password})
            user = session_data.user
            if user:
                usuario_data = supabase.table("usuarios").select(
                    "*").eq("correo", email).single().execute()
                usuario = usuario_data.data
                session["usuario"] = {
                    "correo": usuario["correo"],
                    "nombre": usuario.get("nombre", ""),
                    "rol": usuario["rol"]
                }
                return redirect(url_for("index"))
            return "Usuario o contrase\u00f1a incorrectos", 401
        except Exception as e:
            return f"Error al iniciar sesi\u00f3n: {e}", 500
    return render_template("login.html")

# ----------------------
# Ruta de Registro
# ----------------------


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        nombre = request.form["nombre"]
        rol = request.form["rol"]
        try:
            supabase.auth.sign_up({"email": email, "password": password})
            supabase.table("usuarios").insert(
                {"correo": email, "nombre": nombre, "rol": rol}).execute()
            return redirect(url_for("auth.login"))
        except Exception as e:
            return f"Error al registrar: {e}", 500
    return render_template("register.html")

# -------------------
# Ruta de Logout
# -------------------


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
