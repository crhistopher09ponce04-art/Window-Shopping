import os
from flask import Flask, render_template, request, redirect, url_for, session, abort

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")

# =========================================================
# Utilidades de idioma
# =========================================================
def t(es, en, zh=None):
    """Traductor simple ES/EN/ZH según session['lang']."""
    lang = session.get("lang", "es")
    if lang == "en":
        return en
    if lang == "zh" and zh:
        return zh
    return es

@app.route("/set_lang/<lang>")
def set_lang(lang):
    session["lang"] = lang if lang in ("es", "en", "zh") else "es"
    return redirect(request.referrer or url_for("home"))

# =========================================================
# Datos de demo / "DB" en memoria
# =========================================================
ROLES_COMPRA_VENTA = ["Productor", "Planta", "Packing", "Frigorífico", "Exportador", "Cliente extranjero"]
ROLES_SERVICIOS = ["Packing", "Frigorífico", "Transporte", "Agencia de Aduanas", "Extraportuario"]

USERS = {
    # Compra/Venta
    "productor1":     {"password": "1234", "rol": "Productor",          "perfil_tipo": "compra_venta", "pais": "CL"},
    "planta1":        {"password": "1234", "rol": "Planta",             "perfil_tipo": "compra_venta", "pais": "CL"},
    "exportador1":    {"password": "1234", "rol": "Exportador",         "perfil_tipo": "compra_venta", "pais": "CL"},
    "cliente1":       {"password": "1234", "rol": "Cliente extranjero", "perfil_tipo": "compra_venta", "pais": "US"},

    # Servicios
    "packing1":       {"password": "1234", "rol": "Packing",            "perfil_tipo": "servicios",    "pais": "CL"},
    "frigorifico1":   {"password": "1234", "rol": "Frigorífico",        "perfil_tipo": "servicios",    "pais": "CL"},
    "transporte1":    {"password": "1234", "rol": "Transporte",         "perfil_tipo": "servicios",    "pais": "CL"},
    "aduana1":        {"password": "1234", "rol": "Agencia de Aduanas", "perfil_tipo": "servicios",    "pais": "CL"},
    "extraportuario1":{"password": "1234", "rol": "Extraportuario",     "perfil_tipo": "servicios",    "pais": "CL"},

    # Extra demo multi-ámbito (Packing/Frigorífico también compra/venta)
    "packing_cv":     {"password": "1234", "rol": "Packing",            "perfil_tipo": "compra_venta", "pais": "CL"},
    "frigorifico_cv": {"password": "1234", "rol": "Frigorífico",        "perfil_tipo": "compra_venta", "pais": "CL"},
}

# Perfiles públicos (clave = username). Incluye 2 con "Ciruela".
USER_PROFILES = {
    "productor1": {
        "empresa": "Agro Andes SPA",
        "rut": "76.123.456-7",
        "rol": "Productor",
        "perfil_tipo": "compra_venta",
        "pais": USERS["productor1"]["pais"],
        "email": "contacto@agroandes.cl",
        "telefono": "+56 9 1111 1111",
        "direccion": "Ruta 5 km 123, IV Región",
        "descripcion": "Uva de mesa y arándanos.",
        "items": [
            {"tipo": "oferta", "producto": "Uva Crimson", "cantidad": "80 pallets", "origen": "IV Región", "precio": "A convenir"},
            {"tipo": "oferta", "producto": "Ciruela D'Agen", "cantidad": "40 pallets", "origen": "V Región", "precio": "A convenir"},  # Ciruela 1
        ],
    },
    "planta1": {
        "empresa": "Planta Valle Central",
        "rut": "77.234.567-8",
        "rol": "Planta",
        "perfil_tipo": "compra_venta",
        "pais": USERS["planta1"]["pais"],
        "email": "ventas@vallecentral.cl",
        "telefono": "+56 9 2222 2222",
        "direccion": "Camino Industrial 555, R.M.",
        "descripcion": "Proceso primario y secundario.",
        "items": [
            {"tipo": "demanda", "producto": "Cajas plásticas", "cantidad": "15.000 und", "origen": "CL", "precio": "Oferta"},
        ],
    },
    "exportador1": {
        "empresa": "OCExport",
        "rut": "79.345.678-9",
        "rol": "Exportador",
        "perfil_tipo": "compra_venta",
        "pais": USERS["exportador1"]["pais"],
        "email": "info@ocexport.cl",
        "telefono": "+56 9 3333 3333",
        "direccion": "Av. Exportadores 45, Santiago",
        "descripcion": "Exportación multiproducto.",
        "items": [
            {"tipo": "demanda", "producto": "Cerezas", "cantidad": "150 pallets", "origen": "VI-VII", "precio": "A convenir"},
            {"tipo": "demanda", "producto": "Ciruela Larry Anne", "cantidad": "60 pallets", "origen": "VI Región", "precio": "A convenir"},  # Ciruela 2
        ],
    },
    "cliente1": {
        "empresa": "Global Buyer LLC",
        "rut": None,
        "rol": "Cliente extranjero",
        "perfil_tipo": "compra_venta",
        "pais": USERS["cliente1"]["pais"],
        "email": "contact@globalbuyer.com",
        "telefono": "+1 555 0100",
        "direccion": "Miami, USA",
        "descripcion": "Mayorista en EEUU.",
        "items": [
            {"tipo": "demanda", "producto": "Uva Thompson", "cantidad": "400 pallets", "origen": "US", "precio": "A convenir"},
        ],
    },
    # Servicios
    "packing1": {
        "empresa": "PackSmart",
        "rut": "78.456.789-0",
        "rol": "Packing",
        "perfil_tipo": "servicios",
        "pais": USERS["packing1"]["pais"],
        "email": "info@packsmart.cl",
        "telefono": "+56 9 4444 4444",
        "direccion": "Sector Industrial 12, Rancagua",
        "descripcion": "Servicios de packing y embalaje.",
        "items": [
            {"tipo": "servicio", "servicio": "Embalaje exportación", "capacidad": "30.000 cajas/día", "ubicacion": "R.M."}
        ],
    },
    "frigorifico1": {
        "empresa": "FríoPoint Ltda.",
        "rut": "80.567.890-1",
        "rol": "Frigorífico",
        "perfil_tipo": "servicios",
        "pais": USERS["frigorifico1"]["pais"],
        "email": "contacto@friopoint.cl",
        "telefono": "+56 32 444 5555",
        "direccion": "Puerto Central, Valparaíso",
        "descripcion": "Almacenaje refrigerado y logística.",
        "items": [
            {"tipo": "servicio", "servicio": "Almacenaje en frío", "capacidad": "1.200 pallets", "ubicacion": "Valparaíso"},
            {"tipo": "servicio", "servicio": "Preenfriado", "capacidad": "8 túneles", "ubicacion": "Valparaíso"},
        ],
    },
    "transporte1": {
        "empresa": "TransLog",
        "rut": "76.987.654-3",
        "rol": "Transporte",
        "perfil_tipo": "servicios",
        "pais": USERS["transporte1"]["pais"],
        "email": "contacto@translog.cl",
        "telefono": "+56 9 5555 5555",
        "direccion": "Ruta 68, KM 23",
        "descripcion": "Transporte refrigerado nacional.",
        "items": [
            {"tipo": "servicio", "servicio": "Transporte refrigerado", "capacidad": "Flota 20 camiones", "ubicacion": "Centro-Sur"},
        ],
    },
    "aduana1": {
        "empresa": "Aduanet",
        "rut": "70.123.777-5",
        "rol": "Agencia de Aduanas",
        "perfil_tipo": "servicios",
        "pais": USERS["aduana1"]["pais"],
        "email": "servicios@aduanet.cl",
        "telefono": "+56 2 2345 6789",
        "direccion": "Santiago",
        "descripcion": "Servicios de despacho aduanero.",
        "items": [
            {"tipo": "servicio", "servicio": "Despacho aduanero", "capacidad": "Export e Import", "ubicacion": "Puertos CL"},
        ],
    },
    "extraportuario1": {
        "empresa": "PortaPlus",
        "rut": "72.321.111-0",
        "rol": "Extraportuario",
        "perfil_tipo": "servicios",
        "pais": USERS["extraportuario1"]["pais"],
        "email": "operaciones@portaplus.cl",
        "telefono": "+56 32 222 3344",
        "direccion": "San Antonio",
        "descripcion": "Servicios extraportuarios.",
        "items": [
            {"tipo": "servicio", "servicio": "Consolidado/Desconsolidado", "capacidad": "100 cont/día", "ubicacion": "San Antonio"},
        ],
    },
    # Multi-ámbito: Packing y Frigorífico también con compra/venta
    "packing_cv": {
        "empresa": "PackSmart CV",
        "rut": "88.111.222-3",
        "rol": "Packing",
        "perfil_tipo": "compra_venta",
        "pais": USERS["packing_cv"]["pais"],
        "email": "cv@packsmart.cl",
        "telefono": "+56 9 6666 6666",
        "direccion": "Rancagua",
        "descripcion": "Packing con operación comercial.",
        "items": [
            {"tipo": "oferta", "producto": "Manzana Gala", "cantidad": "50 pallets", "origen": "VI Región", "precio": "A convenir"},
        ],
    },
    "frigorifico_cv": {
        "empresa": "FríoPoint CV",
        "rut": "89.222.333-4",
        "rol": "Frigorífico",
        "perfil_tipo": "compra_venta",
        "pais": USERS["frigorifico_cv"]["pais"],
        "email": "cv@friopoint.cl",
        "telefono": "+56 9 7777 7777",
        "direccion": "Valparaíso",
        "descripcion": "Frigorífico con operación comercial.",
        "items": [
            {"tipo": "demanda", "producto": "Uva Red Globe", "cantidad": "70 pallets", "origen": "V Región", "precio": "A convenir"},
        ],
    },
}

# Empresas de muestra (para accesos y detalles). Packing y Frigorífico aparecen en ambos ámbitos.
COMPANIES = [
    {
        "slug": "agro-andes",
        "nombre": "Agro Andes SPA",
        "rut": "76.123.456-7",
        "rol": "Productor",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "breve": "Uva de mesa y arándanos.",
        "email": "contacto@agroandes.cl",
        "telefono": "+56 9 1111 1111",
        "items": [
            {"tipo": "oferta", "producto": "Uva Crimson", "cantidad": "80 pallets", "origen": "IV Región", "precio": "A convenir"},
            {"tipo": "oferta", "producto": "Ciruela D'Agen", "cantidad": "40 pallets", "origen": "V Región", "precio": "A convenir"},  # Ciruela 1
        ],
    },
    {
        "slug": "friopoint",
        "nombre": "FríoPoint Ltda.",
        "rut": "80.567.890-1",
        "rol": "Frigorífico",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "breve": "Frío y logística en Valparaíso.",
        "email": "contacto@friopoint.cl",
        "telefono": "+56 32 444 5555",
        "items": [
            {"tipo": "servicio", "servicio": "Almacenaje en frío", "capacidad": "1.200 pallets", "ubicacion": "Valparaíso"},
            {"tipo": "servicio", "servicio": "Preenfriado", "capacidad": "8 túneles", "ubicacion": "Valparaíso"},
        ],
    },
    {
        "slug": "pack-smart",
        "nombre": "PackSmart",
        "rut": "78.456.789-0",
        "rol": "Packing",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "breve": "Servicios de packing fruta fresca.",
        "email": "info@packsmart.cl",
        "telefono": "+56 9 4444 4444",
        "items": [
            {"tipo": "servicio", "servicio": "Embalaje exportación", "capacidad": "30.000 cajas/día", "ubicacion": "R.M."}
        ],
    },
    {
        "slug": "ocexport",
        "nombre": "OCExport",
        "rut": "79.345.678-9",
        "rol": "Exportador",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "breve": "Exportación multiproducto.",
        "email": "info@ocexport.cl",
        "telefono": "+56 9 3333 3333",
        "items": [
            {"tipo": "demanda", "producto": "Cerezas", "cantidad": "150 pallets", "origen": "VI-VII", "precio": "A convenir"},
            {"tipo": "demanda", "producto": "Ciruela Larry Anne", "cantidad": "60 pallets", "origen": "VI Región", "precio": "A convenir"},  # Ciruela 2
        ],
    },
    # MISMO packing y frigorífico en compra/venta
    {
        "slug": "pack-smart-cv",
        "nombre": "PackSmart CV",
        "rut": "88.111.222-3",
        "rol": "Packing",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "breve": "Packing con operación comercial.",
        "email": "cv@packsmart.cl",
        "telefono": "+56 9 6666 6666",
        "items": [
            {"tipo": "oferta", "producto": "Manzana Gala", "cantidad": "50 pallets", "origen": "VI Región", "precio": "A convenir"},
        ],
    },
    {
        "slug": "friopoint-cv",
        "nombre": "FríoPoint CV",
        "rut": "89.222.333-4",
        "rol": "Frigorífico",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "breve": "Frigorífico con operación comercial.",
        "email": "cv@friopoint.cl",
        "telefono": "+56 9 7777 7777",
        "items": [
            {"tipo": "demanda", "producto": "Uva Red Globe", "cantidad": "70 pallets", "origen": "V Región", "precio": "A convenir"},
        ],
    },
]

# =========================================================
# Helpers carrito
# =========================================================
def get_cart():
    return session.setdefault("cart", [])

def add_to_cart(item_dict):
    cart = get_cart()
    cart.append(item_dict)
    session["cart"] = cart

# =========================================================
# Rutas
# =========================================================
@app.route("/")
def home():
    return render_template("landing.html", t=t)

@app.route("/favicon.ico")
def favicon():
    # Evita que /favicon.ico dispare el error handler
    return ("", 204)

# ---------- Autenticación ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = USERS.get(username)
        if user and user["password"] == password:
            # Seteamos ambas llaves para no romper plantillas antiguas
            session["usuario"] = username
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            error = t("Credenciales inválidas", "Invalid credentials", "帳密無效")
    return render_template("login.html", error=error, t=t)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ---------- Registro ----------
@app.route("/register_router")
def register_router():
    # Pantalla que deja elegir nacional/extranjero
    return render_template("register_router.html", t=t)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    nacionalidad = request.args.get("nac")
    perfil_tipo = request.args.get("tipo")
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        email = request.form.get("email", "").strip()
        telefono = request.form.get("phone", "").strip()
        direccion = request.form.get("address", "").strip()
        rut = request.form.get("rut", "").strip()
        pais = request.form.get("pais", "CL").strip()
        rol = request.form.get("rol", "").strip()
        perfil_tipo = request.form.get("perfil_tipo", "").strip()
        nac = request.form.get("nacionalidad", "").strip()

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
            session["user"] = username
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

# ---------- Panel ----------
@app.route("/dashboard")
def dashboard():
    if "usuario" not in session and "user" not in session:
        return redirect(url_for("login"))
    username = session.get("usuario") or session.get("user")
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

# ---------- Listados tipo "accesos" (opcional, tus plantillas lo manejan) ----------
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

# ---------- Detalles (ventas/compras/servicios) ----------
@app.route("/detalles/<tipo>")
def detalles(tipo):
    tipo = tipo.lower()
    if tipo not in ["ventas", "compras", "servicios"]:
        abort(404)

    # Combinamos COMPANIES + USER_PROFILES para alimentar data
    def company_like_from_profile(slug, prof):
        return {
            "slug": slug,
            "nombre": prof.get("empresa", slug),
            "rut": prof.get("rut"),
            "rol": prof.get("rol"),
            "perfil_tipo": prof.get("perfil_tipo"),
            "pais": prof.get("pais", "CL"),
            "breve": prof.get("descripcion", ""),
            "email": prof.get("email"),
            "telefono": prof.get("telefono"),
            "items": prof.get("items", []),
        }

    merged = []
    merged.extend(COMPANIES)
    # Agregamos perfiles de usuarios
    for slug, prof in USER_PROFILES.items():
        merged.append(company_like_from_profile(slug, prof))

    if tipo == "servicios":
        # Filtramos empresas/perfiles que tengan items de tipo "servicio"
        data = []
        for c in merged:
            has_service = any(i.get("tipo") == "servicio" for i in c.get("items", []))
            if has_service:
                data.append(c)
        template = "detalle_servicios.html"
    elif tipo == "ventas":
        # Ofertas
        data = []
        for c in merged:
            has_offer = any(i.get("tipo") == "oferta" for i in c.get("items", []))
            if has_offer:
                data.append(c)
        template = "detalle_ventas.html"
    else:
        # Compras (demandas)
        data = []
        for c in merged:
            has_demand = any(i.get("tipo") == "demanda" for i in c.get("items", []))
            if has_demand:
                data.append(c)
        template = "detalle_compras.html"

    return render_template(template, data=data, t=t)

# ---------- Perfil público de empresa ----------
@app.route("/empresa/<slug>")
def empresa(slug):
    comp = next((c for c in COMPANIES if c["slug"] == slug), None)
    if comp:
        return render_template("empresa.html", comp=comp, es_user=False, t=t)

    prof = USER_PROFILES.get(slug)
    if prof:
        # Normalizamos campos para el template empresa.html
        prof_norm = {
            "nombre": prof.get("empresa", slug),
            "empresa": prof.get("empresa", slug),
            "rut": prof.get("rut"),
            "rol": prof.get("rol"),
            "perfil_tipo": prof.get("perfil_tipo"),
            "pais": prof.get("pais", "CL"),
            "breve": prof.get("descripcion"),
            "descripcion": prof.get("descripcion"),
            "email": prof.get("email"),
            "telefono": prof.get("telefono"),
            "items": prof.get("items", []),
        }
        return render_template("empresa.html", comp=prof_norm, es_user=True, t=t)

    abort(404)

# ---------- Mi perfil (usuario logueado) ----------
@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    if "usuario" not in session and "user" not in session:
        return redirect(url_for("login"))
    username = session.get("usuario") or session.get("user")
    prof = USER_PROFILES.get(username)
    if not prof:
        abort(404)

    mensaje = None
    if request.method == "POST":
        action = request.form.get("action")
        if action == "save_profile":
            prof["empresa"] = request.form.get("empresa", prof.get("empresa", "")).strip()
            prof["email"] = request.form.get("email", prof.get("email", "")).strip()
            prof["telefono"] = request.form.get("telefono", prof.get("telefono", "")).strip()
            prof["direccion"] = request.form.get("direccion", prof.get("direccion", "")).strip()
            prof["descripcion"] = request.form.get("descripcion", prof.get("descripcion", "")).strip()
            prof["rut"] = request.form.get("rut", prof.get("rut", "")).strip()
            mensaje = t("Perfil actualizado.", "Profile updated.", "已更新")
        elif action == "add_item":
            perfil_tipo = prof.get("perfil_tipo")
            if perfil_tipo == "servicios":
                servicio = request.form.get("servicio", "").strip()
                capacidad = request.form.get("capacidad", "").strip()
                ubicacion = request.form.get("ubicacion", "").strip()
                if servicio:
                    prof.setdefault("items", []).append({
                        "tipo": "servicio",
                        "servicio": servicio,
                        "capacidad": capacidad,
                        "ubicacion": ubicacion
                    })
                    mensaje = t("Servicio agregado.", "Service added.", "已新增服務")
            else:
                subtipo = request.form.get("subtipo", "oferta")
                producto = request.form.get("producto", "").strip()
                cantidad = request.form.get("cantidad", "").strip()
                origen = request.form.get("origen", "").strip()
                precio = request.form.get("precio", "").strip()
                if producto:
                    prof.setdefault("items", []).append({
                        "tipo": subtipo,
                        "producto": producto,
                        "cantidad": cantidad,
                        "origen": origen,
                        "precio": precio
                    })
                    mensaje = t("Ítem agregado.", "Item added.", "已新增項目")

    return render_template("perfil.html", perfil=prof, mensaje=mensaje, t=t)

# ---------- Carrito ----------
@app.route("/carrito")
def carrito():
    return render_template("carrito.html", cart=get_cart(), t=t)

@app.route("/cart/add", methods=["POST"])
def cart_add():
    # Recibe datos desde los botones "Agregar"
    item = {
        "empresa": request.form.get("empresa"),
        "tipo": request.form.get("tipo"),
        "producto": request.form.get("producto"),
        "servicio": request.form.get("servicio"),
    }
    add_to_cart(item)
    return redirect(request.referrer or url_for("carrito"))

# Compatibilidad con una ruta antigua que tenías
@app.route("/add_to_cart/<user>/<int:item_idx>")
def add_item(user, item_idx):
    prof = USER_PROFILES.get(user)
    if not prof:
        return redirect(url_for("dashboard"))
    items = prof.get("items", [])
    if 0 <= item_idx < len(items):
        to_add = items[item_idx].copy()
        to_add["empresa"] = prof.get("empresa", user)
        add_to_cart(to_add)
    return redirect(url_for("carrito"))

# ---------- Ayuda ----------
@app.route("/ayuda", methods=["GET", "POST"])
def ayuda():
    mensaje = None
    if request.method == "POST":
        correo = request.form.get("correo")
        msg = request.form.get("mensaje")
        # Aquí podrías enviar correo / guardar ticket. Por ahora, confirmamos.
        mensaje = t("Tu mensaje fue enviado. Te contactaremos pronto.",
                    "Your message was sent. We'll contact you soon.",
                    "訊息已送出，我們將儘快聯繫您。")
    return render_template("ayuda.html", mensaje=mensaje, t=t)

# ---------- Errores ----------
@app.errorhandler(404)
def not_found(e):
    # error.html es una plantilla independiente (no extiende base) para evitar recursión
    return render_template("error.html", code=404, message=t("No encontrado", "Not found", "查無此頁")), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message=t("Error interno", "Internal server error", "內部伺服器錯誤")), 500

# ---------- Run local ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
