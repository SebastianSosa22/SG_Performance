import os
import requests

from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from supabase import create_client, Client
from dotenv import load_dotenv
from auth import auth_bp, requiere_rol

# -------------------
# Cargar configuración
# -------------------
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "\u26a0\ufe0f Faltan las variables SUPABASE_URL o SUPABASE_KEY en el archivo .env o en Render")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clave-secreta-por-defecto")

# Registrar blueprint de autenticación
app.register_blueprint(auth_bp)

# -------------------
#   RUTA PRINCIPAL
# -------------------

# Inyecta 'usuario' en todas las plantillas


@app.context_processor
def inject_usuario():
    return dict(usuario=session.get("usuario"))


@app.route("/")
@requiere_rol(["administrador", "dueno", "mecanico", "hojalatero"])
def index():
    response = supabase.table("orden_servicio").select(
        "*").order("id", desc=True).execute()
    ordenes = response.data or []
    return render_template("lista_ordenes.html", ordenes=ordenes)


# -------------------
#   CREAR ORDEN
# -------------------
@app.route("/orden", methods=["GET", "POST"])
@requiere_rol(["administrador", "dueno", "mecanico", "hojalatero"])
def orden():
    if request.method == "POST":
        ingreso = request.form.get("ingreso")
        if not ingreso:
            return "⚠️ Debes ingresar la fecha de ingreso", 400

        salida = request.form.get("salida") or None

        datos = {
            "marca": request.form["marca"],
            "modelo": request.form["modelo"],
            "ano": request.form.get("ano"),
            "kilometraje": request.form["kilometraje"],
            "placas": request.form["placas"],
            "ingreso_grua": request.form.get("ingreso_grua", "No"),
            "vin": request.form.get("vin"),
            "ingreso": ingreso,
            "salida": salida,
            "nombre": request.form["nombre"],
            "telefono": request.form["telefono"],
            # "servicios": ", ".join(request.form.getlist("servicios")),
            "servicios": request.form["servicios"],
            "danos": request.form["danos"],
            "observaciones": request.form["observaciones"],
            "realizados": request.form["realizados"],
            "presupuesto": request.form["presupuesto"]
        }

        supabase.table("orden_servicio").insert(datos).execute()
        return redirect(url_for("index"))

    # Obtener servicios agrupados por categoría
    categorias_data = supabase.table(
        "categorias_servicio").select("*").execute().data
    servicios_data = supabase.table("servicios").select("*").execute().data

    # Agrupar servicios por categoría
    categorias = []
    for cat in categorias_data:
        cat_servicios = [
            s for s in servicios_data if s["categoria_id"] == cat["id"]]
        categorias.append({
            "id": cat["id"],
            "nombre": cat["nombre"],
            "servicios": cat_servicios
        })

    return render_template("orden_servicio.html", categorias=categorias)

# -------------------
#   EDITAR ORDEN
# -------------------


@app.route("/editar/<int:orden_id>", methods=["GET", "POST"])
@requiere_rol(["administrador", "dueno", "mecanico", "hojalatero"])
def editar_orden(orden_id):
    if request.method == "POST":
        datos = {
            "marca": request.form["marca"],
            "modelo": request.form["modelo"],
            "ano": request.form.get("ano"),
            "nombre": request.form["nombre"],
            "telefono": request.form["telefono"],
            "placas": request.form["placas"],
            "vin": request.form.get("vin"),
            "kilometraje": request.form.get("kilometraje"),
            "ingreso_grua": request.form.get("ingreso_grua", "No"),
            "ingreso": request.form.get("ingreso"),
            # Aquí se actualiza siempre
            "salida": request.form.get("salida") if request.form.get("salida") else None,
            # "servicios": ", ".join(request.form.getlist("servicios")),
            "servicios": request.form["servicios"],
            "danos": request.form["danos"],
            "observaciones": request.form["observaciones"],
            "realizados": request.form["realizados"],
            "presupuesto": request.form["presupuesto"]
        }

        supabase.table("orden_servicio").update(
            datos).eq("id", orden_id).execute()
        return redirect(url_for("index"))

    orden = supabase.table("orden_servicio").select(
        "*").eq("id", orden_id).single().execute().data
    return render_template("editar_orden.html", orden=orden)


# -------------------
#   DETALLE ORDEN
# -------------------
@app.route("/orden/<int:orden_id>")
@requiere_rol(["administrador", "dueno", "mecanico", "hojalatero"])
def detalle(orden_id):
    orden = supabase.table("orden_servicio").select(
        "*").eq("id", orden_id).single().execute().data
    checklist_data = supabase.table("checklist").select(
        "*").eq("orden_id", orden_id).execute().data
    checklist = checklist_data[0] if checklist_data else None
    return render_template("detalle_orden.html", orden=orden, checklist=checklist)


# -------------------
#   BORRAR ORDEN
# -------------------
@app.route("/borrar/<int:orden_id>")
@requiere_rol(["administrador", "dueno", "mecanico", "hojalatero"])
def borrar(orden_id):
    supabase.table("orden_servicio").delete().eq("id", orden_id).execute()
    return redirect(url_for("index"))

# -------------------
#   ACTUALIZAR  ORDEN
# -------------------


@app.route('/ordenes/actualizar/<int:id>', methods=['POST'])
def actualizar_orden(id):
    # lógica para guardar cambios
    ...


# -------------------
#   CHECKLIST
# -------------------
@app.route("/checklist/<int:orden_id>", methods=["GET", "POST"])
@requiere_rol(["administrador", "dueno", "mecanico", "hojalatero"])
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
#   BUSCAR VIN
# -------------------


@app.route("/api/vin/<vin>")
def buscar_vin(vin):
    try:
        url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvaluesextended/{vin}?format=json"
        r = requests.get(url)
        data = r.json()

        if "Results" not in data or not data["Results"]:
            return jsonify({"error": "No se encontró información para este VIN"}), 404

        result = data["Results"][0]

        return jsonify({
            "marca": result.get("Make"),
            "modelo": result.get("Model"),
            "ano": result.get("ModelYear"),
            "carroceria": result.get("BodyClass"),
            "puertas": result.get("Doors"),
            "motor": result.get("EngineModel"),
            "cilindrada": result.get("DisplacementL"),
            "cilindros": result.get("EngineCylinders"),
            "combustible": result.get("FuelTypePrimary"),
            "transmision": result.get("TransmissionStyle"),
            "ensamblaje": f"{result.get('PlantCity')}, {result.get('PlantCountry')}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------
#   MAIN
# -------------------
if __name__ == "__main__":
    app.run(debug=True)
