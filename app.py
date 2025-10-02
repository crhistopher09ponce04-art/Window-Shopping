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
# Usuarios demo (login con username / password)
# ---------------------------
USERS = {
    "productor1": {"password": "1234", "rol": "Productor", "perfil_tipo": "compra_venta", "pais": "CL"},
    "planta1": {"password": "1234", "rol": "Planta", "perfil_tipo": "compra_venta", "pais": "CL"},
    "packing1": {"password": "1234", "rol": "Packing", "perfil_tipo": "servicios", "pais": "CL"},
    "frigorifico1": {"password": "1234", "rol": "Frigorífico", "perfil_tipo": "servicios", "pais": "CL"},
    "exportador1": {"password": "1234", "rol": "Exportador", "perfil_tipo": "compra_venta", "pais": "CL"},
    "cliente1": {"password": "1234", "rol": "Cliente extranjero", "perfil_tipo": "compra_venta", "pais": "US"},
    "transporte1": {"password": "1234", "rol": "Transporte", "perfil_tipo": "servicios", "pais": "CL"},
    "aduana1": {"password": "1234", "rol": "Agencia de Aduanas", "perfil_tipo": "servicios", "pais": "CL"},
    "extraportuario1": {"password": "1234", "rol": "Extraportuario", "perfil_tipo": "servicios", "pais": "CL"},
}

# ---------------------------
# Perfiles ficticios
# ---------------------------
USER_PROFILES = {
    "productor1": {
        "empresa": "Frutícola Los Andes",
        "rut": "76.111.111-1",
        "rol": "Productor",
        "email": "ventas@fruticoland.cl",
        "telefono": "+56 9 7000 1111",
        "direccion": "Camino Agrícola 45, San Felipe",
        "descripcion": "Productores de uva de mesa y ciruelas.",
        "items": [
            {"tipo": "oferta", "producto": "Uva Red Globe", "cantidad": "150 pallets", "precio": "USD 2.1/kg", "origen": "Aconcagua"},
            {"tipo": "oferta", "producto": "Ciruelas D'Agen", "cantidad": "200 pallets", "precio": "USD 1.8/kg", "origen": "San Felipe"},
        ],
    },
    "planta1": {
        "empresa": "AgroPlanta Chile Ltda.",
        "rut": "77.222.222-2",
        "rol": "Planta",
        "email": "contacto@agroplanta.cl",
        "telefono": "+56 9 7000 2222",
        "direccion": "Ruta 5 Sur, Talca",
        "descripcion": "Planta de procesamiento y clasificación de fruta fresca.",
        "items": [
            {"tipo": "oferta", "producto": "Manzanas Fuji", "cantidad": "500 pallets", "precio": "USD 1.5/kg", "origen": "Talca"},
        ],
    },
    "packing1": {
        "empresa": "PackingPro SPA",
        "rut": "78.333.333-3",
        "rol": "Packing",
        "email": "info@packingpro.cl",
        "telefono": "+56 9 7000 3333",
        "direccion": "Parque Industrial, Rancagua",
        "descripcion": "Servicios de packing y embalaje para fruta fresca.",
        "items": [
            {"tipo": "servicio", "servicio": "Packing exportación", "capacidad": "30.000 cajas/día", "ubicacion": "Rancagua"},
        ],
    },
    "frigorifico1": {
        "empresa": "Frigorífico del Pacífico",
        "rut": "79.444.444-4",
        "rol": "Frigorífico",
        "email": "contacto@friopacifico.cl",
        "telefono": "+56 9 7000 4444",
        "direccion": "Puerto Central, Valparaíso",
        "descripcion": "Almacenamiento en frío para exportaciones.",
        "items": [
            {"tipo": "servicio", "servicio": "Almacenaje congelado", "capacidad": "2.000 pallets", "ubicacion": "Valparaíso"},
            {"tipo": "servicio", "servicio": "Prefrío rápido", "capacidad": "10 túneles", "ubicacion": "Valparaíso"},
        ],
    },
    "exportador1": {
        "empresa": "ChileFresh Export",
        "rut": "80.555.555-5",
        "rol": "Exportador",
        "email": "export@chilefresh.cl",
        "telefono": "+56 9 7000 5555",
        "direccion": "Av. Apoquindo 1234, Santiago",
        "descripcion": "Exportador de fruta fresca con llegada a China y USA.",
        "items": [
            {"tipo": "demanda", "producto": "Arándanos", "cantidad": "100 pallets", "precio": "A convenir", "origen": "Chile"},
        ],
    },
    "cliente1": {
        "empresa": "Global Fruits Import LLC",
        "rut": None,
        "rol": "Cliente extranjero",
        "email": "purchasing@globalfruits.com",
        "telefono": "+1 305 123 4567",
        "direccion": "Miami, USA",
        "descripcion": "Importador de fruta latinoamericana en EEUU.",
        "items": [
            {"tipo": "demanda", "producto": "Cerezas", "cantidad": "300 pallets", "precio": "A convenir", "origen": "Chile"},
        ],
    },
    "transporte1": {
        "empresa": "TransAndes Logistics",
        "rut": "81.666.666-6",
        "rol": "Transporte",
        "email": "logistica@transandes.cl",
        "telefono": "+56 9 7000 6666",
        "direccion": "Camino a Melipilla, Santiago",
        "descripcion": "Servicios de transporte terrestre y portuario.",
        "items": [
            {"tipo": "servicio", "servicio": "Transporte terrestre", "capacidad": "50 camiones", "ubicacion": "Chile"},
        ],
    },
    "aduana1": {
        "empresa": "Agencia Aduanera Sur",
        "rut": "82.777.777-7",
        "rol": "Agencia de Aduanas",
        "email": "aduana@aduanasur.cl",
        "telefono": "+56 9 7000 7777",
        "direccion": "Puerto San Antonio",
        "descripcion": "Agencia de aduanas autorizada por el SAG.",
        "items": [
            {"tipo": "servicio", "servicio": "Gestión documental exportación", "capacidad": "300 operaciones/mes", "ubicacion": "San Antonio"},
        ],
    },
    "extraportuario1": {
        "empresa": "Depósitos Extraport",
        "rut": "83.888.888-8",
        "rol": "Extraportuario",
        "email": "contacto@extraport.cl",
        "telefono": "+56 9 7000 8888",
        "direccion": "Camino Puerto 456, San Antonio",
        "descripcion": "Depósitos extraportuarios para fruta de exportación.",
        "items": [
            {"tipo": "servicio", "servicio": "Almacenaje extraportuario", "capacidad": "800 pallets", "ubicacion": "San Antonio"},
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
    user = session["user"]
    profile = USER_PROFILES.get(user, {})
    return render_template("dashboard.html", usuario=user, rol=USERS[user]["rol"], perfil_tipo=USERS[user]["perfil_tipo"], my_company=profile, cart=get_cart(), t=t)

@app.route("/perfil")
def perfil():
    if "user" not in session:
        return redirect(url_for("login"))
    user = session["user"]
    profile = USER_PROFILES.get(user)
    return render_template("perfil.html", perfil=profile, t=t)

@app.route("/empresa/<slug>")
def empresa(slug):
    profile = USER_PROFILES.get(slug)
    if not profile:
        return redirect(url_for("dashboard"))
    return render_template("empresa.html", comp=profile, es_user=False, t=t)

@app.route("/detalles/<tipo>")
def detalles(tipo):
    data = []
    for slug, p in USER_PROFILES.items():
        comp = {
            "slug": slug,
            "nombre": p.get("empresa"),
            "rol": p.get("rol"),
            "pais": USERS.get(slug, {}).get("pais", ""),
            "rut": p.get("rut"),
            "email": p.get("email"),
            "telefono": p.get("telefono"),
            "descripcion": p.get("descripcion"),
            "items": p.get("items", []),
        }
        for it in comp["items"]:
            if tipo == "ventas" and it.get("tipo") == "oferta":
                data.append(comp)
            elif tipo == "compras" and it.get("tipo") == "demanda":
                data.append(comp)
            elif tipo == "servicios" and it.get("tipo") == "servicio":
                data.append(comp)
    return render_template(f"detalle_{tipo}.html", data=data, t=t)

@app.route("/carrito")
def carrito():
    return render_template("carrito.html", cart=get_cart(), t=t)

@app.route("/add_to_cart/<user>/<int:item>")
def add_item(user, item):
    profile = USER_PROFILES.get(user)
    if not profile:
        return redirect(url_for("dashboard"))
    if 0 <= item < len(profile["items"]):
        item_data = dict(profile["items"][item])
        item_data["empresa"] = profile["empresa"]
        add_to_cart(item_data)
    return redirect(url_for("carrito"))

# ---------------------------
# Manejo de errores
# ---------------------------
@app.errorhandler(HTTPException)
def handle_http(e):
    return render_template("error.html", code=e.code, message=e.description, t=t), e.code

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message=t("Error interno", "Internal server error"), t=t), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
