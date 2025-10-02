from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.exceptions import HTTPException
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------------------
# Traducción simple (ES, EN, ZH)
# ---------------------------
def t(es, en, zh=None):
    lang = session.get("lang", "es")
    if lang == "en":
        return en
    elif lang == "zh" and zh:
        return zh
    return es

# ---------------------------
# Usuarios de prueba
# ---------------------------
USERS = {
    "productor_demo": {"password": "Demo1234", "rol": "Productor", "perfil_tipo": "compra_venta", "pais": "CL"},
    "planta_demo": {"password": "Demo1234", "rol": "Planta", "perfil_tipo": "compra_venta", "pais": "CL"},
    "packing_demo": {"password": "Demo1234", "rol": "Packing", "perfil_tipo": "servicios", "pais": "CL"},
    "frigorifico_demo": {"password": "Demo1234", "rol": "Frigorífico", "perfil_tipo": "servicios", "pais": "CL"},
    "exportador_demo": {"password": "Demo1234", "rol": "Exportador", "perfil_tipo": "compra_venta", "pais": "CL"},
    "cliente_ex_demo": {"password": "Demo1234", "rol": "Cliente extranjero", "perfil_tipo": "compra_venta", "pais": "US"},
    "transporte_demo": {"password": "Demo1234", "rol": "Transporte", "perfil_tipo": "servicios", "pais": "CL"},
    "aduana_demo": {"password": "Demo1234", "rol": "Agencia de Aduanas", "perfil_tipo": "servicios", "pais": "CL"},
    "extraport_demo": {"password": "Demo1234", "rol": "Extraportuario", "perfil_tipo": "servicios", "pais": "CL"},
    "empresa_demo": {"password": "Demo1234", "rol": "Productor", "perfil_tipo": "compra_venta", "pais": "CL"},
}

# ---------------------------
# Perfiles ficticios
# ---------------------------
USER_PROFILES = {
    "productor_demo": {
        "empresa": "AgroDemo Productores SPA",
        "rut": "76.123.456-7",
        "rol": "Productor",
        "email": "ventas@agrodemo.cl",
        "telefono": "+56 9 6000 0001",
        "direccion": "Camino Real 123, Vicuña",
        "descripcion": "Productores de uva y berries.",
        "items": [
            {"tipo": "oferta", "producto": "Uva Crimson", "cantidad": "120 pallets", "precio": "A convenir"},
            {"tipo": "oferta", "producto": "Arándanos", "cantidad": "30 pallets", "precio": "USD 0.95/kg"},
        ],
    },
    "packing_demo": {
        "empresa": "PackDemo S.A.",
        "rut": "78.345.678-9",
        "rol": "Packing",
        "email": "info@packdemo.cl",
        "telefono": "+56 9 6000 0002",
        "direccion": "Sector Industrial 12, Rancagua",
        "descripcion": "Servicios de packing y embalaje.",
        "items": [
            {"tipo": "servicio", "servicio": "Embalaje y etiquetado", "capacidad": "25.000 cajas/día"},
        ],
    },
    "frigorifico_demo": {
        "empresa": "FríoDemo Ltda.",
        "rut": "79.456.789-0",
        "rol": "Frigorífico",
        "email": "contacto@friodemo.cl",
        "telefono": "+56 32 444 5555",
        "direccion": "Puerto Central, Valparaíso",
        "descripcion": "Almacenaje refrigerado y logística.",
        "items": [
            {"tipo": "servicio", "servicio": "Almacenaje en frío", "capacidad": "1.500 pallets"},
            {"tipo": "servicio", "servicio": "Preenfriado", "capacidad": "6 túneles"},
        ],
    },
    "exportador_demo": {
        "empresa": "OCExport Demo",
        "rut": "80.567.890-1",
        "rol": "Exportador",
        "email": "export@ocexport.cl",
        "telefono": "+56 9 6000 0003",
        "direccion": "Av. Exportadores 45, Santiago",
        "descripcion": "Exportador con red en Europa y Asia.",
        "items": [
            {"tipo": "demanda", "producto": "Cerezas", "cantidad": "200 pallets", "precio": "A convenir"},
        ],
    },
    "cliente_ex_demo": {
        "empresa": "GlobalBuyer Co.",
        "rut": None,
        "rol": "Cliente extranjero",
        "email": "contact@globalbuyer.com",
        "telefono": "+1 555 0100",
        "direccion": "Miami, USA",
        "descripcion": "Comprador mayorista en EEUU.",
        "items": [
            {"tipo": "demanda", "producto": "Uva Thompson", "cantidad": "400 pallets", "precio": "A convenir"},
        ],
    },
}

# ---------------------------
# Carrito (simulación en sesión)
# ---------------------------
def get_cart():
    return session.get("cart", [])

def add_to_cart(item):
    cart = get_cart()
    cart.append(item)
    session["cart"] = cart

# ---------------------------
# Rutas principales
# ---------------------------
@app.route("/")
def home():
    return render_template("landing.html", t=t)

@app.route("/set_lang/<lang>")
def set_lang(lang):
    session["lang"] = lang
    return redirect(request.referrer or url_for("home"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]
        if user in USERS and USERS[user]["password"] == pwd:
            session["user"] = user
            return redirect(url_for("dashboard"))
        return render_template("login.html", error=t("Credenciales inválidas", "Invalid credentials"), t=t)
    return render_template("login.html", t=t)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    profile = USER_PROFILES.get(session["user"], {})
    return render_template("dashboard.html", profile=profile, t=t)

@app.route("/perfil")
def perfil():
    if "user" not in session:
        return redirect(url_for("login"))
    user = session["user"]
    profile = USER_PROFILES.get(user)
    return render_template("perfil.html", profile=profile, t=t)

@app.route("/detalles/<tipo>")
def detalles(tipo):
    if tipo == "ventas":
        items = [(u, p) for u, p in USER_PROFILES.items() for i in p["items"] if i.get("tipo") == "oferta"]
    elif tipo == "compras":
        items = [(u, p) for u, p in USER_PROFILES.items() for i in p["items"] if i.get("tipo") == "demanda"]
    elif tipo == "servicios":
        items = [(u, p) for u, p in USER_PROFILES.items() for i in p["items"] if i.get("tipo") == "servicio"]
    else:
        items = []
    return render_template(f"detalle_{tipo}.html", items=items, t=t)

@app.route("/carrito")
def carrito():
    return render_template("carrito.html", cart=get_cart(), t=t)

@app.route("/add_to_cart/<user>/<item>")
def add_item(user, item):
    profile = USER_PROFILES.get(user)
    if not profile:
        return redirect(url_for("dashboard"))
    if 0 <= int(item) < len(profile["items"]):
        add_to_cart(profile["items"][int(item)])
    return redirect(url_for("carrito"))

@app.errorhandler(HTTPException)
def handle_http(e):
    return render_template("error.html", code=e.code, message=e.description, t=t), e.code

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message=t("Error interno", "Internal server error"), t=t), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
