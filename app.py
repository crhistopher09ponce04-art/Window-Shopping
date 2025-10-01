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

USER_PROFILES = {
    u: {
        "empresa": u.capitalize(),
        "pais": USERS[u].get("pais", "CL"),
        "rol": USERS[u]["rol"],
        "perfil_tipo": USERS[u]["perfil_tipo"],
        "email": f"{u}@demo.cl",
        "telefono": "+56 9 0000 0000",
        "direccion": "S/N",
        "rut": "",
        "descripcion": "Perfil demo.",
        "items": []
    } for u in USERS
}

# Empresas de muestra
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
            {"tipo": "servicio", "servicio": "Preenfriado", "capacidad": "8 túneles", "ubicacion": "Valparaíso"}
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
            error = t("Usuario o clave inválidos.", "Invalid user or password.", "用戶或密碼無效。")
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
        perfil_tipo = request.form.get("perfil_tipo", "").strip()
        rut = request.form.get("rut", "").strip()

        if not username or not password or not rol or not perfil_tipo:
            error = t("Completa los campos obligatorios.", "Please complete required fields.", "請完成必填欄位。")
        elif username in USERS:
            error = t("El usuario ya existe.", "User already exists.", "用戶已存在。")
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
                "descripcion": "Nuevo perfil.",
                "items": []
            }
            session["usuario"] = username
            return redirect(url_for("dashboard"))

    return render_template("register.html", error=error, nacionalidad=nacionalidad,
                           perfil_tipo=perfil_tipo, roles_cv=ROLES_COMPRA_VENTA,
                           roles_srv=ROLES_SERVICIOS, t=t)

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
    else:
        data = [c for c in COMPANIES if c["perfil_tipo"] == "compra_venta"]
    return render_template("accesos.html", tipo=tipo, data=data, t=t)

@app.route("/empresa/<slug>")
def empresa(slug):
    comp = next((c for c in COMPANIES if c["slug"] == slug), None)
    if not comp:
        prof = USER_PROFILES.get(slug)
        if not prof: abort(404)
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
    if not prof: abort(404)

    msg = None
    if request.method == "POST":
        action = request.form.get("action")
        if action == "save_profile":
            prof["empresa"] = request.form.get("empresa", prof["empresa"])
            prof["email"] = request.form.get("email", prof["email"])
            prof["telefono"] = request.form.get("telefono", prof["telefono"])
            prof["direccion"] = request.form.get("direccion", prof["direccion"])
            prof["rut"] = request.form.get("rut", prof["rut"])
            prof["descripcion"] = request.form.get("descripcion", prof["descripcion"])
            msg = t("Perfil actualizado.", "Profile updated.", "檔案已更新。")
        elif action == "add_item":
            if prof.get("perfil_tipo") == "servicios":
                servicio = request.form.get("servicio", "")
                capacidad = request.form.get("capacidad", "")
                ubicacion = request.form.get("ubicacion", "")
                if servicio:
                    prof["items"].append({"tipo": "servicio", "servicio": servicio, "capacidad": capacidad, "ubicacion": ubicacion})
                    msg = t("Servicio agregado.", "Service added.", "已添加服務。")
            else:
                subtipo = request.form.get("subtipo", "oferta")
                producto = request.form.get("producto", "")
                cantidad = request.form.get("cantidad", "")
                origen = request.form.get("origen", "")
                precio = request.form.get("precio", "")
                if producto:
                    prof["items"].append({"tipo": subtipo, "producto": producto, "cantidad": cantidad, "origen": origen, "precio": precio})
                    msg = t("Ítem agregado.", "Item added.", "已添加項目。")
    return render_template("perfil.html", perfil=prof, mensaje=msg, t=t)

# ---------------------------
# Errores
# ---------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message=t("No encontrado", "Not found", "未找到"), t=t), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message=t("Error interno", "Internal server error", "內部錯誤"), t=t), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
