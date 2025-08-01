from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Inicializar la base de datos


def init_db():
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orden_servicio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT,
            modelo TEXT,
            ano TEXT,
            kilometraje TEXT,
            placas TEXT,
            ingreso_grua TEXT,
            vin TEXT,
            ingreso TEXT,
            salida TEXT,
            nombre TEXT,
            telefono TEXT,
            servicios TEXT,
            danos TEXT,
            observaciones TEXT,
            realizados TEXT,
            presupuesto TEXT
        )
    ''')
    conn.commit()
    conn.close()


@app.route("/orden", methods=["GET", "POST"])
def orden():
    if request.method == "POST":
        datos = (
            request.form["marca"],
            request.form["modelo"],
            request.form["ano"],
            request.form["kilometraje"],
            request.form["placas"],
            request.form.get("ingreso_grua", "No"),
            request.form["vin"],
            request.form["ingreso"],
            request.form["salida"],
            request.form["nombre"],
            request.form["telefono"],
            ", ".join(request.form.getlist("servicios")),
            request.form["danos"],
            request.form["observaciones"],
            request.form["realizados"],
            request.form["presupuesto"]
        )
        conn = sqlite3.connect("db.sqlite3")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orden_servicio 
            (marca, modelo, ano, kilometraje, placas, ingreso_grua, vin, ingreso, salida, nombre, telefono,
             servicios, danos, observaciones, realizados, presupuesto)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', datos)
        conn.commit()
        conn.close()
        return redirect(url_for("ordenes"))

    return render_template("orden_servicio.html")


@app.route("/")
def index():
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orden_servicio ORDER BY id DESC")
    ordenes = cursor.fetchall()
    conn.close()
    return render_template("lista_ordenes.html", ordenes=ordenes)


@app.route("/orden/<int:orden_id>")
def detalle(orden_id):
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orden_servicio WHERE id = ?", (orden_id,))
    orden = cursor.fetchone()
    conn.close()
    return render_template("detalle_orden.html", orden=orden)


@app.route("/borrar/<int:orden_id>")
def borrar(orden_id):
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orden_servicio WHERE id = ?", (orden_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("ordenes"))


@app.route("/checklist/<int:orden_id>", methods=["GET", "POST"])
def checklist(orden_id):
    if request.method == "POST":
        datos = (
            orden_id,
            request.form["mecanico"],
            request.form.getlist("motor"),
            request.form.getlist("frenos"),
            request.form.getlist("transmision"),
            request.form.getlist("llantas"),
            request.form.getlist("luces"),
            request.form.getlist("electrico"),
            request.form.getlist("tablero"),
            request.form.getlist("seguridad"),
            request.form["observaciones_motor"],
            request.form["observaciones_frenos"],
            request.form["observaciones_transmision"],
            request.form["observaciones_llantas"],
            request.form["observaciones_luces"],
            request.form["observaciones_electrico"],
            request.form["observaciones_seguridad"]
        )
        conn = sqlite3.connect("db.sqlite3")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO checklist
            (orden_id, mecanico, motor, frenos, transmision, llantas, luces, electrico, tablero, seguridad,
            observaciones_motor, observaciones_frenos, observaciones_transmision, observaciones_llantas,
            observaciones_luces, observaciones_electrico, observaciones_seguridad)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', datos)
        conn.commit()
        conn.close()
        return redirect(url_for("detalle", orden_id=orden_id))
    return render_template("checklist.html", orden_id=orden_id)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
