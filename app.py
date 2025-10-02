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
# Datos ficticios
# ---------------------------
ROLES_COMPRA_VENTA = ["Productor", "Planta", "Packing", "Frigorífico", "Exportador", "Cliente extranjero"]
ROLES_SERVICIOS = ["Packing", "Frigorífico", "Transporte", "Agencia de Aduanas", "Extraportuario"]

USERS = {
    "productor1": {"password": "1234", "rol": "Productor", "perfil_tipo": "compra_venta", "pais": "CL"},
    "planta1": {"password": "1234", "rol": "Planta", "perfil_tipo": "compra_venta", "pais": "CL"},
    "packing1": {"password": "1234", "rol": "Packing", "perfil_tipo": "servicios", "pais": "CL"},
    "frigorifico1": {"password": "1234", "rol": "Frigorífico", "perfil_tipo": "servicios", "pais": "CL"},
    "exportador1": {"password": "1234", "rol": "Exportador", "perfil_tipo": "compra_venta", "pais": "CL"},
    "cliente1": {"password": "1234", "rol": "Cliente extranjero", "perfil_tipo": "compra_venta", "pais": "US"},
    "transporte1": {"password": "1234", "rol": "Transporte", "perfil_tipo": "servicios", "pais": "CL"},
    "aduana1": {"password": "1234", "rol": "Agencia de Aduanas", "perfil_tipo": "servicios", "pais": "CL"},
    "extraportuario1": {"password": "1234", "rol": "Extraportuario", "perfil_tipo": "servicios", "pais": "CL"},
}

USER_PROFILES = {
    "productor1": {"empresa": "Agro Maule", "rut": "76.111.222-3", "pais": "CL", "rol": "Productor",
                   "perfil_tipo": "compra_venta", "email": "agro@maule.cl", "telefono": "+56 9 1111 1111",
                   "direccion": "Talca, Maule", "descripcion": "Exportador de uva Thompson",
                   "items": [{"tipo": "oferta", "producto": "Uva Thompson", "cantidad": "100 pallets",
                              "origen": "Maule", "precio": "USD 25/caja"}]},
    "packing1": {"empresa": "PackSmart", "rut": "77.444.555-6", "pais": "CL", "rol": "Packing",
                 "perfil_tipo": "servicios", "email": "pack@smart.cl", "telefono": "+56 9 2222 2222",
                 "direccion": "Rancagua", "descripcion": "Packing de cerezas y arándanos",
                 "items": [{"tipo": "servicio", "servicio": "Embalaje exportación",
                            "capacidad": "30.000 cajas/día", "ubicacion": "Rancagua"}]},
    "frigorifico1": {"empresa": "FríoPoint Ltda.", "rut": "77.111.222-3", "pais": "CL", "rol": "Frigorífico",
                     "perfil_tipo": "servicios", "email": "contacto@friopoint.cl", "telefono": "+56 9 3333 3333",
                     "direccion": "Valparaíso", "descripcion": "Almacenaje frigorífico y túneles de frío",
                     "items": [{"tipo": "servicio", "servicio": "Almacenaje en frío",
                                "capacidad": "1200 pallets", "ubicacion": "Valparaíso"}]},
    "exportador1": {"empresa": "OCExport", "rut": "76.999.888-1", "pais": "CL", "rol": "Exportador",
                    "perfil_tipo": "compra_venta", "email": "ventas@ocexport.cl", "telefono": "+56 9 4444 4444",
                    "direccion": "Santiago", "descripcion": "Exportador multiproducto",
                    "items": [{"tipo": "demanda", "producto": "Cerezas", "cantidad": "150 pallets",
                               "origen": "VI-VII Región", "precio": "A convenir"}]},
}

COMPANIES = list(USER_PROFILES.values())

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
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
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

@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect(url_for("login"))
    username = session["usuario"]
    user = USERS.get(username)
    my_company = USER_PROFILES.get(username, {})
    return render_template("dashboard.html", usuario=username, rol=user["rol"],
                           perfil_tipo=user["perfil_tipo"], my_company=my_company,
                           cart=get_cart(), t=t)

@app.route("/accesos/<tipo>")
def accesos(tipo):
    tipo = tipo.lower()
    if tipo not in ["ventas", "compras", "servicios"]:
        abort(404)
    if tipo == "servicios":
        data = [c for c in COMPANIES if c["perfil_tipo"] == "servicios"]
        return render_template("detalle_servicios.html", data=data, t=t)
    if tipo == "ventas":
        data = [c for c in COMPANIES if any(it["tipo"] == "oferta" for it in c["items"])]
        return render_template("detalle_ventas.html", data=data, t=t)
    if tipo == "compras":
        data = [c for c in COMPANIES if any(it["tipo"] == "demanda" for it in c["items"])]
        return render_template("detalle_compras.html", data=data, t=t)

@app.route("/empresa/<username>")
def empresa(username):
    prof = USER_PROFILES.get(username)
    if not prof:
        abort(404)
    return render_template("empresa.html", comp=prof, t=t)

@app.route("/cart")
def cart_view():
    return render_template("carrito.html", cart=get_cart(), t=t)

@app.route("/cart/add", methods=["POST"])
def cart_add():
    item = request.form.to_dict()
    cart = get_cart()
    cart.append(item)
    session["cart"] = cart
    return redirect(url_for("cart_view"))

@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    if not login_required():
        return redirect(url_for("login"))
    username = session["usuario"]
    prof = USER_PROFILES.get(username)
    if not prof:
        abort(404)
    return render_template("perfil.html", perfil=prof, t=t)

@app.route("/ayuda", methods=["GET", "POST"])
def ayuda():
    msg = None
    if request.method == "POST":
        email = request.form.get("email")
        mensaje = request.form.get("mensaje")
        msg = t("Gracias, responderemos a tu correo.", "Thanks, we will reply to your email.")
    return render_template("ayuda.html", mensaje=msg, t=t)

# ---------------------------
# Errores
# ---------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message=t("No encontrado", "Not found"), t=t), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message=t("Error interno", "Internal server error"), t=t), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
