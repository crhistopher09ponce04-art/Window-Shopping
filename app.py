from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "clave_secreta"

# ==========================
# Usuarios de prueba
# ==========================
usuarios = {
    "productor1": {"password": "1234", "rol": "Productor"},
    "planta1": {"password": "1234", "rol": "Planta"},
    "packing1": {"password": "1234", "rol": "Packing"},
    "frigorifico1": {"password": "1234", "rol": "Frigorífico"},
    "exportador1": {"password": "1234", "rol": "Exportador"},
    "cliente1": {"password": "1234", "rol": "Cliente extranjero"},
    "transporte1": {"password": "1234", "rol": "Transporte"},
    "aduana1": {"password": "1234", "rol": "Agencia de aduana"},
    "extraportuario1": {"password": "1234", "rol": "Extraportuario"}
}

# ==========================
# Función traducción simple
# ==========================
def t(text_es, text_en):
    lang = session.get("lang", "es")
    return text_es if lang == "es" else text_en

app.jinja_env.globals.update(t=t)

# ==========================
# Rutas principales
# ==========================
@app.route("/")
def home():
    if "usuario" in session:
        return redirect(url_for("dashboard"))
    return render_template("landing.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = usuarios.get(username)

        if user and user["password"] == password:
            session["usuario"] = username
            return redirect(url_for("dashboard"))
        else:
            error = t("Usuario o contraseña incorrectos", "Incorrect username or password")
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))
    user = usuarios[session["usuario"]]
    return render_template("dashboard.html", usuario=session["usuario"], rol=user["rol"])

# ==========================
# Ruta accesos
# ==========================
@app.route("/accesos/<tipo>")
def accesos(tipo):
    if "usuario" not in session:
        return redirect(url_for("login"))

    demo_data = {
        "ventas": ["Orden #123 - Cliente X", "Orden #124 - Cliente Y"],
        "servicios": ["Transporte contratado", "Aduana pendiente"],
        "compras": ["Compra #456 - Productor Z", "Compra #457 - Planta W"]
    }

    data = demo_data.get(tipo, [])
    return render_template("accesos.html", tipo=tipo, data=data)

# ==========================
# Cambio de idioma
# ==========================
@app.route("/set_lang/<lang>")
def set_lang(lang):
    session["lang"] = lang
    return redirect(request.referrer or url_for("home"))

# ==========================
# Error handlers
# ==========================
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", msg="404 - Página no encontrada"), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template("error.html", msg="500 - Error interno"), 500

if __name__ == "__main__":
    app.run(debug=True)
