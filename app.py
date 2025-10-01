import os
from flask import Flask, render_template, request, redirect, url_for, session, abort

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")

# ---------------------------
# Idiomas y traducciones
# ---------------------------
SUPPORTED_LANGS = ["es", "en", "zh"]  # zh activado (textos base incluidos)
DEFAULT_LANG = "es"

def get_lang():
    return session.get("lang", DEFAULT_LANG)

def t(es_text, en_text, zh_text=None):
    """Traductor simple: ES / EN / ZH (si no hay ZH, cae a EN)."""
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

# ---- Helper para chequear endpoints desde Jinja ----
@app.context_processor
def inject_helpers():
    def has_endpoint(name: str) -> bool:
        return name in app.view_functions
    return dict(t=t, has_endpoint=has_endpoint)

# ---------------------------
# Datos demo en memoria
# ---------------------------
ROLES_COMPRA_VENTA = [
    "Productor", "Planta", "Packing", "Frigorífico", "Exportador", "Cliente extranjero"
]
ROLES_SERVICIOS = [
    "Packing", "Frigorífico", "Transporte", "Agencia de Aduanas", "Extraportuario"
]

USERS = {
    # Compra/Venta
    "productor1": {"password": "1234", "rol": "Productor", "perfil_tipo": "compra_venta", "pais": "CL"},
    "planta1": {"password": "1234", "rol": "Planta", "perfil_tipo": "compra_venta", "pais": "CL"},
    "packing1": {"password": "1234", "rol": "Packing", "perfil_tipo": "compra_venta", "pais": "CL"},
    "frigorifico1": {"password": "1234", "rol": "Frigorífico", "perfil_tipo": "compra_venta", "pais": "CL"},
    "exportador1": {"password": "1234", "rol": "Exportador", "perfil_tipo": "compra_venta", "pais": "CL"},
    "cliente1": {"password": "1234", "rol": "Cliente extranjero", "perfil_tipo": "compra_venta", "pais": "US"},
    # Servicios
    "transporte1": {"password": "1234", "rol": "Transporte", "perfil_tipo": "servicios", "pais": "CL"},
    "aduana1": {"password": "1234", "rol": "Agencia de Aduanas", "perfil_tipo": "servicios", "pais": "CL"},
    "extraportuario1": {"password": "1234", "rol": "Extraportuario", "perfil_tipo": "servicios", "pais": "CL"},
}

USER_PROFILES = {
    u: {
        "slug": u,
        "nombre": u.capitalize(),
        "rol": USERS[u]["rol"],
        "perfil_tipo": USERS[u]["perfil_tipo"],
        "pais": USERS[u]["pais"],
        "descripcion": "Perfil demo.",
        "email": f"{u}@demo.cl",
        "telefono": "+56 9 0000 0000",
        "direccion": "S/N",
        "items": []
    } for u in USERS
}

COMPANIES = [
    {
        "slug": "agro-andes",
        "nombre": "Agro Andes SPA",
        "rol": "Productor",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "descripcion": "Uva de mesa y arándanos.",
        "items": [
            {"tipo": "oferta", "producto": "Uva Crimson", "cantidad": "80 pallets", "origen": "IV Región", "precio": "A convenir"},
            {"tipo": "demanda", "producto": "Cajas plásticas", "cantidad": "15.000 und", "origen": "CL", "precio": "Oferta"}
        ]
    },
    {
        "slug": "friopoint",
        "nombre": "FríoPoint Ltda.",
        "rol": "Frigorífico",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "descripcion": "Frío y logística en Valparaíso.",
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
        "descripcion": "Servicios de packing fruta fresca.",
        "items": [
            {"tipo": "servicio", "servicio": "Embalaje exportación", "capacidad": "30.000 cajas/día", "ubicacion": "R.M."}
        ]
    },
    {
        "slug": "ocexport",
        "nombre": "OCExport",
        "rol": "Exportador",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "descripcion": "Exportación multiproducto.",
        "items": [
            {"tipo": "demanda", "producto": "Cerezas", "cantidad": "150 pallets", "origen": "VI-VII", "precio": "A convenir"}
        ]
    }
]

def get_cart():
    return session.setdefault("cart", [])

def login_required():
    return "usuario" in session

# ---------------------------
# Rutas
# ---------------------------
@app.route("/")
def home():
    return render_template("landing.html")

@app.route("/login", methods=["GET","POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form.get("username","").strip()
        p = request.form.get("password","").strip()
        if u in USERS and USERS[u]["password"] == p:
            session["usuario"] = u
            return redirect(url_for("dashboard"))
        error = t("Usuario o clave inválidos.", "Invalid user or password.", "用戶或密碼錯誤")
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ----- Registro en 2 pasos -----
@app.route("/register_router")
def register_router():
    return render_template("register_router.html")

@app.route("/register", methods=["GET","POST"])
def register():
    error = None
    nacionalidad = request.args.get("nac")     # nacional / extranjero
    perfil_tipo_q = request.args.get("tipo")   # compra_venta / servicios

    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()
        email = request.form.get("email","").strip()
        telefono = request.form.get("phone","").strip()
        direccion = request.form.get("address","").strip()
        pais = request.form.get("pais","CL").strip()
        rol = request.form.get("rol","").strip()
        perfil_tipo = request.form.get("perfil_tipo","").strip()
        nac = request.form.get("nacionalidad","").strip()

        if not username or not password or not rol or not perfil_tipo or not nac:
            error = t("Completa los campos obligatorios.", "Please complete required fields.", "請完成必填欄位")
        elif username in USERS:
            error = t("El usuario ya existe.", "User already exists.", "使用者已存在")
        else:
            USERS[username] = {
                "password": password,
                "rol": rol,
                "perfil_tipo": perfil_tipo,
                "pais": pais or ("CL" if nac == "nacional" else "EX")
            }
            USER_PROFILES[username] = {
                "slug": username,
                "nombre": username.capitalize(),
                "rol": rol,
                "perfil_tipo": perfil_tipo,
                "pais": USERS[username]["pais"],
                "descripcion": "Perfil registrado.",
                "email": email,
                "telefono": telefono,
                "direccion": direccion,
                "items": []
            }
            session["usuario"] = username
            return redirect(url_for("dashboard"))

    return render_template(
        "register.html",
        error=error,
        nacionalidad=nacionalidad,
        perfil_tipo=perfil_tipo_q,
        roles_cv=ROLES_COMPRA_VENTA,
        roles_srv=ROLES_SERVICIOS
    )

@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect(url_for("login"))
    u = session["usuario"]
    prof = USER_PROFILES.get(u)
    return render_template(
        "dashboard.html",
        usuario=u,
        rol=prof["rol"],
        perfil_tipo=prof["perfil_tipo"],
        my_company=prof,
        cart=get_cart()
    )

@app.route("/accesos/<tipo>")
def accesos(tipo):
    tipo = tipo.lower()
    if tipo not in ["ventas", "compras", "servicios"]:
        abort(404)
    all_data = COMPANIES + list(USER_PROFILES.values())
    if tipo == "servicios":
        data = [c for c in all_data if c["perfil_tipo"] == "servicios"]
    else:
        data = [c for c in all_data if c["perfil_tipo"] == "compra_venta"]
    return render_template("accesos.html", tipo=tipo, data=data)

@app.route("/empresa/<slug>")
def empresa(slug):
    comp = next((c for c in COMPANIES if c["slug"] == slug), None)
    if not comp:
        comp = USER_PROFILES.get(slug)
    if not comp:
        abort(404)
    return render_template("empresa.html", comp=comp)

# ---- PERFIL (crítica para el navbar) ----
@app.route("/perfil", methods=["GET","POST"])
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
            prof["nombre"] = request.form.get("empresa", prof.get("nombre","")).strip() or prof.get("nombre","")
            prof["email"] = request.form.get("email", prof.get("email","")).strip()
            prof["telefono"] = request.form.get("telefono", prof.get("telefono","")).strip()
            prof["direccion"] = request.form.get("direccion", prof.get("direccion","")).strip()
            prof["descripcion"] = request.form.get("descripcion", prof.get("descripcion","")).strip()
            mensaje = t("Perfil actualizado.", "Profile updated.", "資料已更新")
        elif action == "add_item":
            if prof["perfil_tipo"] == "servicios":
                servicio = request.form.get("servicio","").strip()
                capacidad = request.form.get("capacidad","").strip()
                ubicacion = request.form.get("ubicacion","").strip()
                if servicio:
                    prof["items"].append({
                        "tipo": "servicio",
                        "servicio": servicio,
                        "capacidad": capacidad,
                        "ubicacion": ubicacion
                    })
                    mensaje = t("Servicio agregado.", "Service added.", "已新增服務")
            else:
                subtipo = request.form.get("subtipo","oferta")
                producto = request.form.get("producto","").strip()
                cantidad = request.form.get("cantidad","").strip()
                origen = request.form.get("origen","").strip()
                precio = request.form.get("precio","").strip()
                if producto:
                    prof["items"].append({
                        "tipo": subtipo,
                        "producto": producto,
                        "cantidad": cantidad,
                        "origen": origen,
                        "precio": precio
                    })
                    mensaje = t("Ítem agregado.", "Item added.", "已新增項目")

    return render_template("perfil.html", perfil=prof, mensaje=mensaje)

@app.route("/cart/add", methods=["POST"])
def cart_add():
    cart = get_cart()
    item = {k: v for k, v in request.form.items()}
    cart.append(item)
    session["cart"] = cart
    return redirect(request.referrer or url_for("dashboard"))

# ---------------------------
# Errores (páginas autónomas)
# ---------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message=t("No encontrado","Not found","未找到")), 404

@app.errorhandler(500)
def server_error(e):
    # OJO: esta página no extiende base.html para evitar loops
    return render_template("error.html", code=500, message=t("Error interno","Internal error","內部錯誤")), 500

# ---------------------------
# Run
# ---------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
