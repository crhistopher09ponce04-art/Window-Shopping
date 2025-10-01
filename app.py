import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave_secreta_window_shopping")

# ------------------------
# Idiomas (ES / EN)
# ------------------------
LANGS = {"es": "Español", "en": "English"}

def get_lang():
    lang = session.get("lang", "es")
    return lang if lang in LANGS else "es"

def t(es, en):
    return es if get_lang() == "es" else en

@app.context_processor
def inject_globals():
    return {"LANGS": LANGS, "cur_lang": get_lang(), "t": t}

@app.route("/set_lang/<code>")
def set_lang(code):
    session["lang"] = code if code in LANGS else "es"
    return redirect(request.referrer or url_for("home"))

# ------------------------
# Roles
# ------------------------
FRUIT_ROLES = {"Productor", "Planta", "Packing", "Frigorífico", "Exportador", "Cliente extranjero"}
SERVICE_ROLES = {"Packing", "Frigorífico", "Transporte", "Agencia de aduana", "Extraportuario", "Planta", "Exportador"}

# ------------------------
# Empresas demo
# ------------------------
empresas = {
    "C001": {"id": "C001", "name": "Agrícola Montolín", "role": "Productor", "city": "Maule", "country": "Chile",
             "fruit": "Ciruela", "variety": "Black Diamond", "volume_tons": 50, "price_box": 17500, "price_kg": 400,
             "phone": "+56 9 8765 4321", "email": "ventas@montolin.cl"},
    "C005": {"id": "C005", "name": "Tuniche Fruit", "role": "Exportador", "city": "Valparaíso", "country": "Chile",
             "fruit": "Ciruela", "variety": "Black Diamond", "volume_tons": 30, "price_box": 17000, "price_kg": 380,
             "phone": "+56 9 8123 4567", "email": "contacto@tuniche.cl"},
}

# ------------------------
# Usuarios demo
# ------------------------
usuarios = {
    "productor1": {"password": "1234", "rol": "Productor", "company_id": "C001"},
    "exportador1": {"password": "1234", "rol": "Exportador", "company_id": "C005"},
    "packing1": {"password": "1234", "rol": "Packing", "company_id": None},
    "frigorifico1": {"password": "1234", "rol": "Frigorífico", "company_id": None},
    "cliente1": {"password": "1234", "rol": "Cliente extranjero", "company_id": None},
    "transporte1": {"password": "1234", "rol": "Transporte", "company_id": None},
    "aduana1": {"password": "1234", "rol": "Agencia de aduana", "company_id": None},
    "extraportuario1": {"password": "1234", "rol": "Extraportuario", "company_id": None},
    "planta1": {"password": "1234", "rol": "Planta", "company_id": None},
}

# ------------------------
# Helpers
# ------------------------
def require_login():
    if "usuario" not in session:
        flash(t("Inicia sesión para continuar.", "Log in to continue."))
        return False
    return True

# ------------------------
# Rutas públicas
# ------------------------
@app.route("/")
def home():
    if "usuario" in session:
        return redirect(url_for("dashboard"))
    return render_template("landing.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    u = usuarios.get(username)
    if u and u["password"] == password:
        session["usuario"] = username
        session["rol"] = u["rol"]
        session["company_id"] = u["company_id"]
        flash(t("Bienvenido", "Welcome"))
        return redirect(url_for("dashboard"))
    return render_template("login.html", error=t("Usuario o contraseña incorrectos", "Invalid credentials"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    rol = request.form.get("rol")
    rut = request.form.get("rut")
    email = request.form.get("email")
    phone = request.form.get("phone")
    address = request.form.get("address")

    if username in usuarios:
        return render_template("register.html", error=t("Usuario ya existe", "User already exists"))

    usuarios[username] = {"password": password, "rol": rol, "company_id": None,
                          "rut": rut, "email": email, "phone": phone, "address": address}
    flash(t("Registro exitoso. Ahora puedes iniciar sesión.", "Registration successful. You can now log in."))
    return redirect(url_for("login"))

@app.route("/help")
def help_center():
    return render_template("help_center.html")

# ------------------------
# Rutas privadas
# ------------------------
@app.route("/dashboard")
def dashboard():
    if not require_login(): return redirect(url_for("home"))
    user = usuarios[session["usuario"]]
    my_company = empresas.get(user.get("company_id"))
    return render_template("dashboard.html", usuario=session["usuario"], rol=user["rol"], my_company=my_company)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ------------------------
# Errores
# ------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message=t("Recurso no encontrado", "Resource not found")), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message=t("Error interno", "Internal server error")), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
