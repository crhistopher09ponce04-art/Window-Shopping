from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3

# -----------------------------
# Configuración de la app
# -----------------------------
app = Flask(__name__)
app.secret_key = "clave_secreta"
DATABASE = "data.db"

# -----------------------------
# Función para conexión a SQLite
# -----------------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()

# -----------------------------
# Crear tablas si no existen
# -----------------------------
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                tipo TEXT NOT NULL
            )
            """
        )
        db.commit()

init_db()

# -----------------------------
# Rutas principales
# -----------------------------
@app.route("/")
def home():
    return render_template("landing.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()

        if user:
            session["usuario"] = user["username"]
            session["tipo"] = user["tipo"]
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Credenciales incorrectas ⚠️")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        tipo = request.form["tipo"]

        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO usuarios (username, password, tipo) VALUES (?, ?, ?)", (username, password, tipo))
            db.commit()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            return render_template("register.html", error="El usuario ya existe ⚠️")

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", usuario=session["usuario"], tipo=session["tipo"])

@app.route("/help")
def help():
    return render_template("help.html")

# -----------------------------
# Manejo de errores
# -----------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="Página no encontrada"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message="Error interno ⚠️"), 500

# -----------------------------
# Ejecutar localmente
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
