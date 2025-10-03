import os
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, abort, flash
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")

# =========================
# Idiomas / traducción
# =========================
SUPPORTED_LANGS = ["es", "en", "zh"]
DEFAULT_LANG = "es"

def get_lang():
    return session.get("lang", DEFAULT_LANG)

def t(es_text, en_text, zh_text=None):
    """Traducción simple ES/EN/ZH (ZH cae en EN si no hay zh_text)."""
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

# =========================
# Datos de demo
# =========================
# Usuarios demo (user/password = 1234)
USERS = {
    # Compra/Venta
    "productor1":      {"password": "1234", "rol": "Productor",      "perfil_tipo": "compra_venta", "pais": "CL"},
    "planta1":         {"password": "1234", "rol": "Planta",         "perfil_tipo": "compra_venta", "pais": "CL"},
    "exportador1":     {"password": "1234", "rol": "Exportador",     "perfil_tipo": "compra_venta", "pais": "CL"},
    "cliente1":        {"password": "1234", "rol": "Cliente extranjero", "perfil_tipo": "compra_venta", "pais": "US"},

    # Servicios puros
    "transporte1":     {"password": "1234", "rol": "Transporte",         "perfil_tipo": "servicios", "pais": "CL"},
    "aduana1":         {"password": "1234", "rol": "Agencia de Aduanas", "perfil_tipo": "servicios", "pais": "CL"},
    "extraportuario1": {"password": "1234", "rol": "Extraportuario",      "perfil_tipo": "servicios", "pais": "CL"},

    # Duales (aparecen en compra/venta y servicios)
    "packing1":        {"password": "1234", "rol": "Packing",      "perfil_tipo": "dual", "pais": "CL"},
    "frigorifico1":    {"password": "1234", "rol": "Frigorífico",  "perfil_tipo": "dual", "pais": "CL"},
}

# Perfiles públicos/privados de usuarios (editable por cada dueño en /perfil)
# Nota: Packing y Frigorífico tienen ítems de fruta (oferta/demanda) y servicios (dual)
USER_PROFILES = {
    "productor1": {
        "empresa": "Agro Andes SPA",
        "rut": "76.123.456-7",
        "pais": "CL",
        "rol": "Productor",
        "perfil_tipo": "compra_venta",
        "email": "contacto@agroandes.cl",
        "telefono": "+56 9 5000 1001",
        "direccion": "IV Región, Chile",
        "descripcion": "Productores de uva de mesa y ciruelas europeas.",
        "items": [
            {"tipo": "oferta", "producto": "Uva Crimson", "cantidad": "120 pallets", "origen": "IV Región", "precio": "A convenir"},
            {"tipo": "oferta", "producto": "Ciruela D’Agen", "cantidad": "60 pallets", "origen": "IV Región", "precio": "USD 10/caja"},
        ]
    },
    "planta1": {
        "empresa": "Planta El Roble",
        "rut": "77.234.567-8",
        "pais": "CL",
        "rol": "Planta",
        "perfil_tipo": "compra_venta",
        "email": "ventas@elroble.cl",
        "telefono": "+56 9 5000 1002",
        "direccion": "O’Higgins, Chile",
        "descripcion": "Planta con línea de procesos para fruta de exportación.",
        "items": [
            {"tipo": "demanda", "producto": "Cajas plásticas", "cantidad": "20.000 und", "origen": "CL", "precio": "Oferta"},
            {"tipo": "oferta", "producto": "Manzana Gala", "cantidad": "90 pallets", "origen": "VI Región", "precio": "A convenir"},
        ]
    },
    "exportador1": {
        "empresa": "OCExport",
        "rut": "78.345.678-9",
        "pais": "CL",
        "rol": "Exportador",
        "perfil_tipo": "compra_venta",
        "email": "info@ocexport.cl",
        "telefono": "+56 9 5000 1003",
        "direccion": "Santiago, Chile",
        "descripcion": "Exportación multiproducto, foco en Asia.",
        "items": [
            {"tipo": "demanda", "producto": "Cerezas", "cantidad": "150 pallets", "origen": "VI-VII", "precio": "A convenir"},
        ]
    },
    "cliente1": {
        "empresa": "GlobalBuyer Co.",
        "rut": None,
        "pais": "US",
        "rol": "Cliente extranjero",
        "perfil_tipo": "compra_venta",
        "email": "contact@globalbuyer.com",
        "telefono": "+1 305 555 0100",
        "direccion": "Miami, USA",
        "descripcion": "Comprador mayorista en EEUU.",
        "items": [
            {"tipo": "demanda", "producto": "Uva Thompson", "cantidad": "400 pallets", "origen": "CL", "precio": "A convenir"},
        ]
    },
    "transporte1": {
        "empresa": "RutaTrans",
        "rut": "80.567.890-1",
        "pais": "CL",
        "rol": "Transporte",
        "perfil_tipo": "servicios",
        "email": "contacto@rutatrans.cl",
        "telefono": "+56 2 2345 6789",
        "direccion": "Santiago",
        "descripcion": "Transporte refrigerado nacional.",
        "items": [
            {"tipo": "servicio", "servicio": "Transporte refrigerado", "capacidad": "Camiones 28 t", "ubicacion": "Nacional"},
        ]
    },
    "aduana1": {
        "empresa": "AduanasPro",
        "rut": "81.678.901-2",
        "pais": "CL",
        "rol": "Agencia de Aduanas",
        "perfil_tipo": "servicios",
        "email": "info@aduanaspro.cl",
        "telefono": "+56 2 2233 4455",
        "direccion": "Valparaíso",
        "descripcion": "Desaduanaje y documentación.",
        "items": [
            {"tipo": "servicio", "servicio": "Tramitación exportación", "capacidad": "-", "ubicacion": "Valparaíso"},
        ]
    },
    "extraportuario1": {
        "empresa": "ExtraPort",
        "rut": "82.789.012-3",
        "pais": "CL",
        "rol": "Extraportuario",
        "perfil_tipo": "servicios",
        "email": "booking@extraport.cl",
        "telefono": "+56 32 220 1010",
        "direccion": "San Antonio",
        "descripcion": "Depósito extraportuario y consolidado.",
        "items": [
            {"tipo": "servicio", "servicio": "Consolidado contenedor", "capacidad": "40 cont/día", "ubicacion": "San Antonio"},
        ]
    },
    # DUALES
    "packing1": {
        "empresa": "PackSmart",
        "rut": "83.890.123-4",
        "pais": "CL",
        "rol": "Packing",
        "perfil_tipo": "dual",
        "email": "ventas@packsmart.cl",
        "telefono": "+56 72 221 3344",
        "direccion": "Rancagua",
        "descripcion": "Servicios de packing y embalaje + trading.",
        "items": [
            # Compra/Venta
            {"tipo": "oferta", "producto": "Ciruela Larry Anne", "cantidad": "70 pallets", "origen": "VI Región", "precio": "A convenir"},
            {"tipo": "demanda", "producto": "Arándanos", "cantidad": "40 pallets", "origen": "CL", "precio": "Oferta"},
            # Servicios
            {"tipo": "servicio", "servicio": "Embalaje exportación", "capacidad": "30.000 cajas/día", "ubicacion": "Rancagua"},
        ]
    },
    "frigorifico1": {
        "empresa": "FríoPoint Ltda.",
        "rut": "84.901.234-5",
        "pais": "CL",
        "rol": "Frigorífico",
        "perfil_tipo": "dual",
        "email": "contacto@friopoint.cl",
        "telefono": "+56 32 221 7788",
        "direccion": "Valparaíso",
        "descripcion": "Frío + operaciones y trading estacional.",
        "items": [
            # Compra/Venta
            {"tipo": "oferta", "producto": "Manzana Fuji", "cantidad": "100 pallets", "origen": "V Región", "precio": "A convenir"},
            # Servicios
            {"tipo": "servicio", "servicio": "Almacenaje en frío", "capacidad": "1.200 pallets", "ubicacion": "Valparaíso"},
            {"tipo": "servicio", "servicio": "Preenfriado", "capacidad": "8 túneles", "ubicacion": "Valparaíso"},
        ]
    },
}

# Empresas visibles (catálogo general para accesos y detalles)
# Nota: Incluye 2 empresas con CIRUELA
COMPANIES = [
    {
        "slug": "agro-andes",
        "nombre": "Agro Andes SPA",
        "rut": "76.123.456-7",
        "rol": "Productor",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "email": "contacto@agroandes.cl",
        "telefono": "+56 9 5000 1001",
        "direccion": "IV Región",
        "breve": "Uva de mesa y ciruelas europeas.",
        "items": [
            {"tipo": "oferta", "producto": "Uva Crimson", "cantidad": "120 pallets", "origen": "IV Región", "precio": "A convenir"},
            {"tipo": "oferta", "producto": "Ciruela D’Agen", "cantidad": "60 pallets", "origen": "IV Región", "precio": "USD 10/caja"},
        ]
    },
    {
        "slug": "pack-smart",
        "nombre": "PackSmart",
        "rut": "83.890.123-4",
        "rol": "Packing",
        "perfil_tipo": "dual",
        "pais": "CL",
        "email": "ventas@packsmart.cl",
        "telefono": "+56 72 221 3344",
        "direccion": "Rancagua",
        "breve": "Servicios de packing y trading.",
        "items": [
            {"tipo": "oferta", "producto": "Ciruela Larry Anne", "cantidad": "70 pallets", "origen": "VI Región", "precio": "A convenir"},
            {"tipo": "demanda", "producto": "Arándanos", "cantidad": "40 pallets", "origen": "CL", "precio": "Oferta"},
            {"tipo": "servicio", "servicio": "Embalaje exportación", "capacidad": "30.000 cajas/día", "ubicacion": "Rancagua"},
        ]
    },
    {
        "slug": "friopoint",
        "nombre": "FríoPoint Ltda.",
        "rut": "84.901.234-5",
        "rol": "Frigorífico",
        "perfil_tipo": "dual",
        "pais": "CL",
        "email": "contacto@friopoint.cl",
        "telefono": "+56 32 221 7788",
        "direccion": "Valparaíso",
        "breve": "Frío y logística + trading estacional.",
        "items": [
            {"tipo": "oferta", "producto": "Manzana Fuji", "cantidad": "100 pallets", "origen": "V Región", "precio": "A convenir"},
            {"tipo": "servicio", "servicio": "Almacenaje en frío", "capacidad": "1.200 pallets", "ubicacion": "Valparaíso"},
            {"tipo": "servicio", "servicio": "Preenfriado", "capacidad": "8 túneles", "ubicacion": "Valparaíso"},
        ]
    },
    {
        "slug": "ocexport",
        "nombre": "OCExport",
        "rut": "78.345.678-9",
        "rol": "Exportador",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "email": "info@ocexport.cl",
        "telefono": "+56 9 5000 1003",
        "direccion": "Santiago",
        "breve": "Exportación multiproducto.",
        "items": [
            {"tipo": "demanda", "producto": "Cerezas", "cantidad": "150 pallets", "origen": "VI-VII", "precio": "A convenir"},
        ]
    },
    {
        "slug": "ruta-trans",
        "nombre": "RutaTrans",
        "rut": "80.567.890-1",
        "rol": "Transporte",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "email": "contacto@rutatrans.cl",
        "telefono": "+56 2 2345 6789",
        "direccion": "Santiago",
        "breve": "Transporte refrigerado nacional.",
        "items": [
            {"tipo": "servicio", "servicio": "Transporte refrigerado", "capacidad": "Camiones 28 t", "ubicacion": "Nacional"},
        ]
    },
    {
        "slug": "aduanas-pro",
        "nombre": "AduanasPro",
        "rut": "81.678.901-2",
        "rol": "Agencia de Aduanas",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "email": "info@aduanaspro.cl",
        "telefono": "+56 2 2233 4455",
        "direccion": "Valparaíso",
        "breve": "Desaduanaje y documentación.",
        "items": [
            {"tipo": "servicio", "servicio": "Tramitación exportación", "capacidad": "-", "ubicacion": "Valparaíso"},
        ]
    },
]

# =========================
# Carrito en sesión
# =========================
def get_cart():
    return session.setdefault("cart", [])

def save_cart(cart):
    session["cart"] = cart

# =========================
# Helpers
# =========================
def login_required():
    return "usuario" in session

def companies_for_tipo(tipo):
    """Devuelve lista de empresas según 'tipo' de vista."""
    if tipo == "servicios":
        return [c for c in COMPANIES if c["perfil_tipo"] in ("servicios", "dual")]
    elif tipo in ("ventas", "compras"):
        # ventas/compras -> incluyen compra_venta y dual
        base = [c for c in COMPANIES if c["perfil_tipo"] in ("compra_venta", "dual")]
        if tipo == "ventas":
            return [c for c in base if any(i.get("tipo") == "oferta" for i in c.get("items", []))]
        else:
            return [c for c in base if any(i.get("tipo") == "demanda" for i in c.get("items", []))]
    return []

# =========================
# Rutas
# =========================
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
            flash(t("Bienvenido/a", "Welcome"))
            return redirect(url_for("dashboard"))
        else:
            error = t("Usuario o clave inválidos.", "Invalid user or password.")
    return render_template("login.html", error=error, t=t)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# --- Registro en 2 pasos (router + formulario) ---
@app.route("/register_router")
def register_router():
    return render_template("register_router.html", t=t)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    nacionalidad = request.args.get("nac")       # "nacional" o "extranjero"
    perfil_tipo = request.args.get("tipo")       # "compra_venta" o "servicios" (opcional)

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
                "pais": pais or ("CL" if nac == "nacional" else "EX")
            }
            USER_PROFILES[username] = {
                "empresa": username.capitalize(),
                "rut": rut or None,
                "pais": USERS[username]["pais"],
                "rol": rol,
                "perfil_tipo": perfil_tipo,
                "email": email or f"{username}@mail.com",
                "telefono": telefono or "",
                "direccion": direccion or "",
                "descripcion": "Nuevo perfil.",
                "items": []
            }
            session["usuario"] = username
            flash(t("Registro exitoso", "Registration successful"))
            return redirect(url_for("dashboard"))

    roles_cv = ["Productor", "Planta", "Packing", "Frigorífico", "Exportador", "Cliente extranjero"]
    roles_srv = ["Packing", "Frigorífico", "Transporte", "Agencia de Aduanas", "Extraportuario"]

    return render_template(
        "register.html",
        error=error,
        nacionalidad=nacionalidad,
        perfil_tipo=perfil_tipo,
        roles_cv=roles_cv,
        roles_srv=roles_srv,
        t=t
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
    return render_template("dashboard.html",
                           usuario=username,
                           rol=user["rol"],
                           perfil_tipo=user["perfil_tipo"],
                           my_company=my_company,
                           cart=get_cart(),
                           t=t)

@app.route("/accesos/<tipo>")
def accesos(tipo):
    tipo = tipo.lower()
    if tipo not in ["ventas", "compras", "servicios"]:
        abort(404)
    data = companies_for_tipo(tipo) if tipo in ("ventas", "compras") else companies_for_tipo("servicios")
    return render_template("accesos.html", tipo=tipo, data=data, t=t)

@app.route("/detalles/<tipo>")
def detalles(tipo):
    tipo = tipo.lower()
    if tipo not in ["ventas", "compras", "servicios"]:
        abort(404)
    data = companies_for_tipo(tipo)
    # Renderiza a las plantillas detalle_ventas, detalle_compras, detalle_servicios
    return render_template(f"detalle_{tipo}.html", data=data, t=t)

@app.route("/empresa/<slug>")
def empresa(slug):
    comp = next((c for c in COMPANIES if c["slug"] == slug), None)
    if not comp:
        # Si no existe en catálogo, intentar mostrar perfil de usuario con ese "slug" (username)
        prof = USER_PROFILES.get(slug)
        if not prof:
            abort(404)
        return render_template("empresa.html", comp=prof, es_user=True, t=t)
    return render_template("empresa.html", comp=comp, es_user=False, t=t)

# --------- Carrito ----------
@app.route("/cart/add", methods=["POST"])
def cart_add():
    # item genérico desde formulario (empresa + producto/servicio + tipo)
    form = request.form.to_dict()
    item = {
        "empresa": form.get("empresa") or "-",
        "tipo": form.get("tipo"),
        "producto": form.get("producto"),
        "servicio": form.get("servicio"),
        "cantidad": form.get("cantidad"),
        "origen": form.get("origen"),
        "precio": form.get("precio"),
    }
    cart = get_cart()
    cart.append(item)
    save_cart(cart)
    flash(t("Agregado al carrito.", "Added to cart."))
    return redirect(request.referrer or url_for("carrito"))

@app.route("/carrito", methods=["GET", "POST"])
def carrito():
    cart = get_cart()
    if request.method == "POST":
        action = request.form.get("action")
        if action == "clear":
            save_cart([])
            flash(t("Carrito vaciado.", "Cart cleared."))
            return redirect(url_for("carrito"))
        elif action and action.startswith("remove:"):
            try:
                idx = int(action.split(":")[1])
                if 0 <= idx < len(cart):
                    cart.pop(idx)
                    save_cart(cart)
                    flash(t("Ítem eliminado.", "Item removed."))
            except:
                pass
            return redirect(url_for("carrito"))
    return render_template("carrito.html", cart=cart, t=t)

# --------- Ayuda / contacto ----------
@app.route("/ayuda", methods=["GET", "POST"])
def ayuda():
    mensaje = None
    if request.method == "POST":
        correo = request.form.get("correo", "").strip()
        msg = request.form.get("mensaje", "").strip()
        if correo and msg:
            # Demo: guardamos en sesión un histórico simple
            tickets = session.setdefault("tickets", [])
            tickets.append({"email": correo, "mensaje": msg})
            session["tickets"] = tickets
            mensaje = t("Tu mensaje fue enviado. Te contactaremos.", "Your message was sent. We'll contact you.")
        else:
            mensaje = t("Completa correo y mensaje.", "Please complete email and message.")
    return render_template("ayuda.html", mensaje=mensaje, t=t)

# =========================
# Errores
# =========================
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html",
                           code=404,
                           message=t("No encontrado", "Not found", "未找到"),
                           t=t), 404

@app.errorhandler(500)
def server_error(e):
    # Asegura no romper por traducción en error
    return render_template("error.html",
                           code=500,
                           message=t("Error interno", "Internal server error", "內部伺服器錯誤"),
                           t=t), 500

# =========================
# Run local
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
