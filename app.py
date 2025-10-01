import os
from flask import Flask, render_template, request, redirect, url_for, session, abort, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave_secreta_window_shopping")

# =========================
# i18n (ES/EN) sencillo
# =========================
LANGS = {"es": "Español", "en": "English"}

TRANSLATIONS = {
    "es": {
        "brand": "Window Shopping",
        "login": "Iniciar sesión",
        "logout": "Salir",
        "register": "Crear cuenta",
        "dashboard": "Dashboard",
        "help": "Centro de Ayuda",
        "manual": "Manual de Usuario",
        "cart": "Carrito",
        "my_profile": "Mi Perfil",
        "my_items": "Mis ítems",
        "sell": "Vender",
        "buy": "Comprar",
        "apply_filters": "Aplicar filtros",
        "clear": "Limpiar",
        "back": "Volver",
        "add_to_cart": "Agregar al carrito",
        "quantity": "Cantidad",
        "unit": "Unidad",
        "notes": "Notas",
        "price": "Precio",
        "role": "Rol",
        "country": "País",
        "city": "Ciudad",
        "product": "Producto",
        "variety": "Variedad",
        "type": "Tipo",
        "rubro": "Rubro",
        "sale": "venta",
        "buying": "compra",
        "fruit": "fruta",
        "service": "servicio",
        "email": "Correo",
        "name": "Nombre",
        "actions": "Acciones",
        "empty_list": "No hay resultados para los filtros.",
        "item_added": "Agregado al carrito.",
        "cart_cleared": "Carrito vaciado.",
        "item_removed": "Ítem eliminado.",
        "request_sent": "¡Solicitud enviada! Nuestro equipo te contactará.",
        "changes_saved": "Cambios guardados.",
        "login_needed": "Inicia sesión para continuar.",
        "invalid_credentials": "Usuario o contraseña incorrectos",
        "welcome": "Bienvenido",
        "search": "Búsqueda",
        "order_by": "Ordenar por",
        "min": "mín",
        "max": "máx",
        "volume": "Cantidad",
        "price_box": "Precio caja",
        "price_kg": "Precio kg",
        "units": {
            "tons": "tons",
            "kg": "kg",
            "boxes": "cajas",
            "pallets": "pallets",
            "containers": "contenedores"
        }
    },
    "en": {
        "brand": "Window Shopping",
        "login": "Log in",
        "logout": "Log out",
        "register": "Create account",
        "dashboard": "Dashboard",
        "help": "Help Center",
        "manual": "User Manual",
        "cart": "Cart",
        "my_profile": "My Profile",
        "my_items": "My Items",
        "sell": "Sell",
        "buy": "Buy",
        "apply_filters": "Apply filters",
        "clear": "Clear",
        "back": "Back",
        "add_to_cart": "Add to cart",
        "quantity": "Quantity",
        "unit": "Unit",
        "notes": "Notes",
        "price": "Price",
        "role": "Role",
        "country": "Country",
        "city": "City",
        "product": "Product",
        "variety": "Variety",
        "type": "Type",
        "rubro": "Segment",
        "sale": "sale",
        "buying": "buy",
        "fruit": "fruit",
        "service": "service",
        "email": "Email",
        "name": "Name",
        "actions": "Actions",
        "empty_list": "No results for the filters.",
        "item_added": "Added to cart.",
        "cart_cleared": "Cart cleared.",
        "item_removed": "Item removed.",
        "request_sent": "Request sent! Our team will contact you.",
        "changes_saved": "Changes saved.",
        "login_needed": "Log in to continue.",
        "invalid_credentials": "Invalid credentials",
        "welcome": "Welcome",
        "search": "Search",
        "order_by": "Order by",
        "min": "min",
        "max": "max",
        "volume": "Quantity",
        "price_box": "Box price",
        "price_kg": "Kg price",
        "units": {
            "tons": "tons",
            "kg": "kg",
            "boxes": "boxes",
            "pallets": "pallets",
            "containers": "containers"
        }
    }
}

def get_lang():
    lang = session.get("lang", "es")
    return lang if lang in LANGS else "es"

def _(key):
    lang = get_lang()
    # soporte "units.xxx"
    d = TRANSLATIONS.get(lang, {})
    node = d
    for part in key.split("."):
        node = node.get(part, None) if isinstance(node, dict) else None
        if node is None: return key
    return node if isinstance(node, str) else key

@app.context_processor
def inject_globals():
    return {
        "LANGS": LANGS,
        "cur_lang": get_lang(),
        "_": _
    }

@app.route("/lang/<code>")
def set_lang(code):
    session["lang"] = code if code in LANGS else "es"
    return redirect(request.args.get("next") or url_for("home"))

# =========================
# Roles y flujo
# =========================
FRUIT_ROLES = {"Productor", "Planta", "Packing", "Frigorífico", "Exportador", "Cliente extranjero"}
SERVICE_ROLES = {"Packing", "Frigorífico", "Transporte", "Agencia de aduana", "Extraportuario", "Planta", "Exportador"}

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

# =========================
# Datos demo + estructura multi-ítems
# =========================
UNITS = ["tons", "kg", "boxes", "pallets", "containers"]

def seed_items_for_company(role):
    # demo básico por rol
    if role in ["Transporte", "Agencia de aduana", "Extraportuario"]:
        return [{
            "type": "venta", "rubro": "servicio",
            "product": "Servicio " + role, "variety": "",
            "quantity": 1, "unit": "containers", "price": "", "details": "Disponibilidad inmediata"
        }]
    elif role == "Cliente extranjero":
        return [{
            "type": "compra", "rubro": "fruta",
            "product": "Ciruela fresca", "variety": "Black Diamond",
            "quantity": 50, "unit": "tons", "price": "", "details": "Entrega Octubre"
        }]
    else:
        return [{
            "type": "venta", "rubro": "fruta",
            "product": "Ciruela", "variety": "Black Diamond",
            "quantity": 40, "unit": "tons", "price": "17500/caja", "details": "Calibre mixto"
        }]

empresas = {
    "C001": {"id": "C001", "name": "Agrícola Montolín", "role": "Productor", "city": "Maule", "country": "Chile",
             "phone": "+56 9 8765 4321", "email": "ventas@montolin.cl",
             "items": seed_items_for_company("Productor")},
    "C002": {"id": "C002", "name": "Planta Ejemplo", "role": "Planta", "city": "Talca", "country": "Chile",
             "phone": "+56 9 5555 5555", "email": "planta@ejemplo.cl",
             "items": seed_items_for_company("Planta")},
    "C003": {"id": "C003", "name": "Pukiyai Packing", "role": "Packing", "city": "Rancagua", "country": "Chile",
             "phone": "+56 2 2345 6789", "email": "info@pukiyai.cl",
             "items": seed_items_for_company("Packing")},
    "C004": {"id": "C004", "name": "Frigo Sur", "role": "Frigorífico", "city": "Curicó", "country": "Chile",
             "phone": "+56 72 222 3333", "email": "contacto@frigosur.cl",
             "items": seed_items_for_company("Frigorífico")},
    "C005": {"id": "C005", "name": "Tuniche Fruit", "role": "Exportador", "city": "Valparaíso", "country": "Chile",
             "phone": "+56 9 8123 4567", "email": "contacto@tuniche.cl",
             "items": seed_items_for_company("Exportador")},
    "X001": {"id": "X001", "name": "Chensen Ogen Ltd.", "role": "Cliente extranjero", "city": "Shenzhen", "country": "China",
             "phone": "+86 138 0000 1111", "email": "chen@ogen.cn",
             "items": seed_items_for_company("Cliente extranjero")},
    "S001": {"id": "S001", "name": "Transporte Andes", "role": "Transporte", "city": "Santiago", "country": "Chile",
             "phone": "+56 2 3456 7890", "email": "contacto@transporteandes.cl",
             "items": seed_items_for_company("Transporte")},
    "S002": {"id": "S002", "name": "Aduanas Chile Ltda.", "role": "Agencia de aduana", "city": "Valparaíso", "country": "Chile",
             "phone": "+56 2 9999 1111", "email": "aduana@chile.cl",
             "items": seed_items_for_company("Agencia de aduana")},
    "S003": {"id": "S003", "name": "Puerto Seco SA", "role": "Extraportuario", "city": "San Antonio", "country": "Chile",
             "phone": "+56 35 1234 567", "email": "info@puertoseco.cl",
             "items": seed_items_for_company("Extraportuario")},
}

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

# =========================
# Helpers
# =========================
def require_login():
    if "usuario" not in session:
        flash(_("login_needed"))
        return False
    return True

def next_company_id():
    # genera Cxyz / Sxyz / Xxyz según rol
    base = len(empresas) + 1
    return f"C{base:03d}"

def destinos_por_rol(rol, tipo, rubro):
    if rubro == "servicio":
        mapping = VENTAS_SERV if tipo == "ventas" else COMPRAS_SERV
    else:
        mapping = VENTAS_FRUTA if tipo == "ventas" else COMPRAS_FRUTA
    return mapping.get(rol, [])

def companies_for_roles(roles):
    return [c for c in empresas.values() if c["role"] in roles]

def apply_company_filters(lista, args):
    q = (args.get("q") or "").strip().lower()
    country = (args.get("country") or "").strip().lower()
    city = (args.get("city") or "").strip().lower()
    role = (args.get("role") or "").strip()

    out = []
    for c in lista:
        blob = " ".join([c.get("name",""), c.get("city",""), c.get("country","")]).lower()
        if q and q not in blob: continue
        if country and country not in c.get("country","").lower(): continue
        if city and city not in c.get("city","").lower(): continue
        if role and role != c.get("role"): continue
        out.append(c)
    return out

# =========================
# Rutas públicas
# =========================
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
        flash(_("welcome"))
        return redirect(url_for("dashboard"))
    return render_template("login.html", error=_("invalid_credentials"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    username = request.form.get("usuario", "").strip()
    password = request.form.get("password", "").strip()
    rol = request.form.get("rol", "").strip()
    name = request.form.get("empresa", "").strip()
    city = request.form.get("ciudad", "").strip()
    country = request.form.get("pais", "").strip()
    phone = request.form.get("telefono", "").strip()
    email = request.form.get("email", "").strip()

    if not username or username in usuarios:
        return render_template("register.html", error="Usuario inválido o ya existe.")
    if not password or not rol or not name:
        return render_template("register.html", error="Completa los campos requeridos.")

    new_id = next_company_id()
    empresas[new_id] = {
        "id": new_id, "name": name, "role": rol, "city": city, "country": country,
        "phone": phone, "email": email, "items": []
    }
    usuarios[username] = {"password": password, "rol": rol, "company_id": new_id}
    session["usuario"] = username
    session["rol"] = rol
    session["company_id"] = new_id
    session.setdefault("cart", [])
    flash(_("welcome"))
    return redirect(url_for("dashboard"))

@app.route("/help")
def help_center():
    return render_template("help_center.html")

@app.route("/manual")
def manual():
    return render_template("manual.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# =========================
# Rutas privadas
# =========================
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
    # empresas destino por rol
    roles_destino = destinos_por_rol(rol, tipo, rubro)
    lista_empresas = companies_for_roles(roles_destino)
    lista_empresas = apply_company_filters(lista_empresas, request.args)

    # filtros de items
    f_tipo = request.args.get("tipo_item", "")  # "venta" / "compra" / ""
    f_rubro = rubro
    q = (request.args.get("q") or "").strip().lower()

    # construir lista de filas por item
    filas = []
    for c in lista_empresas:
        for idx, it in enumerate(c.get("items", [])):
            if f_rubro and it.get("rubro") != f_rubro: continue
            if f_tipo and it.get("type") != f_tipo: continue
            blob = " ".join([c["name"], c["city"], c["country"],
                             it.get("product",""), it.get("variety",""), it.get("details","")]).lower()
            if q and q not in blob: continue
            filas.append({
                "company": c, "item": it, "item_index": idx
            })

    roles_opts = sorted(FRUIT_ROLES if rubro == "fruta" else SERVICE_ROLES)
    values = {k: request.args.get(k, "") for k in
              ("q", "country", "city", "role", "sort", "tipo_item")}
    return render_template("accesos.html", tipo=tipo, rubro=rubro, filas=filas, rol=rol,
                           usuario=session["usuario"], values=values, roles_opts=roles_opts, UNITS=UNITS)

@app.route("/detalle/<company_id>", methods=["GET", "POST"])
def detalle(company_id):
    if not require_login(): return redirect(url_for("home"))
    c = empresas.get(company_id)
    if not c: abort(404)

    if request.method == "POST":
        # agregar al carrito un ítem específico
        idx = int(request.form.get("item_index", "-1"))
        if 0 <= idx < len(c.get("items", [])):
            it = c["items"][idx]
            entry = {
                "company_id": company_id,
                "company_name": c["name"],
                "role": c["role"],
                "rubro": it.get("rubro"),
                "type": it.get("type"),
                "product": it.get("product"),
                "variety": it.get("variety"),
                "quantity": request.form.get("quantity", it.get("quantity")),
                "unit": request.form.get("unit", it.get("unit")),
                "price": it.get("price"),
                "notes": request.form.get("notes", "")
            }
            cart = session.setdefault("cart", [])
            cart.append(entry)
            session["cart"] = cart
            flash(_("item_added"))
            return redirect(url_for("cart"))

    return render_template("detalle.html", company=c, UNITS=UNITS)

@app.route("/cart", methods=["GET", "POST"])
def cart():
    if not require_login(): return redirect(url_for("home"))
    if request.method == "POST":
        action = request.form.get("action")
        if action == "clear":
            session["cart"] = []
            flash(_("cart_cleared"))
        elif action and action.startswith("remove:"):
            idx = int(action.split(":")[1])
            cart = session.get("cart", [])
            if 0 <= idx < len(cart):
                cart.pop(idx)
                session["cart"] = cart
                flash(_("item_removed"))
        elif action == "checkout":
            session["cart"] = []
            flash(_("request_sent"))
            return redirect(url_for("dashboard"))
    return render_template("cart.html", cart=session.get("cart", []), UNITS=UNITS)

@app.route("/mi-perfil", methods=["GET", "POST"])
def mi_perfil():
    if not require_login(): return redirect(url_for("home"))
    company_id = session["company_id"]
    c = empresas.get(company_id)
    if not c: abort(404)

    if request.method == "POST":
        form_action = request.form.get("form_action", "")
        if form_action == "save_company":
            c["name"] = request.form.get("name", c["name"])
            c["city"] = request.form.get("city", c.get("city", ""))
            c["country"] = request.form.get("country", c.get("country", ""))
            c["phone"] = request.form.get("phone", c.get("phone", ""))
            c["email"] = request.form.get("email", c.get("email", ""))
            flash(_("changes_saved"))
            return redirect(url_for("mi_perfil"))

        if form_action == "add_item":
            new_item = {
                "type": request.form.get("type", "venta"),  # venta/compra
                "rubro": request.form.get("rubro", "fruta"), # fruta/servicio
                "product": request.form.get("product", "").strip(),
                "variety": request.form.get("variety", "").strip(),
                "quantity": request.form.get("quantity", "").strip(),
                "unit": request.form.get("unit", "tons"),
                "price": request.form.get("price", "").strip(),
                "details": request.form.get("details", "").strip()
            }
            c.setdefault("items", []).append(new_item)
            flash(_("changes_saved"))
            return redirect(url_for("mi_perfil"))

        if form_action.startswith("delete_item:"):
            idx = int(form_action.split(":")[1])
            items = c.get("items", [])
            if 0 <= idx < len(items):
                items.pop(idx)
                c["items"] = items
                flash(_("changes_saved"))
            return redirect(url_for("mi_perfil"))

    return render_template("mi_perfil.html", company=c, UNITS=UNITS)

# =========================
# Errores
# =========================
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="Not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message="Internal server error"), 500

# =========================
# Entrypoint
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
