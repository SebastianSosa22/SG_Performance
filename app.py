from flask import Flask, render_template, request, redirect, url_for
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env
load_dotenv()

# Conexión a Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "⚠️ Faltan las variables SUPABASE_URL o SUPABASE_KEY en el archivo .env o en Render")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)


# -------------------
#   RUTA PRINCIPAL
# -------------------
@app.route("/")
def index():
    response = supabase.table("orden_servicio").select(
        "*").order("id", desc=True).execute()
    ordenes = response.data if response.data else []
    return render_template("lista_ordenes.html", ordenes=ordenes)


# -------------------
#   CREAR ORDEN
# -------------------
@app.route("/orden", methods=["GET", "POST"])
def orden():
    if request.method == "POST":
        ingreso = request.form.get("ingreso")
        if not ingreso:
            return "⚠️ Debes ingresar la fecha de ingreso", 400

        # Convertir salida vacía a None
        salida = request.form.get("salida") or None

        datos = {
            "marca": request.form["marca"],
            "modelo": request.form["modelo"],
            "ano": request.form.get("ano"),
            "kilometraje": request.form["kilometraje"],
            "placas": request.form["placas"],
            "ingreso_grua": request.form.get("ingreso_grua", "No"),
            "vin": request.form.get("vin"),
            "ingreso": ingreso,       # obligatorio
            "salida": salida,         # opcional
            "nombre": request.form["nombre"],
            "telefono": request.form["telefono"],
            "servicios": ", ".join(request.form.getlist("servicios")),
            "danos": request.form["danos"],
            "observaciones": request.form["observaciones"],
            "realizados": request.form["realizados"],
            "presupuesto": request.form["presupuesto"]
        }

        supabase.table("orden_servicio").insert(datos).execute()
        return redirect(url_for("index"))

    return render_template("orden_servicio.html")


# -------------------
#   DETALLE ORDEN
# -------------------
@app.route("/orden/<int:orden_id>")
def detalle(orden_id):
    response = supabase.table("orden_servicio").select(
        "*").eq("id", orden_id).single().execute()
    orden = response.data

    checklist = supabase.table("checklist").select(
        "*").eq("orden_id", orden_id).execute()
    checklist_data = checklist.data[0] if checklist.data else None

    return render_template("detalle_orden.html", orden=orden, checklist=checklist_data)


# -------------------
#   BORRAR ORDEN
# -------------------
@app.route("/borrar/<int:orden_id>")
def borrar(orden_id):
    supabase.table("orden_servicio").delete().eq("id", orden_id).execute()
    return redirect(url_for("index"))


# -------------------
#   CHECKLIST
# -------------------
@app.route("/checklist/<int:orden_id>", methods=["GET", "POST"])
def checklist(orden_id):
    if request.method == "POST":
        datos = {
            "orden_id": orden_id,
            "mecanico": request.form["mecanico"],
            "motor": ", ".join(request.form.getlist("motor")),
            "frenos": ", ".join(request.form.getlist("frenos")),
            "transmision": ", ".join(request.form.getlist("transmision")),
            "llantas": ", ".join(request.form.getlist("llantas")),
            "luces": ", ".join(request.form.getlist("luces")),
            "electrico": ", ".join(request.form.getlist("electrico")),
            "tablero": ", ".join(request.form.getlist("tablero")),
            "seguridad": ", ".join(request.form.getlist("seguridad")),
            "observaciones_motor": request.form["observaciones_motor"],
            "observaciones_frenos": request.form["observaciones_frenos"],
            "observaciones_transmision": request.form["observaciones_transmision"],
            "observaciones_llantas": request.form["observaciones_llantas"],
            "observaciones_luces": request.form["observaciones_luces"],
            "observaciones_electrico": request.form["observaciones_electrico"],
            "observaciones_seguridad": request.form["observaciones_seguridad"]
        }
        supabase.table("checklist").insert(datos).execute()
        return redirect(url_for("detalle", orden_id=orden_id))

    return render_template("checklist.html", orden_id=orden_id)


# -------------------
#   MAIN
# -------------------
if __name__ == "__main__":
    app.run(debug=True)
