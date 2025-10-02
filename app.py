import os
from flask import Flask, render_template, request, redirect, url_for, session, abort

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
# Datos de demo
# ---------------------------
ROLES_COMPRA_VENTA = ["Productor", "Planta", "Packing", "Frigorífico", "Exportador", "Cliente extranjero"]
ROLES_SERVICIOS = ["Packing", "Frigorífico", "Transporte", "Agencia de Aduanas", "Extraportuario"]

USERS = {
    "exportador1": {"password": "1234", "rol": "Exportador", "perfil_tipo": "compra_venta", "pais": "CL"},
    "cliente1": {"password": "1234", "rol": "Cliente extranjero", "perfil_tipo": "compra_venta", "pais": "US"},
    "packing1": {"password": "1234", "rol": "Packing", "perfil_tipo": "servicios", "pais": "CL"},
    "frigorifico1": {"password": "1234", "rol": "Frigorífico", "perfil_tipo": "servicios", "pais": "CL"},
    "transporte1": {"password": "1234", "rol": "Transporte", "perfil_tipo": "servicios", "pais": "CL"},
    "aduana1": {"password": "1234", "rol": "Agencia de Aduanas", "perfil_tipo": "servicios", "pais": "CL"},
}

USER_PROFILES = {
    u: {
        "empresa": u.capitalize(),
        "pais": USERS[u].get("pais", "CL"),
        "rol": USERS[u]["rol"],
        "perfil_tipo": USERS[u]["perfil_tipo"],
        "email": f"{u}@demo.cl",
        "telefono": "+56 9 1111 1111",
        "direccion": "Calle Falsa 123",
        "rut": "76.543.210-K",
        "descripcion": "Perfil demo de empresa.",
        "items": []
    } for u in USERS
}

COMPANIES = [
    {
        "slug": "frutal-sur",
        "nombre": "Frutal Sur Ltda.",
        "rol": "Productor",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "rut": "96.111.222-3",
        "breve": "Productores de cerezas y ciruelas frescas.",
        "items": [
            {"tipo": "oferta", "producto": "Cerezas Lapins", "cantidad": "120 pallets", "origen": "VI Región", "precio": "A convenir"},
            {"tipo": "oferta", "producto": "Ciruelas D’Agen", "cantidad": "80 pallets", "origen": "VII Región", "precio": "A convenir"},
        ]
    },
    {
        "slug": "friopoint",
        "nombre": "FríoPoint SPA",
        "rol": "Frigorífico",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "rut": "77.222.333-4",
        "breve": "Servicios de almacenaje en frío.",
        "items": [
            {"tipo": "servicio", "servicio": "Almacenaje en frío", "capacidad": "1500 pallets", "ubicacion": "Valparaíso"},
            {"tipo": "servicio", "servicio": "Preenfriado", "capacidad": "10 túneles", "ubicacion": "Valparaíso"},
        ]
    }
]

def get_cart():
    return session.setdefault("cart", [])

def login_required():
    return "usuario" in session

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
            error = t("Usuario o clave inválidos.", "Invalid user or password.")
    return render_template("login.html", error=error, t=t)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/register_router")
def register_router():
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
        pais = request.form.get("pais", "CL").strip()
        rol = request.form.get("rol", "").strip()
        rut = request.form.get("rut", "").strip()
        perfil_tipo = request.form.get("perfil_tipo", "").strip()

        if not username or not password or not rol or not perfil_tipo:
            error = t("Completa los campos obligatorios.", "Please complete required fields.")
        elif username in USERS:
            error = t("El usuario ya existe.", "User already exists.")
        else:
            USERS[username] = {"password": password, "rol": rol, "perfil_tipo": perfil_tipo, "pais": pais}
            USER_PROFILES[username] = {
                "empresa": username.capitalize(),
                "pais": pais,
                "rol": rol,
                "perfil_tipo": perfil_tipo,
                "email": email or f"{username}@mail.com",
                "telefono": telefono,
                "direccion": direccion,
                "rut": rut or "11.111.111-1",
                "descripcion": "Nuevo perfil.",
                "items": []
            }
            session["usuario"] = username
            return redirect(url_for("dashboard"))

    return render_template("register.html", error=error, nacionalidad=nacionalidad, perfil_tipo=perfil_tipo,
                           roles_cv=ROLES_COMPRA_VENTA, roles_srv=ROLES_SERVICIOS, t=t)

@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect(url_for("login"))
    username = session["usuario"]
    user = USERS.get(username)
    my_company = USER_PROFILES.get(username, {})
    return render_template("dashboard.html", usuario=username, rol=user["rol"], perfil_tipo=user["perfil_tipo"],
                           my_company=my_company, cart=get_cart(), t=t)

# ---------------------------
# Vistas de detalle
# ---------------------------
@app.route("/detalles/<tipo>")
def detalles(tipo):
    tipo = tipo.lower()
    if tipo == "ventas":
        data = [c for c in COMPANIES if c["perfil_tipo"] == "compra_venta"]
        return render_template("detalle_ventas.html", data=data, t=t)
    elif tipo == "compras":
        data = [c for c in COMPANIES if c["perfil_tipo"] == "compra_venta"]
        return render_template("detalle_compras.html", data=data, t=t)
    elif tipo == "servicios":
        data = [c for c in COMPANIES if c["perfil_tipo"] == "servicios"]
        return render_template("detalle_servicios.html", data=data, t=t)
    else:
        abort(404)

@app.route("/empresa/<slug>")
def empresa(slug):
    comp = next((c for c in COMPANIES if c["slug"] == slug), None)
    if not comp:
        prof = USER_PROFILES.get(slug)
        if not prof:
            abort(404)
        return render_template("empresa.html", comp=prof, es_user=True, t=t)
    return render_template("empresa.html", comp=comp, es_user=False, t=t)

# ---------------------------
# Carrito y ayuda
# ---------------------------
@app.route("/cart/add", methods=["POST"])
def cart_add():
    item = request.form.to_dict()
    cart = get_cart()
    cart.append(item)
    session["cart"] = cart
    return redirect(request.referrer or url_for("dashboard"))

@app.route("/carrito")
def carrito():
    return render_template("carrito.html", cart=get_cart(), t=t)

@app.route("/ayuda", methods=["GET", "POST"])
def ayuda():
    msg = None
    if request.method == "POST":
        correo = request.form.get("correo")
        mensaje = request.form.get("mensaje")
        msg = f"✅ Mensaje enviado. Te contactaremos a {correo}"
    return render_template("ayuda.html", mensaje=msg, t=t)

# ---------------------------
# Errores corregidos
# ---------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="Página no encontrada"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message="Error interno"), 500

# ---------------------------
# Run local
# ---------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
