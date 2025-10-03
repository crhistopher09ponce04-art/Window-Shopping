# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, session, abort, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

# =========================================================
# i18n simple
# =========================================================
def t(es, en, zh=None):
    lang = session.get("lang", "es")
    if lang == "en":
        return en
    if lang == "zh" and zh:
        return zh
    return es

@app.route("/set_lang/<lang>")
@app.route("/lang/<lang>")
def set_lang(lang):
    session["lang"] = lang if lang in ("es", "en", "zh") else "es"
    return redirect(request.referrer or url_for("home"))

# =========================================================
# Datos DEMO (Usuarios / Perfiles / Empresas públicas)
#  - Packing y Frigorífico aparecen en Servicios y también en Compra/Venta.
#  - Al menos 2 ofertas con Ciruela (Ciruela D’Agen, Ciruela Angeleno)
# =========================================================

USERS = {
    # Compra/Venta
    "frutera@demo.cl":     {"password": "1234", "rol": "Productor",          "perfil_tipo": "compra_venta", "pais": "CL"},
    "planta@demo.cl":      {"password": "1234", "rol": "Planta",             "perfil_tipo": "compra_venta", "pais": "CL"},
    "exportador@demo.cl":  {"password": "1234", "rol": "Exportador",         "perfil_tipo": "compra_venta", "pais": "CL"},
    "cliente@usa.com":     {"password": "1234", "rol": "Cliente extranjero", "perfil_tipo": "compra_venta", "pais": "US"},
    # Servicios
    "packing@demo.cl":     {"password": "1234", "rol": "Packing",            "perfil_tipo": "servicios",    "pais": "CL"},
    "frigorifico@demo.cl": {"password": "1234", "rol": "Frigorífico",        "perfil_tipo": "servicios",    "pais": "CL"},
    "transporte@demo.cl":  {"password": "1234", "rol": "Transporte",         "perfil_tipo": "servicios",    "pais": "CL"},
    "aduana@demo.cl":      {"password": "1234", "rol": "Agencia de Aduanas", "perfil_tipo": "servicios",    "pais": "CL"},
    "extraport@demo.cl":   {"password": "1234", "rol": "Extraportuario",     "perfil_tipo": "servicios",    "pais": "CL"},
}

USER_PROFILES = {
    "frutera@demo.cl": {
        "empresa": "Agro El Valle SPA",
        "rut": "76.123.456-7",
        "rol": "Productor",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "email": "ventas@agrovalle.cl",
        "telefono": "+56 9 6000 0001",
        "direccion": "Parcela 21, Vicuña",
        "descripcion": "Productores de uva de mesa, ciruela y arándano.",
        "items": [
            {"tipo": "oferta", "producto": "Uva Crimson",      "cantidad": "120 pallets", "origen": "IV Región", "precio": "A convenir"},
            {"tipo": "oferta", "producto": "Ciruela D’Agen",   "cantidad": "80 pallets",  "origen": "VI Región", "precio": "USD 12/caja"},
        ],
    },
    "planta@demo.cl": {
        "empresa": "Planta Los Nogales",
        "rut": "77.200.111-9",
        "rol": "Planta",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "email": "contacto@nogales.cl",
        "telefono": "+56 9 6000 0010",
        "direccion": "Km 5 Camino Interior, Rengo",
        "descripcion": "Recepción y proceso de fruta fresca.",
        "items": [
            {"tipo": "demanda", "producto": "Cajas plásticas 10kg", "cantidad": "20.000 und", "origen": "CL", "precio": "Ofertar"},
        ],
    },
    "exportador@demo.cl": {
        "empresa": "OCExport Chile",
        "rut": "78.345.678-9",
        "rol": "Exportador",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "email": "export@ocexport.cl",
        "telefono": "+56 2 2345 6789",
        "direccion": "Av. Apoquindo 1234, Las Condes",
        "descripcion": "Exportador multiproducto a EEUU/EU/Asia.",
        "items": [
            {"tipo": "demanda", "producto": "Cereza Santina", "cantidad": "150 pallets", "origen": "VI-VII", "precio": "A convenir"},
        ],
    },
    "cliente@usa.com": {
        "empresa": "GlobalBuyer Co.",
        "rut": None,
        "rol": "Cliente extranjero",
        "perfil_tipo": "compra_venta",
        "pais": "US",
        "email": "contact@globalbuyer.com",
        "telefono": "+1 305 555 0100",
        "direccion": "Miami, FL",
        "descripcion": "Mayorista importador en EEUU.",
        "items": [
            {"tipo": "demanda", "producto": "Uva Thompson", "cantidad": "400 pallets", "origen": "CL", "precio": "A convenir"},
        ],
    },
    "packing@demo.cl": {
        "empresa": "PackSmart S.A.",
        "rut": "79.456.789-0",
        "rol": "Packing",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "email": "info@packsmart.cl",
        "telefono": "+56 9 6000 0002",
        "direccion": "Ruta 5 km 185, Rancagua",
        "descripcion": "Servicios de packing, etiquetado y QA.",
        "items": [
            {"tipo": "servicio", "servicio": "Embalaje exportación", "capacidad": "30.000 cajas/día", "ubicacion": "Rancagua"},
            {"tipo": "oferta",   "producto": "Ciruela Angeleno",     "cantidad": "60 pallets",        "origen": "R.M.", "precio": "USD 10/caja"},
        ],
    },
    "frigorifico@demo.cl": {
        "empresa": "FríoPoint Ltda.",
        "rut": "80.567.890-1",
        "rol": "Frigorífico",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "email": "contacto@friopoint.cl",
        "telefono": "+56 32 444 5555",
        "direccion": "Puerto Central, Valparaíso",
        "descripcion": "Almacenaje en frío y logística de puerto.",
        "items": [
            {"tipo": "servicio", "servicio": "Almacenaje en frío", "capacidad": "1.500 pallets", "ubicacion": "Valparaíso"},
            {"tipo": "servicio", "servicio": "Preenfriado",        "capacidad": "6 túneles",     "ubicacion": "Valparaíso"},
            {"tipo": "oferta",   "producto": "Uva Red Globe",      "cantidad": "40 pallets",     "origen": "V Región", "precio": "USD 9/caja"},
        ],
    },
    "transporte@demo.cl": {
        "empresa": "TransVeloz",
        "rut": "81.222.333-4",
        "rol": "Transporte",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "email": "operaciones@transveloz.cl",
        "telefono": "+56 9 5000 1111",
        "direccion": "San Bernardo, RM",
        "descripcion": "Transporte nacional refrigerado.",
        "items": [
            {"tipo": "servicio", "servicio": "Transporte reefer", "capacidad": "35 camiones", "ubicacion": "RM"},
        ],
    },
    "aduana@demo.cl": {
        "empresa": "AduanasFast",
        "rut": "82.555.666-7",
        "rol": "Agencia de Aduanas",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "email": "agencia@aduanasfast.cl",
        "telefono": "+56 2 2987 6543",
        "direccion": "Valparaíso",
        "descripcion": "Tramitación aduanera y asesoría.",
        "items": [
            {"tipo": "servicio", "servicio": "Despacho exportación", "capacidad": "Alta", "ubicacion": "Valparaíso"},
        ],
    },
    "extraport@demo.cl": {
        "empresa": "PortHelper",
        "rut": "83.777.888-9",
        "rol": "Extraportuario",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "email": "info@porthelper.cl",
        "telefono": "+56 9 7000 2222",
        "direccion": "San Antonio",
        "descripcion": "Servicios extraportuarios y contenedores.",
        "items": [
            {"tipo": "servicio", "servicio": "Consolidación de contenedores", "capacidad": "120/día", "ubicacion": "San Antonio"},
        ],
    },
}

# Empresas públicas (perfiles visibles por slug) para /empresa/<slug> y vistas de detalle
COMPANIES = [
    {
        "slug": "agro-el-valle",
        "nombre": "Agro El Valle SPA",
        "rut": "76.123.456-7",
        "rol": "Productor",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "breve": "Uva, ciruela y berries.",
        "email": "ventas@agrovalle.cl",
        "telefono": "+56 9 6000 0001",
        "direccion": "Parcela 21, Vicuña",
        "items": [
            {"tipo": "oferta", "producto": "Uva Crimson",    "cantidad": "120 pallets", "origen": "IV Región", "precio": "A convenir"},
            {"tipo": "oferta", "producto": "Ciruela D’Agen", "cantidad": "80 pallets",  "origen": "VI Región", "precio": "USD 12/caja"},
        ],
    },
    {
        "slug": "packsmart",
        "nombre": "PackSmart S.A.",
        "rut": "79.456.789-0",
        "rol": "Packing",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "breve": "Packing, QA y etiquetado.",
        "email": "info@packsmart.cl",
        "telefono": "+56 9 6000 0002",
        "direccion": "Ruta 5 km 185, Rancagua",
        "items": [
            {"tipo": "servicio", "servicio": "Embalaje exportación", "capacidad": "30.000 cajas/día", "ubicacion": "Rancagua"},
            {"tipo": "oferta",   "producto": "Ciruela Angeleno",     "cantidad": "60 pallets",        "origen": "R.M.", "precio": "USD 10/caja"},
        ],
    },
    {
        "slug": "friopoint",
        "nombre": "FríoPoint Ltda.",
        "rut": "80.567.890-1",
        "rol": "Frigorífico",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "breve": "Almacenaje y logística en Valparaíso.",
        "email": "contacto@friopoint.cl",
        "telefono": "+56 32 444 5555",
        "direccion": "Puerto Central, Valparaíso",
        "items": [
            {"tipo": "servicio", "servicio": "Almacenaje en frío", "capacidad": "1.500 pallets", "ubicacion": "Valparaíso"},
            {"tipo": "servicio", "servicio": "Preenfriado",        "capacidad": "6 túneles",     "ubicacion": "Valparaíso"},
            {"tipo": "oferta",   "producto": "Uva Red Globe",      "cantidad": "40 pallets",     "origen": "V Región", "precio": "USD 9/caja"},
        ],
    },
    {
        "slug": "ocexport",
        "nombre": "OCExport Chile",
        "rut": "78.345.678-9",
        "rol": "Exportador",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "breve": "Exportación multiproducto.",
        "email": "export@ocexport.cl",
        "telefono": "+56 2 2345 6789",
        "direccion": "Av. Apoquindo 1234, Las Condes",
        "items": [
            {"tipo": "demanda", "producto": "Cereza Santina", "cantidad": "150 pallets", "origen": "VI-VII", "precio": "A convenir"},
        ],
    },
    {
        "slug": "transveloz",
        "nombre": "TransVeloz",
        "rut": "81.222.333-4",
        "rol": "Transporte",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "breve": "Transporte reefer nacional.",
        "email": "operaciones@transveloz.cl",
        "telefono": "+56 9 5000 1111",
        "direccion": "San Bernardo, RM",
        "items": [
            {"tipo": "servicio", "servicio": "Transporte reefer", "capacidad": "35 camiones", "ubicacion": "RM"},
        ],
    },
    {
        "slug": "aduanasfast",
        "nombre": "AduanasFast",
        "rut": "82.555.666-7",
        "rol": "Agencia de Aduanas",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "breve": "Tramitación aduanera.",
        "email": "agencia@aduanasfast.cl",
        "telefono": "+56 2 2987 6543",
        "direccion": "Valparaíso",
        "items": [
            {"tipo": "servicio", "servicio": "Despacho exportación", "capacidad": "Alta", "ubicacion": "Valparaíso"},
        ],
    },
    {
        "slug": "porthelper",
        "nombre": "PortHelper",
        "rut": "83.777.888-9",
        "rol": "Extraportuario",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "breve": "Consolidación y extraportuario.",
        "email": "info@porthelper.cl",
        "telefono": "+56 9 7000 2222",
        "direccion": "San Antonio",
        "items": [
            {"tipo": "servicio", "servicio": "Consolidación de contenedores", "capacidad": "120/día", "ubicacion": "San Antonio"},
        ],
    },
]

# =========================================================
# Helpers de sesión / carrito
# =========================================================
def is_logged():
    return "user" in session

def current_user_profile():
    u = session.get("user")
    return USER_PROFILES.get(u)

def get_cart():
    return session.setdefault("cart", [])

def add_to_cart(item_dict):
    cart = get_cart()
    cart.append(item_dict)
    session["cart"] = cart

def clear_cart():
    session["cart"] = []

def remove_from_cart(index):
    cart = get_cart()
    try:
        idx = int(index)
        if 0 <= idx < len(cart):
            cart.pop(idx)
            session["cart"] = cart
            return True
    except Exception:
        pass
    return False

# =========================================================
# Rutas
# =========================================================
@app.route("/")
def home():
    return render_template("landing.html", t=t)

# ---------- Auth ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        user = request.form.get("username", "").strip()
        pwd = request.form.get("password", "").strip()
        udata = USERS.get(user)
        if udata and udata["password"] == pwd:
            session["user"] = user
            session["usuario"] = user  # compatibilidad con templates antiguos
            flash(t("Bienvenido/a", "Welcome", "歡迎"))
            return redirect(url_for("dashboard"))
        error = t("Credenciales inválidas", "Invalid credentials", "帳密錯誤")
    return render_template("login.html", error=error, t=t)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ---------- Registro (Router + Form) ----------
@app.route("/register_router")
def register_router():
    return render_template("register_router.html", t=t)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    nacionalidad = request.args.get("nac")   # nacional / extranjero
    perfil_tipo  = request.args.get("tipo")  # compra_venta / servicios

    ROLES_COMPRA_VENTA = ["Productor", "Planta", "Packing", "Frigorífico", "Exportador", "Cliente extranjero"]
    ROLES_SERVICIOS    = ["Packing", "Frigorífico", "Transporte", "Agencia de Aduanas", "Extraportuario"]

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        email    = request.form.get("email", "").strip()
        telefono = request.form.get("phone", "").strip()
        direccion= request.form.get("address", "").strip()
        pais     = request.form.get("pais", "CL").strip()
        rol      = request.form.get("rol", "").strip()
        pft      = request.form.get("perfil_tipo", "").strip()
        rut      = request.form.get("rut", "").strip()
        nac      = request.form.get("nacionalidad", "").strip()

        if not username or not password or not rol or not pft or not nac:
            error = t("Completa los campos obligatorios.", "Please complete required fields.")
        elif username in USERS:
            error = t("El usuario ya existe.", "User already exists.")
        else:
            USERS[username] = {
                "password": password,
                "rol": rol,
                "perfil_tipo": pft,
                "pais": pais or ("CL" if nac == "nacional" else "EX"),
            }
            USER_PROFILES[username] = {
                "empresa": username.split("@")[0].replace(".", " ").title(),
                "rut": rut or ("76.000.000-0" if nac == "nacional" else None),
                "rol": rol,
                "perfil_tipo": pft,
                "pais": USERS[username]["pais"],
                "email": email or username,
                "telefono": telefono or "",
                "direccion": direccion or "",
                "descripcion": "Nuevo perfil.",
                "items": []
            }
            session["user"] = username
            session["usuario"] = username
            return redirect(url_for("dashboard"))

    return render_template(
        "register.html",
        error=error,
        nacionalidad=nacionalidad,
        perfil_tipo=perfil_tipo,
        roles_cv=ROLES_COMPRA_VENTA,
        roles_srv=ROLES_SERVICIOS,
        t=t
    )

# ---------- Dashboard ----------
@app.route("/dashboard")
def dashboard():
    if not is_logged():
        return redirect(url_for("login"))
    profile = current_user_profile()
    usuario = session.get("user")
    rol = USERS.get(usuario, {}).get("rol", "-")
    perfil_tipo = USERS.get(usuario, {}).get("perfil_tipo", "-")
    return render_template(
        "dashboard.html",
        usuario=usuario,
        rol=rol,
        perfil_tipo=perfil_tipo,
        my_company=profile or {},
        cart=get_cart(),
        t=t
    )

# ---------- Accesos (listado simple) ----------
@app.route("/accesos/<tipo>")
def accesos(tipo):
    tipo = tipo.lower()
    if tipo not in ("ventas", "compras", "servicios"):
        abort(404)

    if tipo == "servicios":
        data = []
        for c in COMPANIES:
            if c["perfil_tipo"] == "servicios" or c["rol"] in ("Packing", "Frigorífico"):
                if any(it.get("tipo") == "servicio" for it in c.get("items", [])):
                    data.append(c)
    else:
        # ventas / compras: compra_venta + (packing/frigorífico con compra/venta)
        tag = "oferta" if tipo == "ventas" else "demanda"
        data = []
        for c in COMPANIES:
            if c["perfil_tipo"] == "compra_venta" or c["rol"] in ("Packing", "Frigorífico"):
                if any(it.get("tipo") == tag for it in c.get("items", [])):
                    data.append(c)

    return render_template("accesos.html", tipo=tipo, data=data, t=t)

# ---------- Detalles (tablas con botón Agregar) ----------
@app.route("/detalles/<tipo>")
def detalles(tipo):
    tipo = tipo.lower()
    if tipo not in ("ventas", "compras", "servicios"):
        abort(404)

    if tipo in ("ventas", "compras"):
        tag = "oferta" if tipo == "ventas" else "demanda"
        data = []
        for c in COMPANIES:
            if c["perfil_tipo"] == "compra_venta" or c["rol"] in ("Packing", "Frigorífico"):
                if any(it.get("tipo") == tag for it in c.get("items", [])):
                    data.append(c)
        tpl = "detalle_ventas.html" if tipo == "ventas" else "detalle_compras.html"
        return render_template(tpl, data=data, t=t)

    # servicios
    data = []
    for c in COMPANIES:
        if c["perfil_tipo"] == "servicios" or c["rol"] in ("Packing", "Frigorífico"):
            if any(it.get("tipo") == "servicio" for it in c.get("items", [])):
                data.append(c)
    return render_template("detalle_servicios.html", data=data, t=t)

# ---------- Perfil público por slug (empresa) ----------
@app.route("/empresa/<slug>")
def empresa(slug):
    comp = next((c for c in COMPANIES if c["slug"] == slug), None)
    if not comp:
        # fallback: si el slug coincide con un username en USER_PROFILES, muestro ese perfil
        prof = USER_PROFILES.get(slug)
        if not prof:
            abort(404)
        return render_template("empresa.html", comp=prof, es_user=True, t=t)
    return render_template("empresa.html", comp=comp, es_user=False, t=t)

# ---------- Mi Perfil (edición + agregar ítems) ----------
@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    if not is_logged():
        return redirect(url_for("login"))
    prof = current_user_profile()
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
            if request.form.get("rut") is not None:
                rut_in = request.form.get("rut").strip()
                prof["rut"] = rut_in if rut_in else prof.get("rut")
            mensaje = t("Perfil actualizado.", "Profile updated.")
        elif action == "add_item":
            perfil_tipo = prof.get("perfil_tipo")
            if perfil_tipo == "servicios":
                servicio = request.form.get("servicio", "").strip()
                capacidad = request.form.get("capacidad", "").strip()
                ubicacion = request.form.get("ubicacion", "").strip()
                if servicio:
                    prof["items"].append({
                        "tipo": "servicio",
                        "servicio": servicio,
                        "capacidad": capacidad,
                        "ubicacion": ubicacion
                    })
                    mensaje = t("Servicio agregado.", "Service added.")
            else:
                subtipo  = request.form.get("subtipo", "oferta")
                producto = request.form.get("producto", "").strip()
                cantidad = request.form.get("cantidad", "").strip()
                origen   = request.form.get("origen", "").strip()
                precio   = request.form.get("precio", "").strip()
                if producto:
                    prof["items"].append({
                        "tipo": subtipo,
                        "producto": producto,
                        "cantidad": cantidad,
                        "origen": origen,
                        "precio": precio
                    })
                    mensaje = t("Ítem agregado.", "Item added.")

    return render_template("perfil.html", perfil=prof, mensaje=mensaje, t=t)

# ---------- Carrito ----------
@app.route("/cart/add", methods=["POST"])
def cart_add():
    # Recibe campos ocultos desde tablas de detalle/perfil público
    item = request.form.to_dict()
    if "empresa" not in item:
        item["empresa"] = "?"
    add_to_cart(item)
    flash(t("Agregado al carrito", "Added to cart"))
    return redirect(request.referrer or url_for("carrito"))

@app.route("/carrito", methods=["GET", "POST"])
def carrito():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "clear":
            clear_cart()
            flash(t("Carrito vaciado", "Cart cleared"))
            return redirect(url_for("carrito"))
        if action and action.startswith("remove:"):
            idx = action.split(":", 1)[1]
            if remove_from_cart(idx):
                flash(t("Ítem eliminado", "Item removed"))
            return redirect(url_for("carrito"))
    return render_template("carrito.html", cart=get_cart(), t=t)

# ---------- Ayuda ----------
@app.route("/ayuda", methods=["GET", "POST"])
def ayuda():
    msg = None
    if request.method == "POST":
        correo = request.form.get("correo", "").strip()
        mensaje = request.form.get("mensaje", "").strip()
        if correo and mensaje:
            msg = t("Hemos recibido tu mensaje. Te contactaremos pronto.", "We received your message. We'll contact you soon.")
        else:
            msg = t("Completa correo y mensaje.", "Please complete email and message.")
    return render_template("ayuda.html", mensaje=msg, t=t)

# =========================================================
# Errores (plantilla independiente para evitar bucles con base.html)
# =========================================================
@app.errorhandler(404)
def not_found(e):
    return render_template(
        "error.html",
        code=404,
        message=t("No encontrado", "Not found", "找不到頁面")
    ), 404

@app.errorhandler(500)
def server_error(e):
    return render_template(
        "error.html",
        code=500,
        message=t("Error interno", "Internal server error", "內部伺服器錯誤")
    ), 500

# =========================================================
# Run local
# =========================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
