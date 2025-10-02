import os
from flask import Flask, render_template, request, redirect, url_for, session, abort, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")

# ---------------------------
# Idiomas y traducciones
# ---------------------------
SUPPORTED_LANGS = ["es", "en", "zh"]
DEFAULT_LANG = "es"

def get_lang():
    return session.get("lang", DEFAULT_LANG)

def t(es_text, en_text, zh_text=None):
    """Traducción semi-formal (ES/EN/中文). Si no hay zh_text, cae a EN."""
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
# Datos de demo / “DB” en memoria
# ---------------------------
ROLES_COMPRA_VENTA = [
    "Productor", "Planta", "Packing", "Frigorífico", "Exportador", "Cliente extranjero"
]
ROLES_SERVICIOS = [
    "Packing", "Frigorífico", "Transporte", "Agencia de Aduanas", "Extraportuario"
]

# Usuarios de prueba (username: info)
USERS = {
    # compra/venta
    "productor1": {"password": "1234", "rol": "Productor", "perfil_tipo": "compra_venta", "pais": "CL", "rut": "76.111.111-1"},
    "planta1": {"password": "1234", "rol": "Planta", "perfil_tipo": "compra_venta", "pais": "CL", "rut": "96.222.222-2"},
    "packing1": {"password": "1234", "rol": "Packing", "perfil_tipo": "servicios", "pais": "CL", "rut": "65.333.333-3"},
    "frigorifico1": {"password": "1234", "rol": "Frigorífico", "perfil_tipo": "servicios", "pais": "CL", "rut": "59.444.444-4"},
    "exportador1": {"password": "1234", "rol": "Exportador", "perfil_tipo": "compra_venta", "pais": "CL", "rut": "77.555.555-5"},
    "cliente1": {"password": "1234", "rol": "Cliente extranjero", "perfil_tipo": "compra_venta", "pais": "US", "rut": ""},
    # servicios
    "transporte1": {"password": "1234", "rol": "Transporte", "perfil_tipo": "servicios", "pais": "CL", "rut": "80.666.666-6"},
    "aduana1": {"password": "1234", "rol": "Agencia de Aduanas", "perfil_tipo": "servicios", "pais": "CL", "rut": "81.777.777-7"},
    "extraportuario1": {"password": "1234", "rol": "Extraportuario", "perfil_tipo": "servicios", "pais": "CL", "rut": "82.888.888-8"},
}

# Perfiles (clave = username) visibles públicamente
USER_PROFILES = {
    u: {
        "empresa": u.capitalize(),
        "pais": USERS[u].get("pais", "CL"),
        "rol": USERS[u]["rol"],
        "perfil_tipo": USERS[u]["perfil_tipo"],
        "rut": USERS[u].get("rut", ""),
        "email": f"{u}@demo.cl",
        "telefono": "+56 9 0000 0000",
        "direccion": "S/N",
        "descripcion": "Perfil de demostración.",
        "items": []
    } for u in USERS
}

# Empresas ficticias para catálogo (perfiles “corporativos”)
COMPANIES = [
    {
        "slug": "agro-andes",
        "nombre": "Agro Andes SPA",
        "rol": "Productor",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "rut": "76.999.111-0",
        "email": "contacto@agroandes.cl",
        "telefono": "+56 2 2345 6789",
        "direccion": "Parcela 12, Vicuña, Coquimbo",
        "web": "https://agroandes.cl",
        "breve": "Uva de mesa y arándanos de exportación.",
        "items": [
            {"tipo": "oferta", "producto": "Uva Crimson", "variedad": "Crimson Seedless", "calibre": "L", "cantidad": "80 pallets", "origen": "IV Región", "precio": "A convenir"},
            {"tipo": "demanda", "producto": "Cajas plásticas", "cantidad": "15.000 und", "origen": "CL", "precio": "Oferta"}
        ]
    },
    {
        "slug": "friopoint",
        "nombre": "FríoPoint Ltda.",
        "rol": "Frigorífico",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "rut": "59.120.450-1",
        "email": "comercial@friopoint.cl",
        "telefono": "+56 32 265 1122",
        "direccion": "Puerto de Valparaíso, Sitio 3",
        "web": "https://friopoint.cl",
        "breve": "Frío y logística en Valparaíso.",
        "items": [
            {"tipo": "servicio", "servicio": "Almacenaje en frío", "capacidad": "1.200 pallets", "ubicacion": "Valparaíso"},
            {"tipo": "servicio", "servicio": "Preenfriado", "capacidad": "8 túneles", "ubicacion": "Valparaíso"}
        ]
    },
    {
        "slug": "pack-smart",
        "nombre": "PackSmart",
        "rol": "Packing",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "rut": "65.777.300-9",
        "email": "ventas@packsmart.cl",
        "telefono": "+56 9 4455 2211",
        "direccion": "Camino a Buin 1450, R.M.",
        "web": "",
        "breve": "Servicios de packing fruta fresca.",
        "items": [
            {"tipo": "servicio", "servicio": "Embalaje exportación", "capacidad": "30.000 cajas/día", "ubicacion": "R.M."}
        ]
    },
    {
        "slug": "ruta-sur",
        "nombre": "RutaSur Logistics",
        "rol": "Transporte",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "rut": "80.321.654-3",
        "email": "ops@rutasur.cl",
        "telefono": "+56 2 2999 7777",
        "direccion": "Américo Vespucio 1001, RM",
        "web": "",
        "breve": "Transporte refrigerado nacional.",
        "items": [
            {"tipo": "servicio", "servicio": "Transporte Reefer", "capacidad": "Flota 25 camiones", "ubicacion": "Chile"}
        ]
    },
    {
        "slug": "aduanas-max",
        "nombre": "AduanasMax",
        "rol": "Agencia de Aduanas",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "rut": "81.555.444-6",
        "email": "contacto@aduanasmax.cl",
        "telefono": "+56 2 2300 8899",
        "direccion": "Huerfanos 999, Stgo",
        "web": "",
        "breve": "Tramitación aduanera export/import.",
        "items": [
            {"tipo": "servicio", "servicio": "Despacho de exportación", "capacidad": "Alta", "ubicacion": "Santiago"}
        ]
    },
    {
        "slug": "extraport-hub",
        "nombre": "Extraport Hub",
        "rol": "Extraportuario",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "rut": "82.444.222-7",
        "email": "comercial@extraporthub.cl",
        "telefono": "+56 32 223 4455",
        "direccion": "Camino La Pólvora, Valpo",
        "web": "",
        "breve": "Consolidación y servicios extraportuarios.",
        "items": [
            {"tipo": "servicio", "servicio": "Consolidación", "capacidad": "6 andenes", "ubicacion": "Valparaíso"}
        ]
    },
    {
        "slug": "ocexport",
        "nombre": "OCExport",
        "rol": "Exportador",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "rut": "77.666.123-5",
        "email": "buyers@ocexport.cl",
        "telefono": "+56 2 2766 9900",
        "direccion": "El Bosque Norte 123, Las Condes",
        "web": "",
        "breve": "Exportación multiproducto.",
        "items": [
            {"tipo": "demanda", "producto": "Cerezas", "variedad": "Santina/Regina", "calibre": "28+", "cantidad": "150 pallets", "origen": "VI-VII", "precio": "A convenir"},
            {"tipo": "oferta", "producto": "Manzana", "variedad": "Gala", "calibre": "125-138", "cantidad": "50 pallets", "origen": "IX", "precio": "USD"}
        ]
    }
]

# Carrito por sesión (lista de dicts JSON-serializable)
def get_cart():
    return session.setdefault("cart", [])

# ---------------------------
# Middlewares / helpers
# ---------------------------
def is_logged():
    return "usuario" in session

def ensure_login():
    if not is_logged():
        return redirect(url_for("login"))
    return None

# ---------------------------
# Rutas principales
# ---------------------------
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
            error = t("Usuario o clave inválidos.", "Invalid user or password.", "帳號或密碼無效")
    return render_template("login.html", error=error, t=t)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ----- Registro en 2 pasos -----
@app.route("/register_router")
def register_router():
    return render_template("register_router.html", t=t)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    # defaults del select si vienen por querystring
    nacionalidad = request.args.get("nac")  # "nacional" o "extranjero"
    perfil_tipo = request.args.get("tipo")  # "compra_venta" o "servicios"

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
            error = t("Completa los campos obligatorios.", "Please complete required fields.", "請填寫必填欄位")
        elif username in USERS:
            error = t("El usuario ya existe.", "User already exists.", "使用者已存在")
        else:
            USERS[username] = {
                "password": password,
                "rol": rol,
                "perfil_tipo": perfil_tipo,
                "pais": pais or ("CL" if nac == "nacional" else "EX"),
                "rut": rut
            }
            USER_PROFILES[username] = {
                "empresa": username.capitalize(),
                "pais": USERS[username]["pais"],
                "rol": rol,
                "perfil_tipo": perfil_tipo,
                "rut": rut,
                "email": email or f"{username}@mail.com",
                "telefono": telefono or "",
                "direccion": direccion or "",
                "descripcion": "Nuevo perfil.",
                "items": []
            }
            session["usuario"] = username
            return redirect(url_for("dashboard"))

    roles_cv = ROLES_COMPRA_VENTA
    roles_srv = ROLES_SERVICIOS

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
    guard = ensure_login()
    if guard: return guard

    username = session["usuario"]
    user = USERS.get(username)
    if not user: return redirect(url_for("logout"))
    my_company = USER_PROFILES.get(username, {})
    return render_template("dashboard.html",
                           usuario=username,
                           rol=user["rol"],
                           perfil_tipo=user["perfil_tipo"],
                           my_company=my_company,
                           cart=get_cart(),
                           t=t)

# ---------------------------
# Vistas de catálogo (accesos “rápidos” y detalles completos)
# ---------------------------
@app.route("/accesos/<tipo>")
def accesos(tipo):
    # Conservamos esta vista por compatibilidad con lo que tenías
    tipo = tipo.lower()
    if tipo not in ["ventas", "compras", "servicios"]:
        abort(404)

    if tipo == "servicios":
        data = [c for c in COMPANIES if c["perfil_tipo"] == "servicios"]
    else:
        data = [c for c in COMPANIES if c["perfil_tipo"] == "compra_venta"]
    return render_template("accesos.html", tipo=tipo, data=data, t=t)

@app.route("/detalles/<tipo>")
def detalles(tipo):
    """Vistas de detalle por tipo con filtro q y botón Agregar al carrito."""
    tipo = tipo.lower()
    if tipo not in ["ventas", "compras", "servicios"]:
        abort(404)
    q = (request.args.get("q") or "").strip().lower()

    if tipo == "servicios":
        empresas = [c for c in COMPANIES if c["perfil_tipo"] == "servicios"]
        # filtramos por q si corresponde
        if q:
            empresas = [
                dict(c, items=[it for it in c["items"]
                               if (q in it.get("servicio","").lower() or q in it.get("ubicacion","").lower()
                                   or q in c["nombre"].lower())])
                for c in empresas
            ]
            empresas = [c for c in empresas if c["items"]]
        template = "detalle_servicios.html"
    elif tipo == "ventas":
        empresas = [c for c in COMPANIES if c["perfil_tipo"] == "compra_venta"]
        # quedarnos solo con items tipo oferta
        empresas = [dict(c, items=[it for it in c["items"] if it.get("tipo") == "oferta"]) for c in empresas]
        if q:
            empresas = [
                dict(c, items=[it for it in c["items"]
                               if (q in it.get("producto","").lower() or q in it.get("variedad","").lower()
                                   or q in c["nombre"].lower())])
                for c in empresas
            ]
        empresas = [c for c in empresas if c["items"]]
        template = "detalle_ventas.html"
    else:  # compras
        empresas = [c for c in COMPANIES if c["perfil_tipo"] == "compra_venta"]
        empresas = [dict(c, items=[it for it in c["items"] if it.get("tipo") == "demanda"]) for c in empresas]
        if q:
            empresas = [
                dict(c, items=[it for it in c["items"]
                               if (q in it.get("producto","").lower() or q in it.get("variedad","").lower()
                                   or q in c["nombre"].lower())])
                for c in empresas
            ]
        empresas = [c for c in empresas if c["items"]]
        template = "detalle_compras.html"

    return render_template(template, data=empresas, q=q, t=t)

@app.route("/empresa/<slug>")
def empresa(slug):
    # Perfil público de empresa del catálogo
    comp = next((c for c in COMPANIES if c["slug"] == slug), None)
    if not comp:
        # Si corresponde a un usuario real, mostramos su perfil público
        prof = USER_PROFILES.get(slug)
        if not prof:
            abort(404)
        return render_template("empresa.html", comp=prof, es_user=True, t=t)
    return render_template("empresa.html", comp=comp, es_user=False, t=t)

# ---------------------------
# Carrito
# ---------------------------
@app.route("/cart/add", methods=["POST"])
def cart_add():
    item = request.form.to_dict()
    cart = get_cart()
    cart.append(item)
    session["cart"] = cart  # asegurar serializable (lista/dict)
    # Regresamos a donde estaba o al carrito
    return redirect(request.referrer or url_for("carrito"))

@app.route("/carrito")
def carrito():
    return render_template("carrito.html", cart=get_cart(), t=t)

@app.route("/cart/clear", methods=["POST"])
def cart_clear():
    session["cart"] = []
    flash(t("Carrito vaciado.", "Cart cleared.", "購物車已清空"))
    return redirect(url_for("carrito"))

# ---------------------------
# Perfil propio (editar + agregar ítems)
# ---------------------------
@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    guard = ensure_login()
    if guard: return guard

    username = session["usuario"]
    prof = USER_PROFILES.get(username)
    if not prof: abort(404)

    msg = None
    if request.method == "POST":
        action = request.form.get("action")
        if action == "save_profile":
            prof["empresa"] = request.form.get("empresa", prof["empresa"]).strip()
            prof["rut"] = request.form.get("rut", prof["rut"]).strip()
            prof["email"] = request.form.get("email", prof["email"]).strip()
            prof["telefono"] = request.form.get("telefono", prof["telefono"]).strip()
            prof["direccion"] = request.form.get("direccion", prof["direccion"]).strip()
            prof["descripcion"] = request.form.get("descripcion", prof["descripcion"]).strip()
            msg = t("Perfil actualizado.", "Profile updated.", "資料已更新")
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
                    msg = t("Servicio agregado.", "Service added.", "已新增服務")
            else:
                subtipo = request.form.get("subtipo", "oferta")
                producto = request.form.get("producto", "").strip()
                variedad = request.form.get("variedad", "").strip()
                calibre = request.form.get("calibre", "").strip()
                cantidad = request.form.get("cantidad", "").strip()
                origen = request.form.get("origen", "").strip()
                precio = request.form.get("precio", "").strip()
                if producto:
                    prof["items"].append({
                        "tipo": subtipo,
                        "producto": producto,
                        "variedad": variedad,
                        "calibre": calibre,
                        "cantidad": cantidad,
                        "origen": origen,
                        "precio": precio
                    })
                    msg = t("Ítem agregado.", "Item added.", "已新增項目")

    return render_template("perfil.html", perfil=prof, mensaje=msg, t=t)

# ---------------------------
# Centro de ayuda (contacto)
# ---------------------------
@app.route("/ayuda", methods=["GET", "POST"])
def ayuda():
    enviado = None
    if request.method == "POST":
        email = request.form.get("email","").strip()
        asunto = request.form.get("asunto","").strip()
        mensaje = request.form.get("mensaje","").strip()
        lista = session.setdefault("help_msgs", [])
        lista.append({"email": email, "asunto": asunto, "mensaje": mensaje})
        session["help_msgs"] = lista
        enviado = True
        flash(t("Tu solicitud fue enviada. Te contactaremos.", 
                "Your request has been sent. We'll contact you.", 
                "您的請求已送出，我們會儘快聯繫您"))
    return render_template("ayuda.html", enviado=enviado, t=t)

# ---------------------------
# Errores
# ---------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message=t("No encontrado", "Not found", "找不到頁面"), t=t), 404

@app.errorhandler(500)
def server_error(e):
    # Evitamos referencias a endpoints inexistentes
    return render_template("error.html", code=500, message=t("Error interno", "Internal server error", "內部伺服器錯誤"), t=t), 500

# ---------------------------
# Run local
# ---------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
