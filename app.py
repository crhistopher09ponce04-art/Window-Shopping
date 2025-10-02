# app.py - Versión completa y estable para demo
import os
from flask import (
    Flask, render_template, request, redirect, url_for, session, abort, flash
)
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

# ---------------------------
# Traducción simple (ES, EN, ZH)
# ---------------------------
SUPPORTED_LANGS = ["es", "en", "zh"]
DEFAULT_LANG = "es"

def get_lang():
    return session.get("lang", DEFAULT_LANG)

def t(es_text, en_text=None, zh_text=None):
    """Helper de traducción. Si falta en inglés, devuelve el español por defecto."""
    lang = get_lang()
    if lang == "en":
        return en_text or es_text
    if lang == "zh":
        return zh_text or en_text or es_text
    return es_text

# Inyectar utilidades en templates para no pasar t=t cada vez
@app.context_processor
def inject_helpers():
    return {
        "t": t,
        "session": session
    }

# ---------------------------
# Datos demo: usuarios, perfiles y empresas
# ---------------------------
USERS = {
    # username: {password, rol, perfil_tipo, pais, rut (opcional)}
    "productor1": {"password": "1234", "rol": "Productor", "perfil_tipo": "compra_venta", "pais": "CL", "rut": "76.123.456-7"},
    "planta1": {"password": "1234", "rol": "Planta", "perfil_tipo": "compra_venta", "pais": "CL", "rut": "77.111.222-3"},
    "packing1": {"password": "1234", "rol": "Packing", "perfil_tipo": "servicios", "pais": "CL", "rut": "78.222.333-4"},
    "frigorifico1": {"password": "1234", "rol": "Frigorífico", "perfil_tipo": "servicios", "pais": "CL", "rut": "79.333.444-5"},
    "exportador1": {"password": "1234", "rol": "Exportador", "perfil_tipo": "compra_venta", "pais": "CL", "rut": "80.444.555-6"},
    "cliente_ex1": {"password": "1234", "rol": "Cliente extranjero", "perfil_tipo": "compra_venta", "pais": "US"},
    "transporte1": {"password": "1234", "rol": "Transporte", "perfil_tipo": "servicios", "pais": "CL", "rut": "81.555.666-7"},
    "aduana1": {"password": "1234", "rol": "Agencia de Aduanas", "perfil_tipo": "servicios", "pais": "CL", "rut": "82.666.777-8"},
    "extraport1": {"password": "1234", "rol": "Extraportuario", "perfil_tipo": "servicios", "pais": "CL", "rut": "83.777.888-9"},
}

# Perfiles públicos (empresa / contacto / items)
USER_PROFILES = {
    "productor1": {
        "empresa": "Agro Andes SPA",
        "rut": "76.123.456-7",
        "rol": "Productor",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "breve": "Uva de mesa y arándanos - cosecha premium.",
        "descripcion": "Productores especializados en uva Crimson y arándanos orgánicos.",
        "email": "ventas@agroandes.cl",
        "telefono": "+56 9 6000 0001",
        "direccion": "Ruta 5, km 72, IV Región",
        "slug": "agro-andes",
        "items": [
            {"tipo": "oferta", "producto": "Uva Crimson", "cantidad": "80 pallets", "origen": "IV Región", "precio": "A convenir"},
            {"tipo": "oferta", "producto": "Arándanos", "cantidad": "30 pallets", "origen": "X Región", "precio": "USD 1.10/kg"},
        ],
    },
    "planta1": {
        "empresa": "Planta Norte Ltda.",
        "rut": "77.111.222-3",
        "rol": "Planta",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "breve": "Recepción, clasificación y expedición.",
        "descripcion": "Planta con trazabilidad y control fitosanitario.",
        "email": "contacto@plantanorte.cl",
        "telefono": "+56 9 6000 0002",
        "direccion": "Zona Industrial, V Región",
        "slug": "planta-norte",
        "items": [
            {"tipo": "demanda", "producto": "Cajas plásticas", "cantidad": "20.000 und", "origen": "CL", "precio": "Oferta"},
        ],
    },
    "packing1": {
        "empresa": "PackSmart",
        "rut": "78.222.333-4",
        "rol": "Packing",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "breve": "Servicios de packing fruta fresca.",
        "descripcion": "Embalaje exportación y etiquetado con capacidad alta.",
        "email": "info@packsmart.cl",
        "telefono": "+56 9 6000 0003",
        "direccion": "R.M., Parque Industrial",
        "slug": "pack-smart",
        "items": [
            {"tipo": "servicio", "servicio": "Embalaje exportación", "capacidad": "30.000 cajas/día", "ubicacion": "R.M."},
        ],
    },
    "frigorifico1": {
        "empresa": "FríoPoint Ltda.",
        "rut": "79.333.444-5",
        "rol": "Frigorífico",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "breve": "Frío y logística en Valparaíso.",
        "descripcion": "Almacenaje en frío, preenfriado y despacho internacional.",
        "email": "logistica@friopoint.cl",
        "telefono": "+56 32 444 5555",
        "direccion": "Puerto Central, Valparaíso",
        "slug": "friopoint",
        "items": [
            {"tipo": "servicio", "servicio": "Almacenaje en frío", "capacidad": "1.200 pallets", "ubicacion": "Valparaíso"},
            {"tipo": "servicio", "servicio": "Preenfriado", "capacidad": "8 túneles", "ubicacion": "Valparaíso"},
        ],
    },
    "exportador1": {
        "empresa": "OCExport",
        "rut": "80.444.555-6",
        "rol": "Exportador",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "breve": "Exportación multiproducto con clientes en Europa.",
        "descripcion": "Exportador con logística completa y acuerdos en UE.",
        "email": "export@ocexport.cl",
        "telefono": "+56 9 6000 0004",
        "direccion": "Av. Exportadores 45, Santiago",
        "slug": "ocexport",
        "items": [
            {"tipo": "demanda", "producto": "Cerezas", "cantidad": "150 pallets", "origen": "VI-VII", "precio": "A convenir"},
        ],
    },
    "cliente_ex1": {
        "empresa": "GlobalBuyer Co.",
        "rut": None,
        "rol": "Cliente extranjero",
        "perfil_tipo": "compra_venta",
        "pais": "US",
        "breve": "Comprador mayorista en EEUU.",
        "descripcion": "Interés en uva y arándanos para mercado retail.",
        "email": "contact@globalbuyer.com",
        "telefono": "+1 555 0100",
        "direccion": "Miami, USA",
        "slug": "globalbuyer",
        "items": [
            {"tipo": "demanda", "producto": "Uva Thompson", "cantidad": "400 pallets", "origen": "CL", "precio": "A convenir"},
        ],
    },
    "transporte1": {
        "empresa": "Translog Demo",
        "rut": "81.555.666-7",
        "rol": "Transporte",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "breve": "Servicios de transporte terrestre y consolidado.",
        "descripcion": "Flota refrigerada y trazabilidad por GPS.",
        "email": "log@translog.cl",
        "telefono": "+56 9 6000 0005",
        "direccion": "Ruta 68, Santiago",
        "slug": "translog",
        "items": [
            {"tipo": "servicio", "servicio": "Transporte refrigerado", "capacidad": "50 camiones", "ubicacion": "Nacional"},
        ],
    },
    "aduana1": {
        "empresa": "AduanasPro",
        "rut": "82.666.777-8",
        "rol": "Agencia de Aduanas",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "breve": "Gestión aduanera y documentación export.",
        "descripcion": "Agentes con experiencia en mercados asiáticos.",
        "email": "aduana@aduanaspro.cl",
        "telefono": "+56 9 6000 0006",
        "direccion": "Santiago Centro",
        "slug": "aduanaspro",
        "items": [
            {"tipo": "servicio", "servicio": "Gestión aduanera", "capacidad": "100 trámites/día", "ubicacion": "Santiago"},
        ],
    },
    "extraport1": {
        "empresa": "ExtraPort Services",
        "rut": "83.777.888-9",
        "rol": "Extraportuario",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "breve": "Operaciones portuarias y almacenaje.",
        "descripcion": "Soporte en patio y despacho internacional.",
        "email": "contacto@extraport.cl",
        "telefono": "+56 9 6000 0007",
        "direccion": "Zona Portuaria",
        "slug": "extraport",
        "items": [
            {"tipo": "servicio", "servicio": "Gestión portuaria", "capacidad": "Plataforma 5.000 m2", "ubicacion": "Valparaíso"},
        ],
    },
}

# Build a quick slug->profile mapping for empresa route compatibility
def all_companies_list():
    # Convert USER_PROFILES values to a list like COMPANIES used in templates
    out = []
    for key, prof in USER_PROFILES.items():
        comp = {
            "slug": prof.get("slug") or key,
            "nombre": prof.get("empresa"),
            "rol": prof.get("rol"),
            "perfil_tipo": prof.get("perfil_tipo"),
            "pais": prof.get("pais"),
            "breve": prof.get("breve"),
            "items": prof.get("items", []),
            # include contact fields for templates that use them
            "email": prof.get("email"),
            "telefono": prof.get("telefono"),
            "rut": prof.get("rut"),
            "descripcion": prof.get("descripcion")
        }
        out.append(comp)
    return out

# ---------------------------
# Carrito (sesión)
# ---------------------------
def get_cart():
    return session.setdefault("cart", [])

def add_to_cart(item):
    cart = get_cart()
    cart.append(item)
    session["cart"] = cart

def clear_cart():
    session["cart"] = []

# ---------------------------
# Helpers / middlewares
# ---------------------------
def login_required(redirect_to_login=True):
    if "usuario" not in session:
        if redirect_to_login:
            return redirect(url_for("login"))
        return False
    return True

# ---------------------------
# RUT / small util (opcionales)
# ---------------------------
def normalize_slug(s):
    return s.lower().replace(" ", "-")

# ---------------------------
# Rutas
# ---------------------------
@app.route("/")
def home():
    # landing page
    return render_template("landing.html")

@app.route("/set_lang/<lang>")
def set_lang(lang):
    if lang not in SUPPORTED_LANGS:
        lang = DEFAULT_LANG
    session["lang"] = lang
    return redirect(request.referrer or url_for("home"))

# ----- Login / logout -----
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = USERS.get(username)
        if user and user.get("password") == password:
            session["usuario"] = username
            # set last seen defaults if missing profile
            if username not in USER_PROFILES:
                USER_PROFILES[username] = {
                    "empresa": username.capitalize(),
                    "rut": None,
                    "rol": user.get("rol"),
                    "perfil_tipo": user.get("perfil_tipo"),
                    "pais": user.get("pais"),
                    "breve": "",
                    "descripcion": "",
                    "email": f"{username}@demo.local",
                    "telefono": "",
                    "direccion": "",
                    "slug": username,
                    "items": []
                }
            flash(t("Ingreso exitoso.", "Login successful."))
            return redirect(url_for("dashboard"))
        else:
            error = t("Usuario o clave inválidos.", "Invalid user or password.")
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ----- Registro -----
@app.route("/register_router")
def register_router():
    return render_template("register_router.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    # defaults if querystring sent from router
    nacionalidad = request.args.get("nac")
    perfil_tipo = request.args.get("tipo")
    roles_cv = ["Productor", "Planta", "Packing", "Frigorífico", "Exportador", "Cliente extranjero"]
    roles_srv = ["Packing", "Frigorífico", "Transporte", "Agencia de Aduanas", "Extraportuario"]

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        pais = request.form.get("pais", "").strip() or "CL"
        rol = request.form.get("rol", "").strip()
        perfil_tipo = request.form.get("perfil_tipo", "").strip()
        rut = request.form.get("rut") or None
        email = request.form.get("email") or f"{username}@demo.local"
        telefono = request.form.get("phone") or ""
        direccion = request.form.get("address") or ""
        nac = request.form.get("nacionalidad") or "nacional"

        if not username or not password or not rol or not perfil_tipo:
            error = t("Completa los campos obligatorios.", "Please complete required fields.")
        elif username in USERS:
            error = t("El usuario ya existe.", "User already exists.")
        else:
            USERS[username] = {
                "password": password,
                "rol": rol,
                "perfil_tipo": perfil_tipo,
                "pais": pais,
                "rut": rut
            }
            # crear perfil público básico
            USER_PROFILES[username] = {
                "empresa": username.capitalize(),
                "rut": rut,
                "rol": rol,
                "perfil_tipo": perfil_tipo,
                "pais": pais,
                "breve": "",
                "descripcion": "",
                "email": email,
                "telefono": telefono,
                "direccion": direccion,
                "slug": normalize_slug(username),
                "items": []
            }
            session["usuario"] = username
            flash(t("Cuenta creada. Bienvenido/a", "Account created. Welcome!"))
            return redirect(url_for("dashboard"))

    return render_template(
        "register.html",
        error=error,
        nacionalidad=nacionalidad,
        perfil_tipo=perfil_tipo,
        roles_cv=roles_cv,
        roles_srv=roles_srv
    )

# ----- Dashboard -----
@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))
    usuario = session["usuario"]
    user_meta = USERS.get(usuario, {})
    perfil = USER_PROFILES.get(usuario, {})
    cart = get_cart()
    # determine profile type & rol for dashboard links
    perfil_tipo = user_meta.get("perfil_tipo") or perfil.get("perfil_tipo") or "compra_venta"
    rol = user_meta.get("rol") or perfil.get("rol") or "-"
    my_company = perfil
    return render_template(
        "dashboard.html",
        usuario=usuario,
        rol=rol,
        perfil_tipo=perfil_tipo,
        my_company=my_company,
        cart=cart
    )

# ----- Accesos (lista tipo resumen) -----
@app.route("/accesos/<tipo>")
def accesos(tipo):
    tipo = tipo.lower()
    if tipo not in ["ventas", "compras", "servicios"]:
        abort(404)
    # Map: ventas/compras come from perfil_tipo compra_venta; servicios from servicios
    if tipo == "servicios":
        data = [c for c in all_companies_list() if c["perfil_tipo"] == "servicios"]
    else:
        data = [c for c in all_companies_list() if c["perfil_tipo"] == "compra_venta"]
    return render_template("accesos.html", tipo=tipo, data=data)

# ----- Detalles (tablas detalladas) -----
@app.route("/detalles/<tipo>")
def detalles(tipo):
    tipo = tipo.lower()
    if tipo not in ["ventas", "compras", "servicios"]:
        abort(404)
    # Build data to match templates (list of company dicts)
    companies = all_companies_list()
    # Filter companies that actually have relevant items
    data = []
    for c in companies:
        has = False
        for it in c.get("items", []):
            if tipo == "ventas" and it.get("tipo") == "oferta":
                has = True
            if tipo == "compras" and it.get("tipo") == "demanda":
                has = True
            if tipo == "servicios" and it.get("tipo") == "servicio":
                has = True
        if has:
            data.append(c)
    # render correspondiente a detalle_ventas/compras/servicios
    template_map = {
        "ventas": "detalle_ventas.html",
        "compras": "detalle_compras.html",
        "servicios": "detalle_servicios.html"
    }
    return render_template(template_map[tipo], data=data)

# ----- Perfil público de empresa / perfil propio -----
@app.route("/empresa/<slug>")
def empresa(slug):
    # buscar en USER_PROFILES por slug o por username
    prof = None
    # first search by slug value
    for username, p in USER_PROFILES.items():
        if p.get("slug") == slug or username == slug:
            prof = p
            break
    if not prof:
        # maybe slug matches 'agro-andes' style created above in data; check all_companies_list
        for c in all_companies_list():
            if c["slug"] == slug:
                # map back to a minimal profile structure to templates
                prof = {
                    "empresa": c["nombre"],
                    "rut": c.get("rut"),
                    "rol": c.get("rol"),
                    "perfil_tipo": c.get("perfil_tipo"),
                    "pais": c.get("pais"),
                    "breve": c.get("breve"),
                    "descripcion": c.get("descripcion"),
                    "email": c.get("email"),
                    "telefono": c.get("telefono"),
                    "direccion": c.get("direccion"),
                    "slug": c.get("slug"),
                    "items": c.get("items", [])
                }
                break
    if not prof:
        abort(404)
    # Determine if this is the logged user's profile
    es_user = session.get("usuario") and session.get("usuario") in USER_PROFILES and USER_PROFILES[session["usuario"]].get("slug") == prof.get("slug")
    return render_template("empresa.html", comp=prof, es_user=es_user)

# ----- Añadir al carrito (form POST en templates usa cart_add) -----
@app.route("/cart_add", methods=["POST"])
def cart_add():
    # expect hidden inputs: empresa, producto/servicio, tipo
    empresa = request.form.get("empresa") or "Empresa desconocida"
    tipo = request.form.get("tipo") or ""
    producto = request.form.get("producto")
    servicio = request.form.get("servicio")
    item = {"empresa": empresa, "tipo": tipo}
    if producto:
        item["producto"] = producto
    if servicio:
        item["servicio"] = servicio
    add_to_cart(item)
    flash(t("Ítem agregado al carrito.", "Item added to cart."))
    return redirect(request.referrer or url_for("dashboard"))

# ----- Carrito (visualizar) -----
@app.route("/carrito")
def carrito():
    cart = get_cart()
    return render_template("carrito.html", cart=cart)

# ----- Ayuda / centro de contacto (simple) -----
@app.route("/ayuda", methods=["GET", "POST"])
def ayuda():
    mensaje = None
    if request.method == "POST":
        correo = request.form.get("correo")
        msg = request.form.get("mensaje")
        # Aquí sólo simulamos el envío. En producción guardar o enviar email.
        mensaje = t("Gracias, su mensaje fue recibido. Le responderemos pronto.",
                    "Thank you, your message was received. We'll reply soon.")
        flash(mensaje)
        return redirect(url_for("dashboard"))
    return render_template("ayuda.html", mensaje=mensaje)

# ----- Perfil privado (edición simple) -----
@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    if "usuario" not in session:
        return redirect(url_for("login"))
    username = session["usuario"]
    prof = USER_PROFILES.get(username)
    if not prof:
        abort(404)
    mensaje = None
    if request.method == "POST":
        action = request.form.get("action")
        if action == "save_profile":
            prof["empresa"] = request.form.get("empresa", prof["empresa"])
            prof["email"] = request.form.get("email", prof.get("email", ""))
            prof["telefono"] = request.form.get("telefono", prof.get("telefono", ""))
            prof["direccion"] = request.form.get("direccion", prof.get("direccion", ""))
            prof["descripcion"] = request.form.get("descripcion", prof.get("descripcion", ""))
            mensaje = t("Perfil actualizado.", "Profile updated.")
            flash(mensaje)
        elif action == "add_item":
            perfil_tipo = prof.get("perfil_tipo")
            if perfil_tipo == "servicios":
                servicio = request.form.get("servicio", "").strip()
                capacidad = request.form.get("capacidad", "").strip()
                ubicacion = request.form.get("ubicacion", "").strip()
                if servicio:
                    prof["items"].append({"tipo": "servicio", "servicio": servicio, "capacidad": capacidad, "ubicacion": ubicacion})
                    mensaje = t("Servicio agregado.", "Service added.")
                    flash(mensaje)
            else:
                subtipo = request.form.get("subtipo", "oferta")
                producto = request.form.get("producto", "").strip()
                cantidad = request.form.get("cantidad", "").strip()
                origen = request.form.get("origen", "").strip()
                precio = request.form.get("precio", "").strip()
                if producto:
                    prof["items"].append({"tipo": subtipo, "producto": producto, "cantidad": cantidad, "origen": origen, "precio": precio})
                    mensaje = t("Ítem agregado.", "Item added.")
                    flash(mensaje)
        return redirect(url_for("perfil"))
    return render_template("perfil.html", perfil=prof, mensaje=mensaje)

# ----- Error handlers -----
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message=t("No encontrado", "Not found")), 404

@app.errorhandler(HTTPException)
def handle_http(e):
    # Generic HTTP exceptions (400, 401, ...)
    return render_template("error.html", code=e.code or 500, message=e.description or t("Error", "Error")), e.code or 500

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message=t("Error interno", "Internal server error")), 500

# ----- Run local -----
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
