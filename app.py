import os
from flask import Flask, render_template, request, redirect, url_for, session, abort, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave_secreta_window_shopping")

# ------------------------
# i18n simple (ES/EN)
# ------------------------
LANGS = {"es": "Español", "en": "English"}

def get_lang():
    lang = session.get("lang", "es")
    return lang if lang in LANGS else "es"

def t(es, en):
    return es if get_lang() == "es" else en

@app.context_processor
def inject_globals():
    return {
        "LANGS": LANGS,
        "cur_lang": get_lang()
    }

@app.route("/lang/<code>")
def set_lang(code):
    session["lang"] = code if code in LANGS else "es"
    return redirect(request.args.get("next") or url_for("home"))

# ------------------------
# Roles
# ------------------------
FRUIT_ROLES = {"Productor", "Planta", "Packing", "Frigorífico", "Exportador", "Cliente extranjero"}
SERVICE_ROLES = {"Packing", "Frigorífico", "Transporte", "Agencia de aduana", "Extraportuario", "Planta", "Exportador"}

# ------------------------
# Empresas demo (seed)
# ------------------------
empresas = {
    # Fruta
    "C001": {"id": "C001", "name": "Agrícola Montolín", "role": "Productor", "city": "Maule", "country": "Chile",
             "fruit": "Ciruela", "variety": "Black Diamond", "volume_tons": 50, "price_box": 17500, "price_kg": 400,
             "phone": "+56 9 8765 4321", "email": "ventas@montolin.cl"},
    "C002": {"id": "C002", "name": "Planta Ejemplo", "role": "Planta", "city": "Talca", "country": "Chile",
             "fruit": "Ciruela", "variety": "D'Agen", "volume_tons": 28, "price_box": 16800, "price_kg": 390,
             "phone": "+56 9 5555 5555", "email": "planta@ejemplo.cl"},
    "C003": {"id": "C003", "name": "Pukiyai Packing", "role": "Packing", "city": "Rancagua", "country": "Chile",
             "fruit": "Ciruela", "variety": "Black Amber", "volume_tons": 40, "price_box": 18000, "price_kg": 420,
             "phone": "+56 2 2345 6789", "email": "info@pukiyai.cl"},
    "C004": {"id": "C004", "name": "Frigo Sur", "role": "Frigorífico", "city": "Curicó", "country": "Chile",
             "fruit": "Ciruela", "variety": "Angeleno", "volume_tons": 60, "price_box": 16500, "price_kg": 370,
             "phone": "+56 72 222 3333", "email": "contacto@frigosur.cl"},
    "C005": {"id": "C005", "name": "Tuniche Fruit", "role": "Exportador", "city": "Valparaíso", "country": "Chile",
             "fruit": "Ciruela", "variety": "Black Diamond", "volume_tons": 30, "price_box": 17000, "price_kg": 380,
             "phone": "+56 9 8123 4567", "email": "contacto@tuniche.cl"},

    # Cliente exterior (fruta)
    "X001": {"id": "X001", "name": "Chensen Ogen Ltd.", "role": "Cliente extranjero", "city": "Shenzhen", "country": "China",
             "product_requested": "Ciruela fresca", "variety_requested": "Black Diamond", "volume_requested_tons": 50,
             "phone": "+86 138 0000 1111", "email": "chen@ogen.cn"},

    # Servicios
    "S001": {"id": "S001", "name": "Transporte Andes", "role": "Transporte", "city": "Santiago", "country": "Chile",
             "service": "Camiones refrigerados", "phone": "+56 2 3456 7890", "email": "contacto@transporteandes.cl"},
    "S002": {"id": "S002", "name": "Aduanas Chile Ltda.", "role": "Agencia de aduana", "city": "Valparaíso", "country": "Chile",
             "service": "Gestión documental y trámites", "phone": "+56 2 9999 1111", "email": "aduana@chile.cl"},
    "S003": {"id": "S003", "name": "Puerto Seco SA", "role": "Extraportuario", "city": "San Antonio", "country": "Chile",
             "service": "Almacenaje extraportuario", "phone": "+56 35 1234 567", "email": "info@puertoseco.cl"}
}

# ------------------------
# Usuarios demo (1 por perfil)
# ------------------------
usuarios = {
    "productor1": {"password": "1234", "rol": "Productor", "company_id": "C001"},
    "planta1": {"password": "1234", "rol": "Planta", "company_id": "C002"},
    "packing1": {"password": "1234", "rol": "Packing", "company_id": "C003"},
    "frigorifico1": {"password": "1234", "rol": "Frigorífico", "company_id": "C004"},
    "exportador1": {"password": "1234", "rol": "Exportador", "company_id": "C005"},
    "cliente1": {"password": "1234", "rol": "Cliente extranjero", "company_id": "X001"},
    "transporte1": {"password": "1234", "rol": "Transporte", "company_id": "S001"},
    "aduana1": {"password": "1234", "rol": "Agencia de aduana", "company_id": "S002"},
    "extraportuario1": {"password": "1234", "rol": "Extraportuario", "company_id": "S003"}
}

# ------------------------
# Reglas de flujo
# ------------------------
VENTAS_FRUTA = {
    "Productor": ["Packing", "Frigorífico", "Exportador"],
    "Planta": ["Packing", "Frigorífico", "Exportador"],
    "Packing": ["Frigorífico", "Exportador"],
    "Frigorífico": ["Packing", "Exportador"],
    "Exportador": ["Cliente extranjero"],
    "Cliente extranjero": []
}
COMPRAS_FRUTA = {
    "Packing": ["Planta", "Frigorífico"],
    "Frigorífico": ["Planta", "Packing"],
    "Exportador": ["Exportador", "Packing", "Frigorífico", "Planta"],
    "Cliente extranjero": ["Exportador"],
    "Productor": [],
    "Planta": []
}
VENTAS_SERV = {
    "Packing": ["Planta", "Frigorífico", "Exportador"],
    "Frigorífico": ["Planta", "Exportador", "Packing"],
    "Transporte": ["Exportador", "Planta", "Packing", "Frigorífico"],
    "Agencia de aduana": ["Exportador"],
    "Extraportuario": ["Exportador"],
    "Planta": [],
    "Exportador": []
}
COMPRAS_SERV = {
    "Packing": ["Frigorífico", "Transporte"],
    "Frigorífico": ["Packing", "Transporte"],
    "Exportador": ["Packing", "Transporte", "Agencia de aduana", "Extraportuario"],
    "Planta": [],
    "Transporte": [],
    "Agencia de aduana": [],
    "Extraportuario": []
}

# ------------------------
# Helpers
# ------------------------
def _matches_rubro(company, rubro):
    if rubro == "servicio":
        return company["role"] in SERVICE_ROLES or "service" in company
    return company["role"] in FRUIT_ROLES or "fruit" in company

def destinos_por_rol(rol, tipo, rubro):
    if rubro == "servicio":
        mapping = VENTAS_SERV if tipo == "ventas" else COMPRAS_SERV
    else:
        mapping = VENTAS_FRUTA if tipo == "ventas" else COMPRAS_FRUTA
    return mapping.get(rol, [])

def companies_for_roles(roles, rubro):
    return [c for c in empresas.values() if c["role"] in roles and _matches_rubro(c, rubro)]

def apply_filters(lista, args):
    q = (args.get("q") or "").strip().lower()
    country = (args.get("country") or "").strip().lower()
    city = (args.get("city") or "").strip().lower()
    role = (args.get("role") or "").strip()

    def to_float(x):
        try:
            return float(x)
        except:
            return None

    min_vol = to_float(args.get("min_volume"))
    max_vol = to_float(args.get("max_volume"))
    min_pb = to_float(args.get("min_price_box"))
    max_pb = to_float(args.get("max_price_box"))
    min_pk = to_float(args.get("min_price_kg"))
    max_pk = to_float(args.get("max_price_kg"))

    filtered = []
    for c in lista:
        blob = " ".join([
            c.get("name",""), c.get("city",""), c.get("country",""),
            c.get("fruit",""), c.get("variety",""), c.get("service",""),
            c.get("product_requested",""), c.get("variety_requested","")
        ]).lower()
        if q and q not in blob: continue
        if country and country not in c.get("country","").lower(): continue
        if city and city not in c.get("city","").lower(): continue
        if role and role != c.get("role"): continue

        vol = c.get("volume_tons") or c.get("volume_requested_tons")
        if min_vol is not None and (vol is None or vol < min_vol): continue
        if max_vol is not None and (vol is None or vol > max_vol): continue

        pb = c.get("price_box")
        if min_pb is not None and (pb is None or pb < min_pb): continue
        if max_pb is not None and (pb is None or pb > max_pb): continue

        pk = c.get("price_kg")
        if min_pk is not None and (pk is None or pk < min_pk): continue
        if max_pk is not None and (pk is None or pk > max_pk): continue

        filtered.append(c)

    sort = args.get("sort") or "name"
    reverse = sort.startswith("-")
    sort_key = sort[1:] if reverse else sort
    valid = {"name", "city", "country", "price_box", "price_kg", "volume_tons"}
    if sort_key not in valid: sort_key = "name"
    filtered.sort(key=lambda x: (x.get(sort_key) is None, x.get(sort_key)), reverse=reverse)
    return filtered

def require_login():
    if "usuario" not in session:
        flash(t("Inicia sesión para continuar.", "Log in to continue."))
        return False
    return True

# ------------------------
# Rutas públicas
# ------------------------
@app.route("/")
def home():
    if "usuario" in session:
        return redirect(url_for("dashboard"))
    return render_template("landing.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    u = usuarios.get(username)
    if u and u["password"] == password:
        session["usuario"] = username
        session["rol"] = u["rol"]
        session["company_id"] = u["company_id"]
        session.setdefault("cart", [])
        flash(t("Bienvenido", "Welcome"))
        return redirect(url_for("dashboard"))
    return render_template("login.html", error=t("Usuario o contraseña incorrectos", "Invalid credentials"))

@app.route("/register")
def register_router():
    # (Demo) pantalla intermedia de registro; si quieres registro real, lo implementamos luego
    return render_template("register_router.html")

@app.route("/password-reset", methods=["GET", "POST"])
def password_reset():
    if request.method == "GET":
        return render_template("password_reset.html")
    email = request.form.get("email", "")
    flash(t("Si el correo existe, te enviaremos un enlace para restablecer.",
            "If the email exists, we sent you a reset link."))
    return redirect(url_for("login"))

@app.route("/help")
def help_center():
    return render_template("help_center.html")

@app.route("/manual")
def manual():
    return render_template("manual.html")

# ------------------------
# Rutas privadas
# ------------------------
@app.route("/dashboard")
def dashboard():
    if not require_login(): return redirect(url_for("home"))
    user = usuarios[session["usuario"]]
    my_company = empresas.get(user["company_id"])
    return render_template("dashboard.html", usuario=session["usuario"], rol=user["rol"], my_company=my_company)

@app.route("/accesos/<tipo>")
def accesos(tipo):
    if not require_login(): return redirect(url_for("home"))
    rol = session["rol"]
    rubro = request.args.get("rubro") or ("servicio" if rol in SERVICE_ROLES and rol not in FRUIT_ROLES else "fruta")
    roles_destino = destinos_por_rol(rol, tipo, rubro)
    lista = companies_for_roles(roles_destino, rubro=rubro)
    lista = apply_filters(lista, request.args)
    values = {k: request.args.get(k, "") for k in
              ("q", "country", "city", "role", "min_volume", "max_volume", "min_price_box", "max_price_box", "min_price_kg", "max_price_kg", "sort")}
    roles_opts = sorted(FRUIT_ROLES if rubro == "fruta" else SERVICE_ROLES)
    return render_template("accesos.html", tipo=tipo, rubro=rubro, empresas=lista, rol=rol,
                           usuario=session["usuario"], values=values, roles_opts=roles_opts)

@app.route("/detalle/<company_id>", methods=["GET", "POST"])
def detalle(company_id):
    if not require_login(): return redirect(url_for("home"))
    c = empresas.get(company_id)
    if not c: abort(404)
    if request.method == "POST":
        item = {
            "company_id": company_id,
            "name": c["name"],
            "role": c["role"],
            "rubro": "servicio" if c["role"] in ["Transporte", "Agencia de aduana", "Extraportuario"] else "fruta",
            "quantity": request.form.get("quantity", "1"),
            "notes": request.form.get("notes", "")
        }
        cart = session.setdefault("cart", [])
        cart.append(item)
        session["cart"] = cart
        flash(t("Agregado al carrito.", "Added to cart."))
        return redirect(url_for("cart"))
    return render_template("detalle.html", company=c)

@app.route("/cart", methods=["GET", "POST"])
def cart():
    if not require_login(): return redirect(url_for("home"))
    if request.method == "POST":
        action = request.form.get("action")
        if action == "clear":
            session["cart"] = []
            flash(t("Carrito vaciado.", "Cart cleared."))
        elif action and action.startswith("remove:"):
            idx = int(action.split(":")[1])
            cart = session.get("cart", [])
            if 0 <= idx < len(cart):
                cart.pop(idx)
                session["cart"] = cart
                flash(t("Ítem eliminado.", "Item removed."))
        elif action == "checkout":
            session["cart"] = []
            flash(t("¡Solicitud enviada! Nuestro equipo te contactará.", "Request sent! Our team will contact you."))
            return redirect(url_for("dashboard"))
    return render_template("cart.html", cart=session.get("cart", []))

@app.route("/mi-perfil", methods=["GET", "POST"])
def mi_perfil():
    if not require_login(): return redirect(url_for("home"))
    company_id = session["company_id"]
    c = empresas.get(company_id)
    if not c: abort(404)
    if request.method == "POST":
        c["name"] = request.form.get("name", c["name"])
        c["city"] = request.form.get("city", c.get("city", ""))
        c["country"] = request.form.get("country", c.get("country", ""))
        c["phone"] = request.form.get("phone", c.get("phone", ""))
        c["email"] = request.form.get("email", c.get("email", ""))

        if c["role"] in FRUIT_ROLES and c["role"] != "Cliente extranjero":
            c["fruit"] = request.form.get("fruit", c.get("fruit", ""))
            c["variety"] = request.form.get("variety", c.get("variety", ""))
            def fnum(k, default=None):
                try:
                    return float(request.form.get(k, ""))
                except:
                    return default
            c["volume_tons"] = fnum("volume_tons", c.get("volume_tons"))
            c["price_box"] = fnum("price_box", c.get("price_box"))
            c["price_kg"] = fnum("price_kg", c.get("price_kg"))

        if c["role"] == "Cliente extranjero":
            c["product_requested"] = request.form.get("product_requested", c.get("product_requested", ""))
            c["variety_requested"] = request.form.get("variety_requested", c.get("variety_requested", ""))
            try:
                c["volume_requested_tons"] = float(request.form.get("volume_requested_tons", ""))
            except:
                pass

        if c["role"] in SERVICE_ROLES and c["role"] not in FRUIT_ROLES:
            c["service"] = request.form.get("service", c.get("service", ""))

        flash(t("Cambios guardados.", "Changes saved."))
        return redirect(url_for("mi_perfil"))
    return render_template("mi_perfil.html", company=c)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ------------------------
# Errores
# ------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message=t("Recurso no encontrado", "Resource not found")), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message=t("Error interno", "Internal server error")), 500

# ------------------------
# Entrypoint local
# ------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
