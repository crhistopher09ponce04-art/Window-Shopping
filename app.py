import os
from copy import deepcopy
from flask import Flask, render_template, request, redirect, url_for, session, abort

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")

# ---------------------------
# Idiomas y traducciones
# ---------------------------
SUPPORTED_LANGS = ["es", "en", "zh"]  # zh = 简体
DEFAULT_LANG = "es"

def get_lang():
    return session.get("lang", DEFAULT_LANG)

def t(es_text, en_text, zh_text=None):
    """Traducción simple (es/en/zh). zh usa zh_text si existe, si no, cae a en."""
    lang = get_lang()
    if lang == "en":
        return en_text
    if lang == "zh":
        return zh_text or en_text
    return es_text

@app.route("/lang/<lang>")
def set_lang(lang):
    if lang not in SUPPORTED_LANGS:
        lang = DEFAULT_LANG
    session["lang"] = lang
    return redirect(request.referrer or url_for("home"))

# ---------------------------
# Datos de demo (in-memory)
# ---------------------------
ROLES_COMPRA_VENTA = [
    "Productor", "Planta", "Packing", "Frigorífico", "Exportador", "Cliente extranjero"
]
ROLES_SERVICIOS = [
    "Packing", "Frigorífico", "Transporte", "Agencia de Aduanas", "Extraportuario"
]

USERS = {
    # Compra/Venta
    "productor1":  {"password": "1234", "rol": "Productor",          "perfil_tipo": "compra_venta", "pais": "CL", "rut": "76.123.456-7"},
    "planta1":     {"password": "1234", "rol": "Planta",             "perfil_tipo": "compra_venta", "pais": "CL", "rut": "76.222.111-9"},
    "packing1":    {"password": "1234", "rol": "Packing",            "perfil_tipo": "compra_venta", "pais": "CL", "rut": "77.100.200-1"},
    "frigorifico1":{"password": "1234", "rol": "Frigorífico",        "perfil_tipo": "compra_venta", "pais": "CL", "rut": "77.100.300-2"},
    "exportador1": {"password": "1234", "rol": "Exportador",         "perfil_tipo": "compra_venta", "pais": "CL", "rut": "77.100.400-3"},
    "cliente1":    {"password": "1234", "rol": "Cliente extranjero", "perfil_tipo": "compra_venta", "pais": "US", "rut": "-"},

    # Servicios
    "transporte1":     {"password": "1234", "rol": "Transporte",         "perfil_tipo": "servicios", "pais": "CL", "rut": "76.555.999-4"},
    "aduana1":         {"password": "1234", "rol": "Agencia de Aduanas", "perfil_tipo": "servicios", "pais": "CL", "rut": "76.888.777-6"},
    "extraportuario1": {"password": "1234", "rol": "Extraportuario",      "perfil_tipo": "servicios", "pais": "CL", "rut": "77.333.222-5"},
}

# Perfiles visibles (usuario puede editar)
USER_PROFILES = {
    u: {
        "empresa": u.capitalize(),
        "pais": USERS[u].get("pais", "CL"),
        "rol": USERS[u]["rol"],
        "perfil_tipo": USERS[u]["perfil_tipo"],
        "rut": USERS[u].get("rut", "-"),
        "email": f"{u}@demo.cl",
        "telefono": "+56 9 0000 0000",
        "direccion": "S/N",
        "descripcion": "Perfil demo.",
        "items": []  # ver abajo estructuras por tipo
    } for u in USERS
}

# Empresas de muestra (aparecen en los listados de detalle)
COMPANIES = [
    {
        "slug": "agro-andes",
        "nombre": "Agro Andes SPA",
        "rol": "Productor",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "rut": "76.555.111-2",
        "email": "contacto@agroandes.cl",
        "telefono": "+56 9 1234 5678",
        "direccion": "La Serena, Chile",
        "breve": "Uva de mesa y arándanos.",
        "items": [
            {"id": "AA1", "tipo": "oferta",  "producto": "Uva Crimson", "cantidad": "80 pallets",  "origen": "IV Región", "precio": "A convenir"},
            {"id": "AA2", "tipo": "demanda", "producto": "Cajas plásticas", "cantidad": "15.000 und", "origen": "CL", "precio": "Oferta"}
        ]
    },
    {
        "slug": "friopoint",
        "nombre": "FríoPoint Ltda.",
        "rol": "Frigorífico",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "rut": "77.111.222-3",
        "email": "ventas@friopoint.cl",
        "telefono": "+56 32 222 3344",
        "direccion": "Valparaíso, Chile",
        "breve": "Frío y logística en Valparaíso.",
        "items": [
            {"id": "FP1", "tipo": "servicio", "servicio": "Almacenaje en frío", "capacidad": "1.200 pallets", "ubicacion": "Valparaíso"},
            {"id": "FP2", "tipo": "servicio", "servicio": "Preenfriado",        "capacidad": "8 túneles",     "ubicacion": "Valparaíso"}
        ]
    },
    {
        "slug": "pack-smart",
        "nombre": "PackSmart",
        "rol": "Packing",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "rut": "77.444.555-6",
        "email": "hello@packsmart.cl",
        "telefono": "+56 2 3210 9876",
        "direccion": "Santiago, Chile",
        "breve": "Servicios de packing fruta fresca.",
        "items": [
            {"id": "PS1", "tipo": "servicio", "servicio": "Embalaje exportación", "capacidad": "30.000 cajas/día", "ubicacion": "R.M."}
        ]
    },
    {
        "slug": "ocexport",
        "nombre": "OCExport",
        "rol": "Exportador",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "rut": "76.999.888-1",
        "email": "info@ocexport.cl",
        "telefono": "+56 9 5555 6666",
        "direccion": "Curicó, Chile",
        "breve": "Exportación multiproducto.",
        "items": [
            {"id": "OC1", "tipo": "demanda", "producto": "Cerezas", "cantidad": "150 pallets", "origen": "VI-VII", "precio": "A convenir"}
        ]
    },

    # Agentes de servicio adicionales (para que en Servicios NO salgan productores/exportadores)
    {
        "slug": "logi-trans",
        "nombre": "LogiTrans Chile",
        "rol": "Transporte",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "rut": "77.222.111-7",
        "email": "contacto@logitrans.cl",
        "telefono": "+56 9 1111 2222",
        "direccion": "San Bernardo, Chile",
        "breve": "Transporte refrigerado nacional.",
        "items": [
            {"id": "LT1", "tipo": "servicio", "servicio": "Transporte refrigerado", "capacidad": "Flota 20 camiones", "ubicacion": "RM / V / VI"}
        ]
    },
    {
        "slug": "adu-express",
        "nombre": "AduExpress",
        "rol": "Agencia de Aduanas",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "rut": "76.333.999-0",
        "email": "agencia@aduexpress.cl",
        "telefono": "+56 2 2345 6789",
        "direccion": "Valparaíso, Chile",
        "breve": "Despacho aduanero para fruta fresca.",
        "items": [
            {"id": "AE1", "tipo": "servicio", "servicio": "Agenciamiento Aduanero", "capacidad": "24/7 temporada", "ubicacion": "PUERTO VAP / SAN A."}
        ]
    },
    {
        "slug": "extra-port",
        "nombre": "ExtraPort",
        "rol": "Extraportuario",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "rut": "77.600.300-9",
        "email": "ops@export.cl",
        "telefono": "+56 32 345 6789",
        "direccion": "San Antonio, Chile",
        "breve": "Servicios extraportuarios y consolidación.",
        "items": [
            {"id": "EP1", "tipo": "servicio", "servicio": "Consolidación/Desconsolidación", "capacidad": "6 andenes", "ubicacion": "SAN A."}
        ]
    },
]

# Carrito (por sesión)
def get_cart():
    cart = session.get("cart")
    if not isinstance(cart, list):
        cart = []
    session["cart"] = cart
    return cart

# ---------------------------
# Helpers
# ---------------------------
def require_login():
    if "usuario" not in session:
        return False
    return True

def current_user():
    u = session.get("usuario")
    return u, USERS.get(u)

def search_filter_companies(data, q):
    """Filtra por búsqueda simple"""
    if not q:
        return data
    q = q.strip().lower()
    filtered = []
    for c in data:
        base = f"{c.get('nombre','')} {c.get('rol','')} {c.get('pais','')} {c.get('breve','')}".lower()
        if q in base:
            filtered.append(c)
            continue
        # Buscar en items
        items = c.get("items", []) or []
        for it in items:
            joined = " ".join(str(v) for v in it.values()).lower()
            if q in joined:
                filtered.append(c)
                break
    return filtered

# ---------------------------
# Rutas
# ---------------------------
@app.route("/")
def home():
    return render_template("landing.html", t=t)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()
        user = USERS.get(username)
        if user and user["password"] == password:
            session["usuario"] = username
            return redirect(url_for("dashboard"))
        else:
            error = t("Usuario o clave inválidos.", "Invalid user or password.", "用户或密码无效。")
    return render_template("login.html", error=error, t=t)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# Registro (router + form)
@app.route("/register_router")
def register_router():
    return render_template("register_router.html", t=t)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    nacionalidad = request.args.get("nac")   # nacional / extranjero
    perfil_tipo  = request.args.get("tipo")  # compra_venta / servicios

    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()
        email    = request.form.get("email","").strip()
        telefono = request.form.get("phone","").strip()
        direccion= request.form.get("address","").strip()
        pais     = request.form.get("pais","CL").strip()
        rol      = request.form.get("rol","").strip()
        perfil_tipo = request.form.get("perfil_tipo","").strip()
        nac      = request.form.get("nacionalidad","").strip()
        rut      = request.form.get("rut","-").strip()

        if not username or not password or not rol or not perfil_tipo or not nac:
            error = t("Completa los campos obligatorios.", "Please complete required fields.", "请填写必填字段。")
        elif username in USERS:
            error = t("El usuario ya existe.", "User already exists.", "用户已存在。")
        else:
            USERS[username] = {
                "password": password,
                "rol": rol,
                "perfil_tipo": perfil_tipo,
                "pais": pais or ("CL" if nac == "nacional" else "EX"),
                "rut": rut or "-"
            }
            USER_PROFILES[username] = {
                "empresa": username.capitalize(),
                "pais": USERS[username]["pais"],
                "rol": rol,
                "perfil_tipo": perfil_tipo,
                "rut": rut or "-",
                "email": email or f"{username}@mail.com",
                "telefono": telefono or "",
                "direccion": direccion or "",
                "descripcion": "Nuevo perfil.",
                "items": []
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
        t=t
    )

@app.route("/dashboard")
def dashboard():
    if not require_login():
        return redirect(url_for("login"))
    username, user = current_user()
    my_company = USER_PROFILES.get(username, {})
    return render_template(
        "dashboard.html",
        usuario=username,
        rol=user["rol"],
        perfil_tipo=user["perfil_tipo"],
        my_company=my_company,
        cart=get_cart(),
        t=t
    )

# ===== Detalles =====
@app.route("/detalles/ventas")
def detalle_ventas():
    q = request.args.get("q", "")
    # Solo empresas de compra_venta con items de oferta (ventas)
    base = [c for c in COMPANIES if c["perfil_tipo"] == "compra_venta"]
    data = []
    for c in base:
        items = [it for it in c.get("items", []) if it.get("tipo") == "oferta"]
        if items:
            c2 = deepcopy(c)
            c2["items"] = items
            data.append(c2)
    data = search_filter_companies(data, q)
    return render_template("detalle_ventas.html", data=data, q=q, t=t)

@app.route("/detalles/compras")
def detalle_compras():
    q = request.args.get("q", "")
    # Solo empresas de compra_venta con items de demanda (compras)
    base = [c for c in COMPANIES if c["perfil_tipo"] == "compra_venta"]
    data = []
    for c in base:
        items = [it for it in c.get("items", []) if it.get("tipo") == "demanda"]
        if items:
            c2 = deepcopy(c)
            c2["items"] = items
            data.append(c2)
    data = search_filter_companies(data, q)
    return render_template("detalle_compras.html", data=data, q=q, t=t)

@app.route("/detalles/servicios")
def detalle_servicios():
    q = request.args.get("q", "")
    # Solo empresas de servicios (Packing, Frigorífico, Transporte, Agencia de Aduanas, Extraportuario)
    base = [c for c in COMPANIES if c["perfil_tipo"] == "servicios"]
    data = search_filter_companies(base, q)
    return render_template("detalle_servicios.html", data=data, q=q, t=t)

# Perfil público de una empresa/usuario
@app.route("/empresa/<slug>")
def empresa(slug):
    comp = next((c for c in COMPANIES if c["slug"] == slug), None)
    if comp:
        return render_template("empresa.html", comp=comp, es_user=False, t=t)
    # Si no es de COMPANIES, puede ser un usuario por username
    prof = USER_PROFILES.get(slug)
    if not prof:
        abort(404)
    comp_like = {
        "slug": slug,
        "nombre": prof["empresa"],
        "rol": prof["rol"],
        "perfil_tipo": prof["perfil_tipo"],
        "pais": prof["pais"],
        "rut": prof.get("rut","-"),
        "email": prof.get("email",""),
        "telefono": prof.get("telefono",""),
        "direccion": prof.get("direccion",""),
        "breve": prof.get("descripcion",""),
        "items": prof.get("items", [])
    }
    return render_template("empresa.html", comp=comp_like, es_user=True, t=t)

# Perfil propio (edición + agregar ítems)
@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    if not require_login():
        return redirect(url_for("login"))
    username = session["usuario"]
    prof = USER_PROFILES.get(username)
    if not prof:
        abort(404)

    msg = None
    if request.method == "POST":
        action = request.form.get("action")
        if action == "save_profile":
            prof["empresa"]    = request.form.get("empresa", prof["empresa"]).strip()
            prof["email"]      = request.form.get("email", prof["email"]).strip()
            prof["telefono"]   = request.form.get("telefono", prof["telefono"]).strip()
            prof["direccion"]  = request.form.get("direccion", prof["direccion"]).strip()
            prof["rut"]        = request.form.get("rut", prof.get("rut","-")).strip() or "-"
            prof["descripcion"]= request.form.get("descripcion", prof["descripcion"]).strip()
            msg = t("Perfil actualizado.", "Profile updated.", "资料已更新。")
        elif action == "add_item":
            if prof.get("perfil_tipo") == "servicios":
                servicio  = request.form.get("servicio","").strip()
                capacidad = request.form.get("capacidad","").strip()
                ubicacion = request.form.get("ubicacion","").strip()
                if servicio:
                    prof["items"].append({
                        "id": f"U{len(prof['items'])+1}",
                        "tipo": "servicio",
                        "servicio": servicio,
                        "capacidad": capacidad,
                        "ubicacion": ubicacion
                    })
                    msg = t("Servicio agregado.", "Service added.", "服务已添加。")
            else:
                subtipo  = request.form.get("subtipo","oferta")
                producto = request.form.get("producto","").strip()
                cantidad = request.form.get("cantidad","").strip()
                origen   = request.form.get("origen","").strip()
                precio   = request.form.get("precio","").strip()
                if producto:
                    prof["items"].append({
                        "id": f"U{len(prof['items'])+1}",
                        "tipo": subtipo,
                        "producto": producto,
                        "cantidad": cantidad,
                        "origen": origen,
                        "precio": precio
                    })
                    msg = t("Ítem agregado.", "Item added.", "项目已添加。")

    return render_template("perfil.html", perfil=prof, mensaje=msg, t=t)

# Carrito
@app.route("/cart")
def cart_view():
    return render_template("carrito.html", cart=get_cart(), t=t)

@app.route("/cart/add", methods=["POST"])
def cart_add():
    item = request.form.to_dict()
    # asegurar campos serializables string
    cleaned = {k: str(v) for k, v in item.items()}
    cart = get_cart()
    cart.append(cleaned)
    session["cart"] = cart
    return redirect(request.referrer or url_for("cart_view"))

@app.route("/cart/clear")
def cart_clear():
    session["cart"] = []
    return redirect(url_for("cart_view"))

# Centro de ayuda (simulado)
@app.route("/ayuda", methods=["GET", "POST"])
def ayuda():
    enviado = False
    if request.method == "POST":
        nombre  = request.form.get("nombre","").strip()
        correo  = request.form.get("correo","").strip()
        asunto  = request.form.get("asunto","").strip()
        mensaje = request.form.get("mensaje","").strip()
        # Simulación de envío: guardamos en sesión como historial simple (lista JSON-serializable)
        history = session.get("help_messages")
        if not isinstance(history, list):
            history = []
        history.append({
            "nombre": nombre, "correo": correo, "asunto": asunto, "mensaje": mensaje
        })
        session["help_messages"] = history
        enviado = True
    history = session.get("help_messages")
    if not isinstance(history, list):
        history = []
    return render_template("ayuda.html", enviado=enviado, history=history, t=t)

# ---------------------------
# Errores
# ---------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message=t("No encontrado", "Not found", "未找到"), t=t), 404

@app.errorhandler(500)
def server_error(e):
    # Nota: mantenemos simple y sin serializar sets/objetos raros
    return render_template("error.html", code=500, message=t("Error interno", "Internal server error", "内部服务器错误"), t=t), 500

# ---------------------------
# Run local
# ---------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
