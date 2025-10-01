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
    return {
        "LANGS": LANGS,
        "cur_lang": get_lang()
    }

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
# Empresas demo (seed)
# ------------------------
empresas = {
    # Fruta
    "C001": {"id": "C001", "name": "Agrícola Montolín", "role": "Productor", "city": "Maule", "country": "Chile",
             "fruit": "Ciruela", "variety": "Black Diamond", "volume_tons": 50, "price_box": 17500, "price_kg": 400,
             "phone": "+56 9 8765 4321", "email": "ventas@montolin.cl"},
    "C002": {"id": "C002", "name": "Planta Ejemplo", "role": "Planta", "city": "Talca", "country": "Chile",
             "fruit": "Ciruela", "variety": "D'Agen", "volume_tons": 28, "price_box": 16800, "price_kg": 390,
             "phone": "+56 9 5555 5555", "email": "planta@ejemplo.cl"},
    "C003": {"id": "C003", "name": "Pukiyai Packing", "role": "Packing", "city": "Rancagua", "country": "Chile",
             "fruit": "Ciruela", "variety": "Black Amber", "volume_tons": 40, "price_box": 18000, "price_kg": 420,
             "phone": "+56 2 2345 6789", "email": "info@pukiyai.cl"},
    "C004": {"id": "C004", "name": "Frigo Sur", "role": "Frigorífico", "city": "Curicó", "country": "Chile",
             "fruit": "Ciruela", "variety": "Angeleno", "volume_tons": 60, "price_box": 16500, "price_kg": 370,
             "phone": "+56 72 222 3333", "email": "contacto@frigosur.cl"},
    "C005": {"id": "C005", "name": "Tuniche Fruit", "role": "Exportador", "city": "Valparaíso", "country": "Chile",
             "fruit": "Ciruela", "variety": "Black Diamond", "volume_tons": 30, "price_box": 17000, "price_kg": 380,
             "phone": "+56 9 8123 4567", "email": "contacto@tuniche.cl"},

    # Cliente exterior (fruta)
    "X001": {"id": "X001", "name": "Chensen Ogen Ltd.", "role": "Cliente extranjero", "city": "Shenzhen", "country": "China",
             "product_requested": "Ciruela fresca", "variety_requested": "Black Diamond", "volume_requested_tons": 50,
             "phone": "+86 138 0000 1111", "email": "chen@ogen.cn"},

    # Servicios
    "S001": {"id": "S001", "name": "Transporte Andes", "role": "Transporte", "city": "Santiago", "country": "Chile",
             "service": "Camiones refrigerados", "phone": "+56 2 3456 7890", "email": "contacto@transporteandes.cl"},
    "S002": {"id": "S002", "name": "Aduanas Chile Ltda.", "role": "Agencia de aduana", "city": "Valparaíso", "country": "Chile",
             "service": "Gestión documental y trámites", "phone": "+56 2 9999 1111", "email": "aduana@chile.cl"},
    "S003": {"id": "S003", "name": "Puerto Seco SA", "role": "Extraportuario", "city": "San Antonio", "country": "Chile",
             "service": "Almacenaje extraportuario", "phone": "+56 35 1234 567", "email": "info@puertoseco.cl"}
}

# ------------------------
# Usuarios demo (1 por perfil)
# ------------------------
usuarios = {
    "productor1": {"password": "1234", "rol": "Productor", "company_id": "C001"},
    "planta1": {"password": "1234", "rol": "Planta", "company_id": "C002"},
    "packing1": {"password": "1234", "rol": "Packing", "company_id": "C003"},
    "frigorifico1": {"password": "1234", "rol": "Frigorífico", "company_id": "C004"},
    "exportador1": {"password": "1234", "rol": "Exportador", "company_id": "C005"},
    "cliente1": {"password": "1234", "rol": "Cliente extranjero", "company_id": "X001"},
    "transporte1": {"password": "1234", "rol": "Transporte", "company_id": "S001"},
    "aduana1": {"password": "1234", "rol": "Agencia de aduana", "company_id": "S002"},
    "extraportuario1": {"password": "1234", "rol": "Extraportuario", "company_id": "S003"}
}

# ------------------------
# Helpers, reglas de flujo y filtros (se mantienen igual que tu versión larga)
# ------------------------
# ... (todo el bloque con VENTAS_FRUTA, COMPRAS_FRUTA, VENTAS_SERV, COMPRAS_SERV,
#     más las funciones _matches_rubro, destinos_por_rol, companies_for_roles, etc.)

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

@app.route("/register")
def register():
    # Registro de prueba → plantilla simple
    return render_template("register_router.html")

@app.route("/password-reset", methods=["GET", "POST"])
def password_reset():
    if request.method == "GET":
        return render_template("password_reset.html")
    email = request.form.get("email", "")
    flash(t("Si el correo existe, te enviaremos un enlace para restablecer.",
            "If the email exists, we sent you a reset link."))
    return redirect(url_for("login"))

@app.route("/help")
def help_center():
    return render_template("help_center.html")

# ------------------------
# Rutas privadas (dashboard, accesos, detalle, cart, mi_perfil, logout)
# ------------------------
# ... (todo tu bloque original aquí se mantiene sin cambios)

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
