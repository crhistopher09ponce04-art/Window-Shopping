import os
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, abort
)
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")

# =========================================================
# i18n simple
# =========================================================
SUPPORTED_LANGS = ["es", "en", "zh"]
DEFAULT_LANG = "es"

def get_lang():
    return session.get("lang", DEFAULT_LANG)

def t(es_text, en_text, zh_text=None):
    lang = get_lang()
    if lang == "en":
        return en_text
    if lang == "zh":
        return zh_text or en_text
    return es_text

@app.route("/set_lang/<lang>")
def set_lang(lang):
    if lang not in SUPPORTED_LANGS:
        lang = DEFAULT_LANG
    session["lang"] = lang
    return redirect(request.referrer or url_for("home"))

# =========================================================
# Datos de prueba (usuarios + perfiles + empresas del “mercado”)
# =========================================================
ROLES_COMPRA_VENTA = ["Productor", "Planta", "Packing", "Frigorífico", "Exportador", "Cliente extranjero"]
ROLES_SERVICIOS = ["Packing", "Frigorífico", "Transporte", "Agencia de aduana", "Extraportuario"]

USERS = {
    # Compra/Venta
    "productor_demo":   {"password": "Demo1234", "rol": "Productor",          "perfil_tipo": "compra_venta", "pais": "CL"},
    "planta_demo":      {"password": "Demo1234", "rol": "Planta",             "perfil_tipo": "compra_venta", "pais": "CL"},
    "exportador_demo":  {"password": "Demo1234", "rol": "Exportador",         "perfil_tipo": "compra_venta", "pais": "CL"},
    "cliente_ex_demo":  {"password": "Demo1234", "rol": "Cliente extranjero", "perfil_tipo": "compra_venta", "pais": "US"},
    # Servicios
    "packing_demo":     {"password": "Demo1234", "rol": "Packing",            "perfil_tipo": "servicios",    "pais": "CL"},
    "frigorifico_demo": {"password": "Demo1234", "rol": "Frigorífico",        "perfil_tipo": "servicios",    "pais": "CL"},
    "transporte_demo":  {"password": "Demo1234", "rol": "Transporte",         "perfil_tipo": "servicios",    "pais": "CL"},
    "aduana_demo":      {"password": "Demo1234", "rol": "Agencia de aduana",  "perfil_tipo": "servicios",    "pais": "CL"},
    "extraport_demo":   {"password": "Demo1234", "rol": "Extraportuario",     "perfil_tipo": "servicios",    "pais": "CL"},
}

USER_PROFILES = {
    "productor_demo": {
        "empresa": "AgroDemo Productores SPA",
        "rut": "76.123.456-7",
        "rol": "Productor",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "email": "ventas@agrodemo.cl",
        "telefono": "+56 9 6000 0001",
        "direccion": "Camino Real 123, Vicuña",
        "descripcion": "Productores de uva y berries.",
        "items": [
            {"tipo": "oferta", "producto": "Uva Crimson", "cantidad": "120 pallets", "origen": "IV Región", "precio": "A convenir"},
            {"tipo": "oferta", "producto": "Arándanos", "cantidad": "30 pallets", "origen": "Maule", "precio": "USD 0.95/kg"},
        ],
    },
    "planta_demo": {
        "empresa": "Procesadora Valle Central Ltda.",
        "rut": "76.987.654-3",
        "rol": "Planta",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "email": "contacto@procvalle.cl",
        "telefono": "+56 72 222 3344",
        "direccion": "Km 5 Ruta 5 Sur, Curicó",
        "descripcion": "Planta procesadora multiproducto.",
        "items": [
            {"tipo": "demanda", "producto": "Cajas plásticas", "cantidad": "20.000 und", "origen": "CL", "precio": "Oferta"},
        ],
    },
    "exportador_demo": {
        "empresa": "OCExport Demo",
        "rut": "80.567.890-1",
        "rol": "Exportador",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "email": "export@ocexport.cl",
        "telefono": "+56 9 6000 0003",
        "direccion": "Av. Exportadores 45, Santiago",
        "descripcion": "Exportador con red en Europa y Asia.",
        "items": [
            {"tipo": "demanda", "producto": "Cerezas", "cantidad": "200 pallets", "origen": "VI-VII", "precio": "A convenir"},
        ],
    },
    "cliente_ex_demo": {
        "empresa": "GlobalBuyer Co.",
        "rut": None,
        "rol": "Cliente extranjero",
        "perfil_tipo": "compra_venta",
        "pais": "US",
        "email": "contact@globalbuyer.com",
        "telefono": "+1 555 0100",
        "direccion": "Miami, USA",
        "descripcion": "Comprador mayorista en EEUU.",
        "items": [
            {"tipo": "demanda", "producto": "Uva Thompson", "cantidad": "400 pallets", "origen": "CL", "precio": "A convenir"},
        ],
    },
    "packing_demo": {
        "empresa": "PackDemo S.A.",
        "rut": "78.345.678-9",
        "rol": "Packing",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "email": "info@packdemo.cl",
        "telefono": "+56 9 6000 0002",
        "direccion": "Sector Industrial 12, Rancagua",
        "descripcion": "Servicios de packing y embalaje.",
        "items": [
            {"tipo": "servicio", "servicio": "Embalaje y etiquetado", "capacidad": "25.000 cajas/día", "ubicacion": "Rancagua"},
        ],
    },
    "frigorifico_demo": {
        "empresa": "FríoDemo Ltda.",
        "rut": "79.456.789-0",
        "rol": "Frigorífico",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "email": "contacto@friodemo.cl",
        "telefono": "+56 32 444 5555",
        "direccion": "Puerto Central, Valparaíso",
        "descripcion": "Almacenaje refrigerado y logística.",
        "items": [
            {"tipo": "servicio", "servicio": "Almacenaje en frío", "capacidad": "1.500 pallets", "ubicacion": "Valparaíso"},
            {"tipo": "servicio", "servicio": "Preenfriado", "capacidad": "6 túneles", "ubicacion": "Valparaíso"},
        ],
    },
    "transporte_demo": {
        "empresa": "RutaExpress Transportes",
        "rut": "77.222.111-0",
        "rol": "Transporte",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "email": "ops@rutaexpress.cl",
        "telefono": "+56 9 5555 6666",
        "direccion": "Camino a Melipilla 1000, RM",
        "descripcion": "Transporte de carga refrigerada.",
        "items": [
            {"tipo": "servicio", "servicio": "Transporte refrigerado", "capacidad": "Flota 20 camiones", "ubicacion": "RM"},
        ],
    },
    "aduana_demo": {
        "empresa": "AduanasSur Agencia",
        "rut": "76.456.321-4",
        "rol": "Agencia de aduana",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "email": "contacto@aduanassur.cl",
        "telefono": "+56 2 2222 1212",
        "direccion": "Calle Puerto 12, San Antonio",
        "descripcion": "Despacho aduanero de exportación.",
        "items": [
            {"tipo": "servicio", "servicio": "Tramitación exportación", "capacidad": "Alta", "ubicacion": "San Antonio"},
        ],
    },
    "extraport_demo": {
        "empresa": "Extraport Services",
        "rut": "76.444.333-2",
        "rol": "Extraportuario",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "email": "info@extraport.cl",
        "telefono": "+56 32 333 2222",
        "direccion": "Terminal Extraportuario, Valparaíso",
        "descripcion": "Servicios extraportuarios integrales.",
        "items": [
            {"tipo": "servicio", "servicio": "Consolidación", "capacidad": "10.000 m²", "ubicacion": "Valparaíso"},
        ],
    },
}

# “Mercado” visible en listados de detalles
COMPANIES = [
    # compra/venta
    {
        "slug": "agro-andes",
        "nombre": "Agro Andes SPA",
        "rut": "76.111.222-3",
        "rol": "Productor",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "breve": "Uva de mesa y arándanos.",
        "email": "contacto@agroandes.cl",
        "telefono": "+56 9 7777 0001",
        "direccion": "Vicuña, Coquimbo",
        "items": [
            {"tipo": "oferta", "producto": "Uva Crimson", "cantidad": "80 pallets", "origen": "IV Región", "precio": "A convenir"},
            {"tipo": "demanda", "producto": "Cajas plásticas", "cantidad": "15.000 und", "origen": "CL", "precio": "Oferta"},
        ],
    },
    {
        "slug": "ocexport",
        "nombre": "OCExport",
        "rut": "80.567.890-1",
        "rol": "Exportador",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "breve": "Exportación multiproducto.",
        "email": "export@ocexport.cl",
        "telefono": "+56 9 6000 0003",
        "direccion": "Santiago",
        "items": [
            {"tipo": "demanda", "producto": "Cerezas", "cantidad": "150 pallets", "origen": "VI-VII", "precio": "A convenir"},
        ],
    },
    # servicios
    {
        "slug": "friopoint",
        "nombre": "FríoPoint Ltda.",
        "rut": "79.222.111-0",
        "rol": "Frigorífico",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "breve": "Frío y logística en Valparaíso.",
        "email": "contacto@friopoint.cl",
        "telefono": "+56 32 444 8888",
        "direccion": "Puerto, Valparaíso",
        "items": [
            {"tipo": "servicio", "servicio": "Almacenaje en frío", "capacidad": "1.200 pallets", "ubicacion": "Valparaíso"},
            {"tipo": "servicio", "servicio": "Preenfriado", "capacidad": "8 túneles", "ubicacion": "Valparaíso"},
        ],
    },
    {
        "slug": "pack-smart",
        "nombre": "PackSmart",
        "rut": "78.345.678-9",
        "rol": "Packing",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "breve": "Servicios de packing fruta fresca.",
        "email": "info@packsmart.cl",
        "telefono": "+56 72 333 2222",
        "direccion": "Rancagua",
        "items": [
            {"tipo": "servicio", "servicio": "Embalaje exportación", "capacidad": "30.000 cajas/día", "ubicacion": "R.M."},
        ],
    },
]

# =========================================================
# Helpers
# =========================================================
def login_required():
    return "usuario" in session

def get_cart():
    return session.setdefault("cart", [])

# =========================================================
# Rutas
# =========================================================
@app.route("/")
def home():
    return render_template("landing.html", t=t)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = USERS.get(username)
        if user and user["password"] == password:
            session["usuario"] = username
            return redirect(url_for("dashboard"))
        else:
            error = t("Usuario o clave inválidos.", "Invalid user or password.", "帳號或密碼錯誤。")
    return render_template("login.html", error=error, t=t)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ----- Registro en 2 pasos: router y formulario -----
@app.route("/register_router")
def register_router():
    return render_template("register_router.html", t=t)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    nacionalidad = request.args.get("nac")  # "nacional" / "extranjero"
    perfil_tipo = request.args.get("tipo")  # "compra_venta" / "servicios"

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        email = request.form.get("email", "").strip()
        telefono = request.form.get("phone", "").strip()
        direccion = request.form.get("address", "").strip()
        pais = request.form.get("pais", "CL").strip()
        rol = request.form.get("rol", "").strip()
        perfil_tipo = request.form.get("perfil_tipo", "").strip()
        nac = request.form.get("nacionalidad", "").strip()
        rut = request.form.get("rut", "").strip()

        if not username or not password or not rol or not perfil_tipo or not nac:
            error = t("Completa los campos obligatorios.", "Please complete required fields.")
        elif username in USERS:
            error = t("El usuario ya existe.", "User already exists.")
        else:
            USERS[username] = {
                "password": password,
                "rol": rol,
                "perfil_tipo": perfil_tipo,
                "pais": pais or ("CL" if nac == "nacional" else "EX"),
            }
            USER_PROFILES[username] = {
                "empresa": username.capitalize(),
                "rut": rut or None,
                "rol": rol,
                "perfil_tipo": perfil_tipo,
                "pais": USERS[username]["pais"],
                "email": email or f"{username}@mail.com",
                "telefono": telefono or "",
                "direccion": direccion or "",
                "descripcion": "Nuevo perfil.",
                "items": [],
            }
            session["usuario"] = username
            return redirect(url_for("dashboard"))

    return render_template(
        "register.html",
        error=error,
        nacionalidad=nacionalidad,
        perfil_tipo=perfil_tipo,
        roles_cv=ROLES_COMPRA_VENTA,
        roles_srv=ROLES_SERVICIOS,
        t=t,
    )

@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect(url_for("login"))
    username = session["usuario"]
    user = USERS.get(username)
    if not user:
        return redirect(url_for("logout"))
    my_company = USER_PROFILES.get(username, {})
    return render_template(
        "dashboard.html",
        usuario=username,
        rol=user["rol"],
        perfil_tipo=user["perfil_tipo"],
        my_company=my_company,
        cart=get_cart(),
        t=t,
    )

# ----- Listados tipo “accesos” (opcional) -----
@app.route("/accesos/<tipo>")
def accesos(tipo):
    tipo = tipo.lower()
    if tipo not in ["ventas", "compras", "servicios"]:
        abort(404)
    if tipo == "servicios":
        data = [c for c in COMPANIES if c["perfil_tipo"] == "servicios"]
    else:
        data = [c for c in COMPANIES if c["perfil_tipo"] == "compra_venta"]
    return render_template("accesos.html", tipo=tipo, data=data, t=t)

# ----- Vistas de detalle (ventas / compras / servicios) -----
@app.route("/detalles/<tipo>")
def detalles(tipo):
    tipo = tipo.lower()
    if tipo == "servicios":
        data = [c for c in COMPANIES if c["perfil_tipo"] == "servicios"]
    elif tipo in ["ventas", "compras"]:
        data = [c for c in COMPANIES if c["perfil_tipo"] == "compra_venta"]
    else:
        abort(404)

    # Renderiza los templates detalle_ventas.html / detalle_compras.html / detalle_servicios.html
    return render_template(f"detalle_{tipo}.html", data=data, t=t)

# ----- Perfil público de empresa (por slug o por usuario real) -----
@app.route("/empresa/<slug>")
def empresa(slug):
    comp = next((c for c in COMPANIES if c["slug"] == slug), None)
    if not comp:
        # Si es username real, mostrar su perfil público
        prof = USER_PROFILES.get(slug)
        if not prof:
            abort(404)
        return render_template("empresa.html", comp=prof, es_user=True, t=t)
    return render_template("empresa.html", comp=comp, es_user=False, t=t)

# ----- Perfil del usuario autenticado (edición básica) -----
@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    if not login_required():
        return redirect(url_for("login"))
    username = session["usuario"]
    prof = USER_PROFILES.get(username)
    if not prof:
        abort(404)

    mensaje = None
    if request.method == "POST":
        action = request.form.get("action")
        if action == "save_profile":
            prof["empresa"] = request.form.get("empresa", prof["empresa"]).strip()
            prof["email"] = request.form.get("email", prof["email"]).strip()
            prof["telefono"] = request.form.get("telefono", prof["telefono"]).strip()
            prof["direccion"] = request.form.get("direccion", prof["direccion"]).strip()
            prof["descripcion"] = request.form.get("descripcion", prof["descripcion"]).strip()
            prof["rut"] = request.form.get("rut", prof.get("rut")).strip() or None
            mensaje = t("Perfil actualizado.", "Profile updated.")
        elif action == "add_item":
            if prof.get("perfil_tipo") == "servicios":
                servicio = request.form.get("servicio", "").strip()
                capacidad = request.form.get("capacidad", "").strip()
                ubicacion = request.form.get("ubicacion", "").strip()
                if servicio:
                    prof["items"].append({"tipo": "servicio", "servicio": servicio, "capacidad": capacidad, "ubicacion": ubicacion})
                    mensaje = t("Servicio agregado.", "Service added.")
            else:
                subtipo = request.form.get("subtipo", "oferta")
                producto = request.form.get("producto", "").strip()
                cantidad = request.form.get("cantidad", "").strip()
                origen = request.form.get("origen", "").strip()
                precio = request.form.get("precio", "").strip()
                if producto:
                    prof["items"].append({"tipo": subtipo, "producto": producto, "cantidad": cantidad, "origen": origen, "precio": precio})
                    mensaje = t("Ítem agregado.", "Item added.")

    return render_template("perfil.html", perfil=prof, mensaje=mensaje, t=t)

# ----- Carrito -----
@app.route("/cart/add", methods=["POST"])
def cart_add():
    item = request.form.to_dict()
    cart = get_cart()
    cart.append(item)
    session["cart"] = cart
    return redirect(request.referrer or url_for("carrito"))

@app.route("/carrito")
def carrito():
    return render_template("carrito.html", cart=get_cart(), t=t)

@app.route("/cart/clear", methods=["POST"])
def cart_clear():
    session["cart"] = []
    return redirect(url_for("carrito"))

# ----- Ayuda / contacto simple -----
@app.route("/ayuda", methods=["GET", "POST"])
def ayuda():
    mensaje = None
    if request.method == "POST":
        # No enviamos emails reales (demo)
        correo = request.form.get("correo", "").strip()
        detalle = request.form.get("mensaje", "").strip()
        if correo and detalle:
            mensaje = t("¡Gracias! Te contactaremos pronto.", "Thanks! We'll contact you soon.", "謝謝！我們會盡快聯絡你。")
        else:
            mensaje = t("Completa todos los campos.", "Please fill all fields.")
    return render_template("ayuda.html", mensaje=mensaje, t=t)

# =========================================================
# Errores
# =========================================================
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message=t("No encontrado", "Not found", "未找到"), t=t), 404

@app.errorhandler(HTTPException)
def http_exc(e: HTTPException):
    # Para códigos 4xx/5xx “limpios”
    return render_template("error.html", code=e.code, message=e.description, t=t), e.code

@app.errorhandler(500)
def server_error(e):
    # Fallback de 500
    return render_template("error.html", code=500, message=t("Error interno", "Internal server error", "內部伺服器錯誤"), t=t), 500

# =========================================================
# Run local
# =========================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
