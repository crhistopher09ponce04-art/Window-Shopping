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
# Datos de prueba
# ---------------------------
ROLES_COMPRA_VENTA = ["Productor", "Planta", "Packing", "Frigorífico", "Exportador", "Cliente extranjero"]
ROLES_SERVICIOS = ["Packing", "Frigorífico", "Transporte", "Agencia de Aduanas", "Extraportuario"]

USERS = {
    "productor1": {"password": "1234", "rol": "Productor", "perfil_tipo": "compra_venta", "pais": "CL"},
    "packing1": {"password": "1234", "rol": "Packing", "perfil_tipo": "servicios", "pais": "CL"},
    "frigorifico1": {"password": "1234", "rol": "Frigorífico", "perfil_tipo": "servicios", "pais": "CL"},
    "exportador1": {"password": "1234", "rol": "Exportador", "perfil_tipo": "compra_venta", "pais": "CL"},
    "cliente1": {"password": "1234", "rol": "Cliente extranjero", "perfil_tipo": "compra_venta", "pais": "CN"},
    "transporte1": {"password": "1234", "rol": "Transporte", "perfil_tipo": "servicios", "pais": "CL"},
    "aduana1": {"password": "1234", "rol": "Agencia de Aduanas", "perfil_tipo": "servicios", "pais": "CL"},
    "extraportuario1": {"password": "1234", "rol": "Extraportuario", "perfil_tipo": "servicios", "pais": "CL"},
}

USER_PROFILES = {
    u: {
        "empresa": u.capitalize(),
        "pais": USERS[u]["pais"],
        "rol": USERS[u]["rol"],
        "perfil_tipo": USERS[u]["perfil_tipo"],
        "email": f"{u}@demo.com",
        "telefono": "+56 9 0000 0000",
        "direccion": "S/N",
        "rut": "76.123.456-7",
        "descripcion": "Perfil de demostración",
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
            {"tipo": "servicio", "servicio": "Almacenaje en frío", "capacidad": "1200 pallets", "ubicacion": "Valparaíso"},
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
    }
]

# Carrito en sesión
def get_cart():
    return session.setdefault("cart", [])

# ---------------------------
# Rutas
# ---------------------------
@app.route("/")
def home():
    return render_template("landing.html", t=t)

@app.route("/login", methods=["GET","POST"])
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
            error = t("Usuario o clave inválidos.","Invalid username or password.","用户名或密码错误")
    return render_template("login.html", error=error, t=t)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/register_router")
def register_router():
    return render_template("register_router.html", t=t)

@app.route("/register", methods=["GET","POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        rol = request.form.get("rol")
        perfil_tipo = request.form.get("perfil_tipo")
        pais = request.form.get("pais","CL")
        email = request.form.get("email")
        telefono = request.form.get("phone")
        direccion = request.form.get("address")
        rut = request.form.get("rut")

        if username in USERS:
            error = t("Usuario ya existe","User already exists","用户已存在")
        else:
            USERS[username] = {"password": password, "rol": rol, "perfil_tipo": perfil_tipo, "pais": pais}
            USER_PROFILES[username] = {
                "empresa": username.capitalize(),
                "pais": pais,
                "rol": rol,
                "perfil_tipo": perfil_tipo,
                "email": email,
                "telefono": telefono,
                "direccion": direccion,
                "rut": rut,
                "descripcion": "Perfil nuevo",
                "items": []
            }
            session["usuario"] = username
            return redirect(url_for("dashboard"))

    return render_template("register.html", error=error, roles_cv=ROLES_COMPRA_VENTA, roles_srv=ROLES_SERVICIOS, t=t)

@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))
    username = session["usuario"]
    my_company = USER_PROFILES[username]
    return render_template("dashboard.html", usuario=username, rol=my_company["rol"], perfil_tipo=my_company["perfil_tipo"], my_company=my_company, cart=get_cart(), t=t)

@app.route("/accesos/<tipo>")
def accesos(tipo):
    tipo = tipo.lower()
    if tipo == "servicios":
        data = [c for c in COMPANIES if c["perfil_tipo"]=="servicios"]
    else:
        data = [c for c in COMPANIES if c["perfil_tipo"]=="compra_venta"]
    return render_template("accesos.html", tipo=tipo, data=data, t=t)

@app.route("/empresa/<slug>")
def empresa(slug):
    comp = next((c for c in COMPANIES if c["slug"]==slug), None)
    if not comp:
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

@app.route("/perfil", methods=["GET","POST"])
def perfil():
    if "usuario" not in session:
        return redirect(url_for("login"))
    username = session["usuario"]
    prof = USER_PROFILES[username]
    if request.method == "POST":
        prof["empresa"] = request.form.get("empresa", prof["empresa"])
        prof["email"] = request.form.get("email", prof["email"])
        prof["telefono"] = request.form.get("telefono", prof["telefono"])
        prof["direccion"] = request.form.get("direccion", prof["direccion"])
        prof["rut"] = request.form.get("rut", prof["rut"])
        prof["descripcion"] = request.form.get("descripcion", prof["descripcion"])
    return render_template("perfil.html", perfil=prof, t=t)

@app.route("/ayuda")
def ayuda():
    return render_template("ayuda.html", t=t)

# ---------------------------
# Errores
# ---------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message=t("No encontrado","Not found","未找到"), t=t), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message=t("Error interno","Internal error","内部错误"), t=t), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
