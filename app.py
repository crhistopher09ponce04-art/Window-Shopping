import os
from flask import Flask, render_template, request, redirect, url_for, session, abort, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave_secreta_window_shopping")

# ------------------------
# i18n simple (ES/EN)
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

@app.route("/lang/<code>")
def set_lang(code):
    session["lang"] = code if code in LANGS else "es"
    return redirect(request.args.get("next") or url_for("home"))

# ------------------------
# Roles
# ------------------------
FRUIT_ROLES = {"Productor", "Planta", "Packing", "Frigorífico", "Exportador", "Cliente extranjero"}
SERVICE_ROLES = {"Packing", "Frigorífico", "Transporte", "Agencia de aduana", "Extraportuario", "Planta", "Exportador"}

# ------------------------
# Empresas demo
# ------------------------
empresas = {}
usuarios = {}

# Usuarios demo pre-cargados
def seed_data():
    global empresas, usuarios
    empresas = {
        "C001": {"id": "C001", "name": "Agrícola Montolín", "role": "Productor", "city": "Maule", "country": "Chile",
                 "fruit": "Ciruela", "variety": "Black Diamond", "volume_tons": 50, "price_box": 17500, "price_kg": 400,
                 "phone": "+56 9 8765 4321", "email": "ventas@montolin.cl"},
        "C005": {"id": "C005", "name": "Tuniche Fruit", "role": "Exportador", "city": "Valparaíso", "country": "Chile",
                 "fruit": "Ciruela", "variety": "Black Diamond", "volume_tons": 30, "price_box": 17000, "price_kg": 380,
                 "phone": "+56 9 8123 4567", "email": "contacto@tuniche.cl"}
    }
    usuarios = {
        "productor1": {"password": "1234", "rol": "Productor", "company_id": "C001"},
        "exportador1": {"password": "1234", "rol": "Exportador", "company_id": "C005"}
    }

seed_data()

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
        session.setdefault("cart", [])
        flash(t("Bienvenido", "Welcome"))
        return redirect(url_for("dashboard"))
    return render_template("login.html", error=t("Usuario o contraseña incorrectos", "Invalid credentials"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    rut = request.form.get("rut", "").strip()
    email = request.form.get("email", "").strip()
    address = request.form.get("address", "").strip()
    phone = request.form.get("phone", "").strip()
    rol = request.form.get("rol", "").strip()

    if not username or not password or not rut or not email:
        return render_template("register.html", error=t("Faltan campos obligatorios.", "Missing required fields."))

    if username in usuarios:
        return render_template("register.html", error=t("Ese usuario ya existe.", "That username already exists."))

    company_id = f"U{len(empresas)+1:03d}"
    empresas[company_id] = {
        "id": company_id,
        "name": username,
        "role": rol,
        "city": "",
        "country": "Chile",
        "phone": phone,
        "email": email,
        "rut": rut,
        "address": address
    }

    usuarios[username] = {
        "password": password,
        "rol": rol,
        "company_id": company_id
    }

    flash(t("Usuario creado con éxito. Ahora puedes iniciar sesión.", "User created successfully. You can now log in."))
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
    my_company = empresas.get(user["company_id"])
    return render_template("dashboard.html", usuario=session["usuario"], rol=user["rol"], my_company=my_company)

@app.route("/mi-perfil", methods=["GET", "POST"])
def mi_perfil():
    if not require_login(): return redirect(url_for("home"))
    company_id = session["company_id"]
    c = empresas.get(company_id)
    if not c: abort(404)
    if request.method == "POST":
        c["name"] = request.form.get("name", c["name"])
        c["city"] = request.form.get("city", c.get("city", ""))
        c["address"] = request.form.get("address", c.get("address", ""))
        c["phone"] = request.form.get("phone", c.get("phone", ""))
        c["email"] = request.form.get("email", c.get("email", ""))
        flash(t("Perfil actualizado.", "Profile updated."))
        return redirect(url_for("mi_perfil"))
    return render_template("mi_perfil.html", company=c)

@app.route("/cart", methods=["GET", "POST"])
def cart():
    if not require_login(): return redirect(url_for("home"))
    if request.method == "POST":
        action = request.form.get("action")
        if action == "clear":
            session["cart"] = []
            flash(t("Carrito vaciado.", "Cart cleared."))
        elif action == "checkout":
            session["cart"] = []
            flash(t("¡Solicitud enviada!", "Request sent!"))
            return redirect(url_for("dashboard"))
    return render_template("cart.html", cart=session.get("cart", []))

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

# ------------------------
# Entrypoint local
# ------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
