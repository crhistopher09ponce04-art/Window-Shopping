from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_babel import Babel, gettext as _
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "clave_secreta"

# Configuración de Babel
app.config['BABEL_DEFAULT_LOCALE'] = 'es'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
babel = Babel(app)

# Idiomas disponibles
LANGUAGES = ['es', 'en']

@babel.localeselector
def get_locale():
    return session.get('lang', 'es')

@app.route("/set_lang/<lang>")
def set_lang(lang):
    if lang in LANGUAGES:
        session['lang'] = lang
    return redirect(request.referrer or url_for("home"))

# Base de datos SQLite
DB_NAME = "data.db"

def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""CREATE TABLE usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        perfil TEXT
                    )""")
        c.execute("""CREATE TABLE items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario_id INTEGER,
                        nombre TEXT,
                        variedad TEXT,
                        medida TEXT,
                        precio REAL,
                        cantidad REAL,
                        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
                    )""")

        # Insertar usuarios de prueba
        usuarios = [
            ("exportador1", "1234", "exportador"),
            ("productor1", "1234", "productor"),
            ("extraportuario1", "1234", "extraportuario"),
            ("comprador1", "1234", "comprador")
        ]
        c.executemany("INSERT INTO usuarios (username, password, perfil) VALUES (?, ?, ?)", usuarios)

        conn.commit()
        conn.close()

init_db()

# ---------------- RUTAS ---------------- #

@app.route("/")
def home():
    return render_template("landing.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT id, perfil FROM usuarios WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["usuario"] = {"id": user[0], "username": username, "perfil": user[1]}
            return redirect(url_for("dashboard"))
        else:
            flash(_("Usuario o contraseña incorrectos"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("home"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        perfil = request.form["perfil"]

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO usuarios (username, password, perfil) VALUES (?, ?, ?)", (username, password, perfil))
            conn.commit()
            flash(_("Usuario creado con éxito"))
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash(_("El nombre de usuario ya existe"))
        finally:
            conn.close()

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))

    usuario = session["usuario"]

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT nombre, variedad, medida, precio, cantidad FROM items WHERE usuario_id=?", (usuario["id"],))
    items = c.fetchall()
    conn.close()

    return render_template("dashboard.html", usuario=usuario, items=items)

@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    if "usuario" not in session:
        return redirect(url_for("login"))

    usuario = session["usuario"]

    if request.method == "POST":
        nombre = request.form["nombre"]
        variedad = request.form["variedad"]
        medida = request.form["medida"]
        precio = request.form["precio"]
        cantidad = request.form["cantidad"]

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO items (usuario_id, nombre, variedad, medida, precio, cantidad) VALUES (?, ?, ?, ?, ?, ?)",
                  (usuario["id"], nombre, variedad, medida, precio, cantidad))
        conn.commit()
        conn.close()
        flash(_("Item agregado con éxito"))
        return redirect(url_for("perfil"))

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, nombre, variedad, medida, precio, cantidad FROM items WHERE usuario_id=?", (usuario["id"],))
    items = c.fetchall()
    conn.close()

    return render_template("perfil.html", usuario=usuario, items=items)

@app.route("/help")
def help_center():
    return render_template("help.html")

# Manejo de errores
@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message=_("Error interno")), 500

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message=_("Página no encontrada")), 404

if __name__ == "__main__":
    app.run(debug=True)
