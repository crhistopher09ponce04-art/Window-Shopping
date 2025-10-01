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
# Datos demo
# ---------------------------
ROLES_COMPRA_VENTA = [
    "Productor", "Planta", "Packing", "Frigorífico", "Exportador", "Cliente extranjero"
]
ROLES_SERVICIOS = [
    "Packing", "Frigorífico", "Transporte", "Agencia de Aduanas", "Extraportuario"
]

USERS = {
    "productor1": {"password": "1234", "rol": "Productor", "perfil_tipo": "compra_venta", "pais": "CL"},
    "planta1": {"password": "1234", "rol": "Planta", "perfil_tipo": "compra_venta", "pais": "CL"},
    "packing1": {"password": "1234", "rol": "Packing", "perfil_tipo": "compra_venta", "pais": "CL"},
    "frigorifico1": {"password": "1234", "rol": "Frigorífico", "perfil_tipo": "compra_venta", "pais": "CL"},
    "exportador1": {"password": "1234", "rol": "Exportador", "perfil_tipo": "compra_venta", "pais": "CL"},
    "cliente1": {"password": "1234", "rol": "Cliente extranjero", "perfil_tipo": "compra_venta", "pais": "US"},
    "transporte1": {"password": "1234", "rol": "Transporte", "perfil_tipo": "servicios", "pais": "CL"},
    "aduana1": {"password": "1234", "rol": "Agencia de Aduanas", "perfil_tipo": "servicios", "pais": "CL"},
    "extraportuario1": {"password": "1234", "rol": "Extraportuario", "perfil_tipo": "servicios", "pais": "CL"},
}

# Perfiles de usuarios reales
USER_PROFILES = {
    u: {
        "slug": u,
        "nombre": u.capitalize(),
        "rol": USERS[u]["rol"],
        "perfil_tipo": USERS[u]["perfil_tipo"],
        "pais": USERS[u]["pais"],
        "descripcion": "Perfil demo generado automáticamente.",
        "items": []
    } for u in USERS
}

# Empresas demo
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
            {"tipo": "servicio", "servicio": "Preenfriado", "capacidad": "8 túneles", "ubicacion": "Valparaíso"},
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
    return render_template("landing.html", t=t)

@app.route("/login", methods=["GET","POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form.get("username")
        p = request.form.get("password")
        if u in USERS and USERS[u]["password"] == p:
            session["usuario"] = u
            return redirect(url_for("dashboard"))
        else:
            error = t("Usuario o clave inválidos.","Invalid user/password.","用戶或密碼錯誤")
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
        username = request.form.get("username")
        password = request.form.get("password")
        rol = request.form.get("rol")
        perfil_tipo = request.form.get("perfil_tipo")
        if username in USERS:
            error = "Usuario ya existe"
        else:
            USERS[username] = {"password": password, "rol": rol, "perfil_tipo": perfil_tipo, "pais": "CL"}
            USER_PROFILES[username] = {
                "slug": username,
                "nombre": username.capitalize(),
                "rol": rol,
                "perfil_tipo": perfil_tipo,
                "pais": "CL",
                "descripcion": "Perfil registrado.",
                "items": []
            }
            session["usuario"] = username
            return redirect(url_for("dashboard"))
    return render_template("register.html", error=error, roles_cv=ROLES_COMPRA_VENTA, roles_srv=ROLES_SERVICIOS, t=t)

@app.route("/dashboard")
def dashboard():
    if not login_required(): return redirect(url_for("login"))
    u = session["usuario"]
    prof = USER_PROFILES.get(u)
    return render_template("dashboard.html", usuario=u, rol=prof["rol"], perfil_tipo=prof["perfil_tipo"], cart=get_cart(), t=t)

@app.route("/accesos/<tipo>")
def accesos(tipo):
    tipo = tipo.lower()
    if tipo not in ["ventas","compras","servicios"]: abort(404)
    # combinamos companies + perfiles
    all_data = COMPANIES + list(USER_PROFILES.values())
    if tipo == "servicios":
        data = [c for c in all_data if c["perfil_tipo"] == "servicios"]
    else:
        data = [c for c in all_data if c["perfil_tipo"] == "compra_venta"]
    return render_template("accesos.html", tipo=tipo, data=data, t=t)

@app.route("/empresa/<slug>")
def empresa(slug):
    comp = next((c for c in COMPANIES if c["slug"] == slug), None)
    if not comp:
        comp = USER_PROFILES.get(slug)
    if not comp: abort(404)
    return render_template("empresa.html", comp=comp, t=t)

@app.route("/cart/add", methods=["POST"])
def cart_add():
    cart = get_cart()
    cart.append(request.form.to_dict())
    session["cart"] = cart
    return redirect(request.referrer or url_for("dashboard"))

# ---------------------------
# Errores
# ---------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="No encontrado", t=t), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message="Error interno", t=t), 500

if __name__ == "__main__":
    app.run(debug=True)
