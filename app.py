from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2

app = Flask(__name__)
app.config.from_object("config.Config")

def get_db_connection():
    return psycopg2.connect(
        host=app.config['DB_HOST'],
        database=app.config['DB_NAME'],
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD']
    )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        contrasena = request.form.get("contrasena")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuario WHERE usuario = %s AND contrasena = %s", (usuario, contrasena))
        user = cursor.fetchone()
        conn.close()
        if user:
            session["user_id"] = user[0]
            session["role"] = "Administrador" if user[-1] == 1 else "Empleado"
            flash(f"Welcome, {user[1]} {user[2]}!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials!", "danger")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))

@app.route("/usuario_perfil", methods=["GET", "POST"])
def usuario_perfil():
    if "role" not in session:
        return redirect(url_for("login"))
    if session["role"] == "Empleado" and request.method == "POST":
        flash("Access Denied! Read-only access for employees.", "danger")
        return redirect(url_for("usuario_perfil"))
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == "POST":
        tipo = request.form.get("tipo")
        if tipo == "usuario":
            nombre = request.form.get("nombre")
            apellido = request.form.get("apellido")
            usuario = request.form.get("usuario")
            contrasena = request.form.get("contrasena")
            id_perfil = request.form.get("id_perfil")
            cursor.execute(
                "INSERT INTO usuario (nombre, apellido, usuario, contrasena, id_perfil) VALUES (%s, %s, %s, %s, %s)",
                (nombre, apellido, usuario, contrasena, id_perfil)
            )
        elif tipo == "perfil":
            nombre_perfil = request.form.get("nombre_perfil")
            cursor.execute("INSERT INTO perfil (nombre) VALUES (%s)", (nombre_perfil,))
        conn.commit()
        flash("Record added successfully!", "success")
    cursor.execute("SELECT * FROM usuario")
    usuarios = cursor.fetchall()
    cursor.execute("SELECT * FROM perfil")
    perfiles = cursor.fetchall()
    conn.close()
    return render_template("usuario_perfil.html", usuarios=usuarios, perfiles=perfiles)

@app.route("/usuario_perfil/edit/<string:tipo>/<int:id>", methods=["GET", "POST"])
def edit_usuario_perfil(tipo, id):
    if "role" not in session or session["role"] != "Administrador":
        flash("Access Denied! Only administrators can edit records.", "danger")
        return redirect(url_for("usuario_perfil"))
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == "POST":
        if tipo == "usuario":
            nombre = request.form.get("nombre")
            apellido = request.form.get("apellido")
            usuario = request.form.get("usuario")
            id_perfil = request.form.get("id_perfil")
            cursor.execute(
                "UPDATE usuario SET nombre = %s, apellido = %s, usuario = %s, id_perfil = %s WHERE id_usuario = %s",
                (nombre, apellido, usuario, id_perfil, id)
            )
        elif tipo == "perfil":
            nombre_perfil = request.form.get("nombre_perfil")
            cursor.execute("UPDATE perfil SET nombre = %s WHERE id_perfil = %s", (nombre_perfil, id))
        conn.commit()
        conn.close()
        flash("Record updated successfully!", "success")
        return redirect(url_for("usuario_perfil"))
    if tipo == "usuario":
        cursor.execute("SELECT * FROM usuario WHERE id_usuario = %s", (id,))
        record = cursor.fetchone()
    elif tipo == "perfil":
        cursor.execute("SELECT * FROM perfil WHERE id_perfil = %s", (id,))
        record = cursor.fetchone()
    conn.close()
    return render_template("edit_usuario_perfil.html", record=record, tipo=tipo)

@app.route("/usuario_perfil/delete/<string:tipo>/<int:id>")
def delete_usuario_perfil(tipo, id):
    if "role" not in session or session["role"] != "Administrador":
        flash("Access Denied! Only administrators can delete records.", "danger")
        return redirect(url_for("usuario_perfil"))
    conn = get_db_connection()
    cursor = conn.cursor()
    if tipo == "usuario":
        cursor.execute("DELETE FROM usuario WHERE id_usuario = %s", (id,))
    elif tipo == "perfil":
        cursor.execute("DELETE FROM perfil WHERE id_perfil = %s", (id,))
    conn.commit()
    conn.close()
    flash("Record deleted successfully!", "info")
    return redirect(url_for("usuario_perfil"))

@app.route("/empleado_departamento", methods=["GET", "POST"])
def empleado_departamento():
    if "role" not in session:
        return redirect(url_for("login"))
    if session["role"] == "Empleado" and request.method == "POST":
        flash("Access Denied! Read-only access for employees.", "danger")
        return redirect(url_for("empleado_departamento"))
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == "POST":
        tipo = request.form.get("tipo")
        if tipo == "empleado":
            nombre = request.form.get("nombre")
            apellido = request.form.get("apellido")
            telefono = request.form.get("telefono")
            direccion = request.form.get("direccion")
            fecha_nacimiento = request.form.get("fecha_nacimiento")
            observaciones = request.form.get("observaciones")
            sueldo = request.form.get("sueldo")
            id_departamento = request.form.get("id_departamento")
            cursor.execute(
                """
                INSERT INTO empleado (nombre, apellido, telefono, direccion, fecha_nacimiento, observaciones, sueldo, id_departamento)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (nombre, apellido, telefono, direccion, fecha_nacimiento, observaciones, sueldo, id_departamento)
            )
        elif tipo == "departamento":
            nombre_departamento = request.form.get("nombre_departamento")
            cursor.execute("INSERT INTO departamento (nombre) VALUES (%s)", (nombre_departamento,))
        conn.commit()
        flash("Record added successfully!", "success")
    cursor.execute("SELECT * FROM empleado")
    empleados = cursor.fetchall()
    cursor.execute("SELECT * FROM departamento")
    departamentos = cursor.fetchall()
    conn.close()
    return render_template("empleado_departamento.html", empleados=empleados, departamentos=departamentos)

@app.route("/empleado_departamento/edit/<string:tipo>/<int:id>", methods=["GET", "POST"])
def edit_empleado_departamento(tipo, id):
    if "role" not in session or session["role"] != "Administrador":
        flash("Access Denied! Only administrators can edit records.", "danger")
        return redirect(url_for("empleado_departamento"))
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == "POST":
        if tipo == "empleado":
            nombre = request.form.get("nombre")
            apellido = request.form.get("apellido")
            telefono = request.form.get("telefono")
            direccion = request.form.get("direccion")
            fecha_nacimiento = request.form.get("fecha_nacimiento")
            observaciones = request.form.get("observaciones")
            sueldo = request.form.get("sueldo")
            id_departamento = request.form.get("id_departamento")
            cursor.execute(
                """
                UPDATE empleado SET nombre = %s, apellido = %s, telefono = %s, direccion = %s,
                fecha_nacimiento = %s, observaciones = %s, sueldo = %s, id_departamento = %s
                WHERE id_empleado = %s
                """,
                (nombre, apellido, telefono, direccion, fecha_nacimiento, observaciones, sueldo, id_departamento, id)
            )
        elif tipo == "departamento":
            nombre_departamento = request.form.get("nombre_departamento")
            cursor.execute("UPDATE departamento SET nombre = %s WHERE id_departamento = %s", (nombre_departamento, id))
        conn.commit()
        conn.close()
        flash("Record updated successfully!", "success")
        return redirect(url_for("empleado_departamento"))
    if tipo == "empleado":
        cursor.execute("SELECT * FROM empleado WHERE id_empleado = %s", (id,))
        record = cursor.fetchone()
    elif tipo == "departamento":
        cursor.execute("SELECT * FROM departamento WHERE id_departamento = %s", (id,))
        record = cursor.fetchone()
    conn.close()
    return render_template("edit_empleado_departamento.html", record=record, tipo=tipo)

@app.route("/empleado_departamento/delete/<string:tipo>/<int:id>")
def delete_empleado_departamento(tipo, id):
    if "role" not in session or session["role"] != "Administrador":
        flash("Access Denied! Only administrators can delete records.", "danger")
        return redirect(url_for("empleado_departamento"))
    conn = get_db_connection()
    cursor = conn.cursor()
    if tipo == "empleado":
        cursor.execute("DELETE FROM empleado WHERE id_empleado = %s", (id,))
    elif tipo == "departamento":
        cursor.execute("DELETE FROM departamento WHERE id_departamento = %s", (id,))
    conn.commit()
    conn.close()
    flash("Record deleted successfully!", "info")
    return redirect(url_for("empleado_departamento"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)