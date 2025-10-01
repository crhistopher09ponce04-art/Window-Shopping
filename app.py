import os
from flask import Flask, render_template, request, redirect, url_for, session, abort

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")

# ---------------------------
# Idiomas y traducciones
# ---------------------------
SUPPORTED_LANGS = ["es", "en", "zh"]  # zh lo dejamos como alias futuro
DEFAULT_LANG = "es"

def get_lang():
    return session.get("lang", DEFAULT_LANG)

def t(es_text, en_text, zh_text=None):
    lang = get_lang()
    if lang == "en":
        return en_text
    if lang == "zh":
        # placeholder: usamos EN mientras cargamos chino más adelante
        return zh_text or en_text
    return es_text

@app.route("/lang/<lang>")
def set_lang(lang):
    if lang not in SUPPORTED_LANGS:
        lang = DEFAULT_LANG
    session["lang"] = lang
    # vuelve a donde estaba si viene de Referer, si no al home
    return redirect(request.referrer or url_for("home"))

# ---------------------------
# Datos de demo / “DB” en memoria
# ---------------------------
# Roles por tipo
ROLES_COMPRA_VENTA = [
    "Productor", "Planta", "Packing", "Frigorífico", "Exportador", "Cliente extranjero"
]
ROLES_SERVICIOS = [
    "Packing", "Frigorífico", "Transporte", "Agencia de Aduanas", "Extraportuario"
]

# Usuarios de prueba (usuario: info)
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

# Perfiles de empresas/usuarios (datos que se muestran públicamente y que el dueño puede editar)
# clave = username
USER_PROFILES = {
    u: {
        "empresa": u.capitalize(),
        "pais": USERS[u].get("pais", "CL"),
        "rol": USERS[u]["rol"],
        "perfil_tipo": USERS[u]["perfil_tipo"],
        "email": f"{u}@demo.cl",
        "telefono": "+56 9 0000 0000",
        "direccion": "S/N",
        "descripcion": "Perfil demo.",
        # Ítems (para compra/venta: ofertas/demandas; para servicios: servicios ofrecidos)
        "items": []
    } for u in USERS
}

# Unas cuantas empresas de muestra (para “accesos” listados)
COMPANIES = [
    {
        "slug": "agro-andes",
        "nombre": "Agro Andes SPA",
        "rol": "Productor",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "breve": "Uva de mesa y arándanos.",
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
        "breve": "Frío y logística en Valparaíso.",
        "items": [
            {"tipo": "servicio", "servicio": "Almacenaje en frío", "capacidad": "1.200 pallets", "ubicacion": "Valparaíso"},
            {"tipo": "servicio", "servicio": "Preenfriado", "capacidad": "8 túneles", "ubicacion": "Valparaíso"},
        ]
    },
    {
        "slug": "pack-smart",
        "nombre": "PackSmart",
        "rol": "Packing",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "breve": "Servicios de packing fruta fresca.",
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
        "breve": "Exportación multiproducto.",
        "items": [
            {"tipo": "demanda", "producto": "Cerezas", "cantidad": "150 pallets", "origen": "VI-VII", "precio": "A convenir"}
        ]
    }
]

# Carrito (demo, por sesión)
def get_cart():
    return session.setdefault("cart", [])

# ---------------------------
# Middlewares / helpers
# ---------------------------
def login_required():
    if "usuario" not in session:
        return False
    return True

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
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = USERS.get(username)
        if user and user["password"] == password:
            session["usuario"] = username
            return redirect(url_for("dashboard"))
        else:
            error = t("Usuario o clave inválidos.", "Invalid user or password.")
    return render_template("login.html", error=error, t=t)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ----- Registro en 2 pasos: router y formulario -----
@app.route("/register_router")
def register_router():
    # Paso 1: elegir nacional/extranjero
    return render_template("register_router.html", t=t)

@app.route("/register", methods=["GET", "POST"])
def register():
    # Paso 2: formulario según nacionalidad + tipo de perfil (compra_venta / servicios)
    error = None
    lang = get_lang()

    # defaults del select si vienen por querystring
    nacionalidad = request.args.get("nac")  # "nacional" o "extranjero"
    perfil_tipo = request.args.get("tipo")  # "compra_venta" o "servicios"

    # Si POST, procesamos
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
            return redirect(url_for("dashboard"))

    # Rol options según selección
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
    # tipo: "ventas", "compras", "servicios"
    tipo = tipo.lower()
    if tipo not in ["ventas", "compras", "servicios"]:
        abort(404)

    # Filtro de demo: listamos empresas según tipo
    if tipo == "servicios":
        data = [c for c in COMPANIES if c["perfil_tipo"] == "servicios"]
    else:
        # ventas/compras: usamos compra_venta
        data = [c for c in COMPANIES if c["perfil_tipo"] == "compra_venta"]

    return render_template("accesos.html", tipo=tipo, data=data, t=t)

@app.route("/empresa/<slug>")
def empresa(slug):
    # Perfil público de empresa
    comp = next((c for c in COMPANIES if c["slug"] == slug), None)
    if not comp:
        # Si es usuario real, mostramos su perfil público también
        prof = USER_PROFILES.get(slug)
        if not prof:
            abort(404)
        return render_template("empresa.html", comp=prof, es_user=True, t=t)
    return render_template("empresa.html", comp=comp, es_user=False, t=t)

@app.route("/cart/add", methods=["POST"])
def cart_add():
    item = request.form.to_dict()
    cart = get_cart()
    cart.append(item)
    session["cart"] = cart
    return redirect(request.referrer or url_for("dashboard"))

@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    if not login_required():
        return redirect(url_for("login"))
    username = session["usuario"]
    prof = USER_PROFILES.get(username)
    if not prof:
        abort(404)

    msg = None
    if request.method == "POST":
        action = request.form.get("action")
        if action == "save_profile":
            prof["empresa"] = request.form.get("empresa", prof["empresa"]).strip()
            prof["email"] = request.form.get("email", prof["email"]).strip()
            prof["telefono"] = request.form.get("telefono", prof["telefono"]).strip()
            prof["direccion"] = request.form.get("direccion", prof["direccion"]).strip()
            prof["descripcion"] = request.form.get("descripcion", prof["descripcion"]).strip()
            msg = t("Perfil actualizado.", "Profile updated.")
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
                    msg = t("Servicio agregado.", "Service added.")
            else:
                subtipo = request.form.get("subtipo", "oferta")
                producto = request.form.get("producto", "").strip()
                cantidad = request.form.get("cantidad", "").strip()
                origen = request.form.get("origen", "").strip()
                precio = request.form.get("precio", "").strip()
                if producto:
                    prof["items"].append({
                        "tipo": subtipo,
                        "producto": producto,
                        "cantidad": cantidad,
                        "origen": origen,
                        "precio": precio
                    })
                    msg = t("Ítem agregado.", "Item added.")

    return render_template("perfil.html", perfil=prof, mensaje=msg, t=t)

# ---------------------------
# Errores
# ---------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message=t("No encontrado", "Not found"), t=t), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message=t("Error interno", "Internal server error"), t=t), 500

# ---------------------------
# Run local
# ---------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
