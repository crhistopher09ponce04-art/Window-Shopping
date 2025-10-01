from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave_secreta_window_shopping")


# ---------------------------
# DB helpers + Auto-seed
# ---------------------------
DB_PATH = "data.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_db():
    """Crea la DB y si no existen, inserta usuarios de prueba."""
    conn = get_db_connection()
    cur = conn.cursor()

    # Tabla de usuarios
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    # Usuarios demo
    demo_users = [
        ("exportador1", "1234", "exportador"),
        ("importador1", "1234", "importador"),
        ("servicio1", "1234", "servicio"),
    ]
    # INSERT OR IGNORE evita reinsertar si ya existen
    cur.executemany(
        "INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
        demo_users
    )

    conn.commit()
    conn.close()

# Crear/sembrar DB al arrancar
ensure_db()


# ---------------------------
# Rutas públicas
# ---------------------------
@app.route("/")
def home():
    return render_template("landing.html")


@app.route("/help")
def help():
    # Usa templates/help.html
    return render_template("help.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            flash("Inicio de sesión exitoso ✅", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Usuario o contraseña incorrectos ⚠️", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "").strip()  # exportador/importador/servicio

        if not username or not password or not role:
            flash("Completa todos los campos.", "warning")
            return render_template("register.html")

        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, password, role)
            )
            conn.commit()
            conn.close()
            flash("Usuario creado con éxito ✅", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Ese nombre de usuario ya existe ❌", "danger")
        except Exception:
            flash("Ocurrió un error al registrar. Intenta de nuevo.", "danger")

    return render_template("register.html")


# ---------------------------
# Rutas privadas
# ---------------------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template(
        "dashboard.html",
        username=session.get("username"),
        role=session.get("role")
    )


@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente 👋", "info")
    return redirect(url_for("home"))


# ---------------------------
# Errores
# ---------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="Página no encontrada"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message="Error interno ⚠️"), 500


# ---------------------------
# Entrypoint local
# ---------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
