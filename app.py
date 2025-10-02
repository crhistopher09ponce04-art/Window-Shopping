import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")

# ---------------------------
# Traducción simple (ES, EN, ZH)
# ---------------------------
def t(es, en, zh=None):
    lang = session.get("lang", "es")
    if lang == "en":
        return en
    if lang == "zh" and zh:
        return zh
    return es

# ---------------------------
# Datos base (usuarios demo + perfiles demo + empresas demo)
# ---------------------------
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
}

# Perfiles públicos (por usuario)
USER_PROFILES = {
    "productor1": {
        "empresa": "AgroCampo Ltda.",
        "rut": "76.111.222-3",
        "rol": "Productor",
        "pais": "CL",
        "email": "ventas@agrocampo.cl",
        "telefono": "+56 9 1111 1111",
        "direccion": "Ruta 5 Sur km 320, Talca",
        "descripcion": "Productores de uva, cereza y ciruela.",
        "perfil_tipo": "compra_venta",
        "items": [
            {"tipo": "oferta", "producto": "Uva Crimson",       "cantidad": "120 pallets", "origen": "Talca",   "precio": "USD 2.1/kg"},
            {"tipo": "oferta", "producto": "Ciruelas D'Agen",   "cantidad": "80 pallets",  "origen": "Curicó",  "precio": "USD 1.5/kg"},
        ],
    },
    "planta1": {
        "empresa": "Planta Andina",
        "rut": "76.234.567-8",
        "rol": "Planta",
        "pais": "CL",
        "email": "contacto@plantaandina.cl",
        "telefono": "+56 9 7777 1111",
        "direccion": "Los Andes",
        "descripcion": "Planta de proceso multiproducto.",
        "perfil_tipo": "compra_venta",
        "items": [
            {"tipo": "oferta", "producto": "Uva Thompson", "cantidad": "60 pallets", "origen": "Los Andes", "precio": "USD 1.9/kg"},
        ],
    },
    "exportador1": {
        "empresa": "ExportFruit SPA",
        "rut": "79.888.999-0",
        "rol": "Exportador",
        "pais": "CL",
        "email": "export@exportfruit.cl",
        "telefono": "+56 9 4444 4444",
        "direccion": "Av. Apoquindo 1234, Santiago",
        "descripcion": "Exportadores con foco en Asia y Europa.",
        "perfil_tipo": "compra_venta",
        "items": [
            {"tipo": "demanda", "producto": "Cerezas", "cantidad": "200 pallets", "origen": "Santiago", "precio": "A convenir"},
        ],
    },
    "cliente1": {
        "empresa": "GlobalBuyer Co.",
        "rut": None,
        "rol": "Cliente extranjero",
        "pais": "US",
        "email": "contact@globalbuyer.com",
        "telefono": "+1 555 111 222",
        "direccion": "Miami, USA",
        "descripcion": "Importadores mayoristas de fruta fresca.",
        "perfil_tipo": "compra_venta",
        "items": [
            {"tipo": "demanda", "producto": "Uva Thompson", "cantidad": "400 pallets", "origen": "USA", "precio": "A convenir"},
        ],
    },
    "packing1": {
        "empresa": "PackCenter SPA",
        "rut": "77.333.444-5",
        "rol": "Packing",
        "pais": "CL",
        "email": "info@packcenter.cl",
        "telefono": "+56 9 2222 2222",
        "direccion": "Parque Industrial, Rancagua",
        "descripcion": "Servicios de embalaje, etiquetado y control de calidad.",
        "perfil_tipo": "servicios",
        "items": [
            {"tipo": "servicio", "servicio": "Packing de fruta fresca", "capacidad": "30.000 cajas/día", "ubicacion": "Rancagua"},
        ],
    },
    "frigorifico1": {
        "empresa": "FrioMax Ltda.",
        "rut": "78.555.666-7",
        "rol": "Frigorífico",
        "pais": "CL",
        "email": "contacto@friomax.cl",
        "telefono": "+56 9 3333 3333",
        "direccion": "Puerto San Antonio",
        "descripcion": "Almacenaje en frío, preenfriado y logística.",
        "perfil_tipo": "servicios",
        "items": [
            {"tipo": "servicio", "servicio": "Almacenaje en frío", "capacidad": "2000 pallets", "ubicacion": "San Antonio"},
            {"tipo": "servicio", "servicio": "Preenfriado",        "capacidad": "10 túneles",  "ubicacion": "San Antonio"},
        ],
    },
    "transporte1": {
        "empresa": "TransDemo",
        "rut": "76.987.654-3",
        "rol": "Transporte",
        "pais": "CL",
        "email": "contacto@transdemo.cl",
        "telefono": "+56 9 5555 6666",
        "direccion": "Talagante",
        "descripcion": "Transporte refrigerado nacional.",
        "perfil_tipo": "servicios",
        "items": [
            {"tipo": "servicio", "servicio": "Transporte refrigerado", "capacidad": "Flota 25 camiones", "ubicacion": "RM"},
        ],
    },
    "aduana1": {
        "empresa": "AduanasPro",
        "rut": "78.321.654-9",
        "rol": "Agencia de Aduanas",
        "pais": "CL",
        "email": "contacto@aduanaspro.cl",
        "telefono": "+56 2 2222 3333",
        "direccion": "Valparaíso",
        "descripcion": "Tramitación aduanera y asesoría.",
        "perfil_tipo": "servicios",
        "items": [
            {"tipo": "servicio", "servicio": "Agenciamiento de exportación", "capacidad": "Alta", "ubicacion": "V Región"},
        ],
    },
    "extraportuario1": {
        "empresa": "ExtraPort",
        "rut": "77.112.223-4",
        "rol": "Extraportuario",
        "pais": "CL",
        "email": "contacto@export.cl",
        "telefono": "+56 32 333 4444",
        "direccion": "San Antonio",
        "descripcion": "Servicios extraportuarios y consolidación.",
        "perfil_tipo": "servicios",
        "items": [
            {"tipo": "servicio", "servicio": "Consolidación", "capacidad": "8 andenes", "ubicacion": "San Antonio"},
        ],
    },
}

# Empresas de muestra con slug (para vistas que usan c.slug / c.nombre / c.items)
COMPANIES = [
    {
        "slug": "agro-andes",
        "nombre": "Agro Andes SPA",
        "rol": "Productor",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "breve": "Uva de mesa y arándanos.",
        "rut": "76.100.200-1",
        "email": "contacto@agroandes.cl",
        "telefono": "+56 9 7000 1111",
        "items": [
            {"tipo": "oferta",  "producto": "Uva Crimson",  "cantidad": "80 pallets",  "origen": "IV Región", "precio": "A convenir"},
            {"tipo": "demanda", "producto": "Cajas plásticas", "cantidad": "15.000 und","origen": "CL",        "precio": "Oferta"},
        ],
    },
    {
        "slug": "friopoint",
        "nombre": "FríoPoint Ltda.",
        "rol": "Frigorífico",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "breve": "Frío y logística en Valparaíso.",
        "rut": "77.300.400-2",
        "email": "info@friopoint.cl",
        "telefono": "+56 32 222 0000",
        "items": [
            {"tipo": "servicio", "servicio": "Almacenaje en frío", "capacidad": "1.200 pallets", "ubicacion": "Valparaíso"},
            {"tipo": "servicio", "servicio": "Preenfriado",        "capacidad": "8 túneles",     "ubicacion": "Valparaíso"},
        ],
    },
    {
        "slug": "pack-smart",
        "nombre": "PackSmart",
        "rol": "Packing",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "breve": "Servicios de packing fruta fresca.",
        "rut": "79.123.456-7",
        "email": "contacto@packsmart.cl",
        "telefono": "+56 72 222 3333",
        "items": [
            {"tipo": "servicio", "servicio": "Embalaje exportación", "capacidad": "30.000 cajas/día", "ubicacion": "R.M."},
        ],
    },
    {
        "slug": "ocexport",
        "nombre": "OCExport",
        "rol": "Exportador",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "breve": "Exportación multiproducto.",
        "rut": "76.555.444-3",
        "email": "ventas@ocexport.cl",
        "telefono": "+56 2 2345 6789",
        "items": [
            {"tipo": "demanda", "producto": "Cerezas", "cantidad": "150 pallets", "origen": "VI-VII", "precio": "A convenir"},
        ],
    },
]

# ---------------------------
# Carrito (sesión)
# ---------------------------
def get_cart():
    return session.setdefault("cart", [])

def add_to_cart(item):
    cart = get_cart()
    cart.append(item)
    session["cart"] = cart

# ---------------------------
# Rutas
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
    error = None
    if request.method == "POST":
        user = request.form.get("username", "").strip()
        pwd  = request.form.get("password", "").strip()
        if user in USERS and USERS[user]["password"] == pwd:
            # Guardamos dos claves por compatibilidad con tus templates
            session["user"] = user
            session["usuario"] = user
            return redirect(url_for("dashboard"))
        error = t("Credenciales inválidas", "Invalid credentials")
    return render_template("login.html", error=error, t=t)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/register_router")
def register_router():
    # Pantalla de elección (nacional / extranjero) y link a /register
    return render_template("register_router.html", t=t)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    nacionalidad = request.args.get("nac")   # 'nacional' | 'extranjero'
    perfil_tipo  = request.args.get("tipo")  # 'compra_venta' | 'servicios'
    roles_cv = ["Productor", "Planta", "Packing", "Frigorífico", "Exportador", "Cliente extranjero"]
    roles_srv = ["Packing", "Frigorífico", "Transporte", "Agencia de Aduanas", "Extraportuario"]

    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()
        email    = request.form.get("email","").strip()
        telefono = request.form.get("phone","").strip()
        direccion= request.form.get("address","").strip()
        rut      = request.form.get("rut","").strip()
        pais     = request.form.get("pais","CL").strip()
        rol      = request.form.get("rol","").strip()
        perfil_tipo = request.form.get("perfil_tipo","").strip()
        nac      = request.form.get("nacionalidad","").strip()

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
                "pais": USERS[username]["pais"],
                "email": email or f"{username}@mail.com",
                "telefono": telefono or "",
                "direccion": direccion or "",
                "descripcion": "Nuevo perfil.",
                "perfil_tipo": perfil_tipo,
                "items": [],
            }
            session["user"] = username
            session["usuario"] = username
            return redirect(url_for("dashboard"))

    return render_template(
        "register.html",
        error=error,
        nacionalidad=nacionalidad,
        perfil_tipo=perfil_tipo,
        roles_cv=roles_cv,
        roles_srv=roles_srv,
        t=t,
    )

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    u = session["user"]
    user = USERS.get(u, {})
    my_company = USER_PROFILES.get(u, {})
    return render_template(
        "dashboard.html",
        usuario=u,
        rol=user.get("rol"),
        perfil_tipo=user.get("perfil_tipo"),
        my_company=my_company,
        cart=get_cart(),
        t=t,
    )

# Perfil público por SLUG (para templates que usan url_for('empresa', slug=c.slug))
@app.route("/empresa/<slug>")
def empresa(slug):
    comp = next((c for c in COMPANIES if c["slug"] == slug), None)
    if not comp:
        # fallback: si el slug coincide con un username, mostramos su perfil
        prof = USER_PROFILES.get(slug)
        if not prof:
            abort(404)
        return render_template("empresa.html", comp=prof, es_user=True, t=t)
    return render_template("empresa.html", comp=comp, es_user=False, t=t)

# Perfil del usuario logueado (para url_for('perfil'))
@app.route("/perfil")
def perfil():
    if "user" not in session:
        return redirect(url_for("login"))
    u = session["user"]
    profile = USER_PROFILES.get(u)
    if not profile:
        abort(404)
    return render_template("perfil.html", perfil=profile, t=t)

# Listado de accesos (opcional, por si tus templates lo usan)
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

# Vistas de detalle (ventas/compras/servicios) compatibles con tus detalle_*.html
@app.route("/detalles/<tipo>")
def detalles(tipo):
    tipo = tipo.lower()
    if tipo not in ["ventas", "compras", "servicios"]:
        abort(404)

    if tipo == "servicios":
        data = [c for c in COMPANIES if c["perfil_tipo"] == "servicios"]
    else:
        data = [c for c in COMPANIES if c["perfil_tipo"] == "compra_venta"]

    # Tus plantillas filtran por it.tipo == "oferta"/"demanda" internamente.
    return render_template(f"detalle_{tipo}.html", data=data, t=t)

# Carrito + agregar al carrito (versiones usadas por tus templates)
@app.route("/carrito")
def carrito():
    return render_template("carrito.html", cart=get_cart(), t=t)

@app.route("/cart/add", methods=["POST"])
def cart_add():
    item = request.form.to_dict()
    cart = get_cart()
    cart.append(item)
    session["cart"] = cart
    # Volvemos a la página anterior o al carrito
    return redirect(request.referrer or url_for("carrito"))

# Ruta auxiliar por si usas add_to_cart con índice
@app.route("/add_to_cart/<user>/<int:item_id>")
def add_item(user, item_id):
    profile = USER_PROFILES.get(user)
    if not profile:
        return redirect(url_for("dashboard"))
    if 0 <= item_id < len(profile["items"]):
        item = dict(profile["items"][item_id])
        item["empresa"] = profile.get("empresa", user)
        add_to_cart(item)
    return redirect(url_for("carrito"))

# Ayuda / contacto sencillo
@app.route("/ayuda", methods=["GET", "POST"])
def ayuda():
    if request.method == "POST":
        correo = request.form.get("correo")
        mensaje = request.form.get("mensaje")
        flash(t("Tu solicitud fue enviada.", "Your request was sent.", "已送出您的請求"))
    return render_template("ayuda.html", t=t)

# ---------------------------
# Errores
# ---------------------------
@app.errorhandler(HTTPException)
def handle_http(e):
    # Usamos un template simple que NO extiende base.html para evitar errores en cascada
    return render_template("error.html", code=e.code, message=e.description), e.code

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message=t("Error interno", "Internal server error", "內部伺服器錯誤")), 500

# ---------------------------
# Run local
# ---------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
