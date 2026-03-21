from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv
import os
import db

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clave-secreta-dev")
db.init_app(app)



def login_requerido(f):
    from functools import wraps
    @wraps(f)
    def decorado(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorado



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario  = request.form["usuario"]
        password = request.form["password"]
        if usuario == os.getenv("ADMIN_USER", "admin") and \
           password == os.getenv("ADMIN_PASSWORD", "admin123"):
            session["admin"] = True
            return redirect(url_for("dashboard"))
        flash("Usuario o contraseña incorrectos", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_requerido
def dashboard():
    stats = {
        "pacientes":       db.query("SELECT COUNT(*) AS n FROM pacientes",    fetch="one")["n"],
        "cuidadores":      db.query("SELECT COUNT(*) AS n FROM cuidadores",   fetch="one")["n"],
        "dispositivos":    db.query("SELECT COUNT(*) AS n FROM dispositivos", fetch="one")["n"],
        "alertas_activas": db.query(
            "SELECT COUNT(*) AS n FROM alertas WHERE estatus_alerta = 'Activa'",
            fetch="one")["n"],
    }
    alertas_recientes = db.query("""
        SELECT a.tipo_alerta,
               a.estatus_alerta,
               a.fecha_hora_lectura,
               p.nombre_paciente || ' ' || p.apellido_p_pac AS paciente
        FROM alertas a
        JOIN pacientes p ON p.id_paciente = a.id_paciente
        ORDER BY a.fecha_hora_lectura DESC
        LIMIT 5
    """)
    return render_template("dashboard.html", stats=stats, alertas=alertas_recientes)



@app.route("/pacientes")
@login_requerido
def pacientes_lista():
    pacientes = db.query("""
        SELECT p.id_paciente,
               p.nombre_paciente,
               p.apellido_p_pac,
               p.apellido_m_pac,
               p.fecha_nacimiento,
               ep.desc_estado
        FROM pacientes p
        JOIN estados_paciente ep ON ep.id_estado = p.id_estado
        ORDER BY p.id_paciente
    """)
    return render_template("pacientes/list.html", pacientes=pacientes)


@app.route("/pacientes/nuevo", methods=["GET", "POST"])
@login_requerido
def pacientes_nuevo():
    estados = db.query("SELECT * FROM estados_paciente ORDER BY id_estado")
    if request.method == "POST":
        db.execute("""
            INSERT INTO pacientes
                (id_paciente, nombre_paciente, apellido_p_pac, apellido_m_pac,
                 fecha_nacimiento, id_estado)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            request.form["id_paciente"],
            request.form["nombre_paciente"],
            request.form["apellido_p_pac"],
            request.form["apellido_m_pac"],
            request.form["fecha_nacimiento"],
            request.form["id_estado"],
        ))
        flash("Paciente registrado correctamente.", "success")
        return redirect(url_for("pacientes_lista"))
    return render_template("pacientes/form.html", paciente=None, estados=estados)


@app.route("/pacientes/editar/<int:id>", methods=["GET", "POST"])
@login_requerido
def pacientes_editar(id):
    estados  = db.query("SELECT * FROM estados_paciente ORDER BY id_estado")
    paciente = db.query("SELECT * FROM pacientes WHERE id_paciente = %s", (id,), fetch="one")
    if request.method == "POST":
        db.execute("""
            UPDATE pacientes
            SET nombre_paciente  = %s,
                apellido_p_pac   = %s,
                apellido_m_pac   = %s,
                fecha_nacimiento = %s,
                id_estado        = %s
            WHERE id_paciente = %s
        """, (
            request.form["nombre_paciente"],
            request.form["apellido_p_pac"],
            request.form["apellido_m_pac"],
            request.form["fecha_nacimiento"],
            request.form["id_estado"],
            id,
        ))
        flash("Paciente actualizado correctamente.", "success")
        return redirect(url_for("pacientes_lista"))
    return render_template("pacientes/form.html", paciente=paciente, estados=estados)


@app.route("/pacientes/eliminar/<int:id>", methods=["POST"])
@login_requerido
def pacientes_eliminar(id):
    db.execute("DELETE FROM pacientes WHERE id_paciente = %s", (id,))
    flash("Paciente eliminado.", "success")
    return redirect(url_for("pacientes_lista"))


@app.route("/cuidadores")
@login_requerido
def cuidadores_lista():
    cuidadores = db.query("""
        SELECT id_cuidador,
               nombre_cuidador,
               apellido_p_cuid,
               apellido_m_cuid,
               telefono_cuid
        FROM cuidadores
        ORDER BY id_cuidador
    """)
    return render_template("cuidadores/list.html", cuidadores=cuidadores)


@app.route("/cuidadores/nuevo", methods=["GET", "POST"])
@login_requerido
def cuidadores_nuevo():
    if request.method == "POST":
        db.execute("""
            INSERT INTO cuidadores
                (id_cuidador, nombre_cuidador, apellido_p_cuid, apellido_m_cuid, telefono_cuid)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            request.form["id_cuidador"],
            request.form["nombre_cuidador"],
            request.form["apellido_p_cuid"],
            request.form["apellido_m_cuid"],
            request.form["telefono_cuid"],
        ))
        flash("Cuidador registrado correctamente.", "success")
        return redirect(url_for("cuidadores_lista"))
    return render_template("cuidadores/form.html", cuidador=None)


@app.route("/cuidadores/editar/<int:id>", methods=["GET", "POST"])
@login_requerido
def cuidadores_editar(id):
    cuidador = db.query("SELECT * FROM cuidadores WHERE id_cuidador = %s", (id,), fetch="one")
    if request.method == "POST":
        db.execute("""
            UPDATE cuidadores
            SET nombre_cuidador = %s,
                apellido_p_cuid = %s,
                apellido_m_cuid = %s,
                telefono_cuid   = %s
            WHERE id_cuidador = %s
        """, (
            request.form["nombre_cuidador"],
            request.form["apellido_p_cuid"],
            request.form["apellido_m_cuid"],
            request.form["telefono_cuid"],
            id,
        ))
        flash("Cuidador actualizado correctamente.", "success")
        return redirect(url_for("cuidadores_lista"))
    return render_template("cuidadores/form.html", cuidador=cuidador)


@app.route("/cuidadores/eliminar/<int:id>", methods=["POST"])
@login_requerido
def cuidadores_eliminar(id):
    db.execute("DELETE FROM cuidadores WHERE id_cuidador = %s", (id,))
    flash("Cuidador eliminado.", "success")
    return redirect(url_for("cuidadores_lista"))



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
