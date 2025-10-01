from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "clave_secreta"

# 📂 Ruta DB
DB_NAME = "data.db"

# =============================
# 🔹 Funciones auxiliares
# =============================
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        # Tabla de usuarios
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        role TEXT,
                        name TEXT,
                        tax_id TEXT,
                        city TEXT,
                        country TEXT,
                        phone TEXT,
                        email TEXT
                    )''')
        # Tabla de ítems
        c.execute('''CREATE TABLE IF NOT EXISTS items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        type TEXT,
                        name TEXT,
                        variety TEXT,
                        quantity TEXT,
                        unit TEXT,
                        price TEXT,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                    )''')
        conn.commit()

def get_user(username):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        return c.fetchone()

def get_user_by_id(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id=?", (user_id,))
        return c.fetchone()

def get_items(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM items WHERE user_id=?", (user_id,))
        return c.fetchall()

# =============================
# 🔹 Rutas principales
# =============================
@app.route("/")
def home():
    return render_template("landing.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                          (username, password, role))
                conn.commit()
                flash("Usuario creado con éxito ✅", "success")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("El usuario ya existe ❌", "danger")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = get_user(username)
        if user and user[2] == password:
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["role"] = user[3]
            flash("Bienvenido, " + username, "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Credenciales incorrectas ❌", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión 👋", "info")
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = get_user_by_id(session["user_id"])
    items = get_items(session["user_id"])
    return render_template("dashboard.html", company=user, items=items)

# =============================
# 🔹 Perfil y manejo de ítems
# =============================
@app.route("/mi_perfil", methods=["GET", "POST"])
def mi_perfil():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    if request.method == "POST":
        # Guardar cambios básicos
        if "name" in request.form:
            with sqlite3.connect(DB_NAME) as conn:
                c = conn.cursor()
                c.execute('''UPDATE users SET name=?, tax_id=?, city=?, country=?, phone=?, email=? 
                             WHERE id=?''',
                          (request.form["name"], request.form["tax_id"], request.form["city"],
                           request.form["country"], request.form["phone"], request.form["email"], user_id))
                conn.commit()
                flash("Datos actualizados ✅", "success")

        # Agregar ítem
        if "add_item" in request.form:
            with sqlite3.connect(DB_NAME) as conn:
                c = conn.cursor()
                c.execute('''INSERT INTO items (user_id, type, name, variety, quantity, unit, price) 
                             VALUES (?, ?, ?, ?, ?, ?, ?)''',
                          (user_id, request.form["item_type"], request.form["item_name"],
                           request.form["item_variety"], request.form["item_quantity"],
                           request.form["item_unit"], request.form["item_price"]))
                conn.commit()
                flash("Ítem agregado ✅", "success")

        # Eliminar ítem
        if "remove_item" in request.form:
            item_id = request.form["remove_item"]
            with sqlite3.connect(DB_NAME) as conn:
                c = conn.cursor()
                c.execute("DELETE FROM items WHERE id=?", (item_id,))
                conn.commit()
                flash("Ítem eliminado 🗑", "warning")

        return redirect(url_for("mi_perfil"))

    user = get_user_by_id(user_id)
    items = get_items(user_id)
    return render_template("mi_perfil.html", company=user, items=items)

# =============================
# 🔹 Errores personalizados
# =============================
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="Página no encontrada ❌"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message="Error interno ⚠️"), 500

# =============================
# 🔹 Inicializar DB al inicio
# =============================
if __name__ == "__main__":
    if not os.path.exists(DB_NAME):
        init_db()
    app.run(debug=True)
