from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2

app = Flask(__name__)
app.config.from_object("config.Config")


def get_db_connection():
    conn = psycopg2.connect(
        host=app.config['DB_HOST'],
        database=app.config['DB_NAME'],
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD']
    )
    return conn

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            flash("Welcome, " + username + "!", "success")
            return redirect(url_for("index"))  # Redirigir al index después de login
        else:
            flash("Invalid credentials!", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/crud", methods=["GET", "POST"])
def crud():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        cursor.execute(
            "INSERT INTO items (name, description) VALUES (%s, %s)",
            (name, description)
        )
        conn.commit()

    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    conn.close()
    return render_template("crud.html", items=items)

@app.route("/edit", methods=["POST"])
def edit():
    id = request.form.get("id")
    name = request.form.get("name")
    description = request.form.get("description")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE items SET name = %s, description = %s, updated_at = NOW() WHERE id = %s",
        (name, description, id)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("crud"))

@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("crud"))

if __name__ == "__main__":
    app.run(debug=True)
