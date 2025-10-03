# app.py
import os
import uuid
from datetime import timedelta
from werkzeug.utils import secure_filename
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, abort, flash, send_from_directory
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")
app.permanent_session_lifetime = timedelta(days=14)

# =========================================================
# Config de uploads (RUT, documentos extranjeros)
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXT = {"pdf", "png", "jpg", "jpeg"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

# =========================================================
# i18n simple
# =========================================================
def t(es, en, zh=None):
    """Traductor mínimo por sesión."""
    lang = session.get("lang", "es")
    if lang == "en":
        return en
    if lang == "zh" and zh:
        return zh
    return es

@app.context_processor
def inject_globals():
    """Inyecta 't' y banderas de idioma en TODAS las plantillas (incluidas de error)."""
    return dict(
        t=t,
        LANGS=[("es", "ES"), ("en", "EN"), ("zh", "中文")]
    )

@app.route("/set_lang/<lang>")
@app.route("/lang/<lang>")
def set_lang(lang):
    session["lang"] = lang if lang in ("es", "en", "zh") else "es"
    return redirect(request.referrer or url_for("home"))

# =========================================================
# Datos DEMO (Usuarios / Perfiles / Empresas públicas)
# =========================================================
USERS = {
    # Compra/Venta
    "frutera@demo.cl":     {"password": "1234", "rol": "Productor",          "perfil_tipo": "compra_venta", "pais": "CL"},
    "planta@demo.cl":      {"password": "1234", "rol": "Planta",              "perfil_tipo": "compra_venta", "pais": "CL"},
    "exportador@demo.cl":  {"password": "1234", "rol": "Exportador",          "perfil_tipo": "compra_venta", "pais": "CL"},
    "cliente@usa.com":     {"password": "1234", "rol": "Cliente extranjero",  "perfil_tipo": "compra_venta", "pais": "US"},
    # Servicios
    "packing@demo.cl":     {"password": "1234", "rol": "Packing",             "perfil_tipo": "servicios",    "pais": "CL"},
    "frigorifico@demo.cl": {"password": "1234", "rol": "Frigorífico",         "perfil_tipo": "servicios",    "pais": "CL"},
    "transporte@demo.cl":  {"password": "1234", "rol": "Transporte",          "perfil_tipo": "servicios",    "pais": "CL"},
    "aduana@demo.cl":      {"password": "1234", "rol": "Agencia de Aduanas",  "perfil_tipo": "servicios",    "pais": "CL"},
    "extraport@demo.cl":   {"password": "1234", "rol": "Extraportuario",      "perfil_tipo": "servicios",    "pais": "CL"},
}

USER_PROFILES = {
    "frutera@demo.cl": {
        "empresa": "Agro El Valle SPA",
        "rut": "76.123.456-7",
        "rut_file": None,  # archivo adjunto RUT (opcional)
        "rol": "Productor",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "email": "ventas@agrovalle.cl",
        "telefono": "+56 9 6000 0001",
        "direccion": "Parcela 21, Vicuña",
        "descripcion": "Productores de uva de mesa, ciruela y arándano.",
        "items": [
            {"tipo": "oferta", "producto": "Uva Crimson",   "cantidad": "120 pallets", "origen": "IV Región", "precio": "A convenir"},
            {"tipo": "oferta", "producto": "Ciruela D’Agen", "cantidad": "80 pallets",  "origen": "VI Región", "precio": "USD 12/caja"},
        ],
        # IDs extranjeros (no aplica)
        "usci": None, "eori": None, "tax_id": None, "otros_id": None
    },
    "planta@demo.cl": {
        "empresa": "Planta Los Nogales",
        "rut": "77.200.111-9",
        "rut_file": None,
        "rol": "Planta",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "email": "contacto@nogales.cl",
        "telefono": "+56 9 6000 0010",
        "direccion": "Km 5 Camino Interior, Rengo",
        "descripcion": "Recepción y proceso de fruta fresca.",
        "items": [
            {"tipo": "demanda", "producto": "Cajas plásticas 10kg", "cantidad": "20.000 und", "origen": "CL", "precio": "Ofertar"},
        ],
        "usci": None, "eori": None, "tax_id": None, "otros_id": None
    },
    "exportador@demo.cl": {
        "empresa": "OCExport Chile",
        "rut": "78.345.678-9",
        "rut_file": None,
        "rol": "Exportador",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "email": "export@ocexport.cl",
        "telefono": "+56 2 2345 6789",
        "direccion": "Av. Apoquindo 1234, Las Condes",
        "descripcion": "Exportador multiproducto a EEUU/EU/Asia.",
        "items": [
            {"tipo": "demanda", "producto": "Cereza Santina", "cantidad": "150 pallets", "origen": "VI-VII", "precio": "A convenir"},
        ],
        "usci": None, "eori": None, "tax_id": None, "otros_id": None
    },
    "cliente@usa.com": {
        "empresa": "GlobalBuyer Co.",
        "rut": None, "rut_file": None,
        "rol": "Cliente extranjero",
        "perfil_tipo": "compra_venta",
        "pais": "US",
        "email": "contact@globalbuyer.com",
        "telefono": "+1 305 555 0100",
        "direccion": "Miami, FL",
        "descripcion": "Mayorista importador en EEUU.",
        "items": [
            {"tipo": "demanda", "producto": "Uva Thompson", "cantidad": "400 pallets", "origen": "CL", "precio": "A convenir"},
        ],
        # IDs extranjeros
        "usci": "US-9988-XY",
        "eori": None,
        "tax_id": "99-1234567",
        "otros_id": None
    },
    "packing@demo.cl": {
        "empresa": "PackSmart S.A.",
        "rut": "79.456.789-0", "rut_file": None,
        "rol": "Packing",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "email": "info@packsmart.cl",
        "telefono": "+56 9 6000 0002",
        "direccion": "Ruta 5 km 185, Rancagua",
        "descripcion": "Servicios de packing, etiquetado y QA.",
        "items": [
            {"tipo": "servicio", "servicio": "Embalaje exportación", "capacidad": "30.000 cajas/día", "ubicacion": "Rancagua"},
            {"tipo": "oferta",   "producto": "Ciruela Angeleno",     "cantidad": "60 pallets",        "origen": "R.M.", "precio": "USD 10/caja"},
        ],
        "usci": None, "eori": None, "tax_id": None, "otros_id": None
    },
    "frigorifico@demo.cl": {
        "empresa": "FríoPoint Ltda.",
        "rut": "80.567.890-1", "rut_file": None,
        "rol": "Frigorífico",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "email": "contacto@friopoint.cl",
        "telefono": "+56 32 444 5555",
        "direccion": "Puerto Central, Valparaíso",
        "descripcion": "Almacenaje en frío y logística de puerto.",
        "items": [
            {"tipo": "servicio", "servicio": "Almacenaje en frío", "capacidad": "1.500 pallets", "ubicacion": "Valparaíso"},
            {"tipo": "servicio", "servicio": "Preenfriado",        "capacidad": "6 túneles",     "ubicacion": "Valparaíso"},
            {"tipo": "oferta",   "producto": "Uva Red Globe",      "cantidad": "40 pallets",     "origen": "V Región",  "precio": "USD 9/caja"},
        ],
        "usci": None, "eori": None, "tax_id": None, "otros_id": None
    },
    "transporte@demo.cl": {
        "empresa": "TransVeloz",
        "rut": "81.222.333-4", "rut_file": None,
        "rol": "Transporte",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "email": "operaciones@transveloz.cl",
        "telefono": "+56 9 5000 1111",
        "direccion": "San Bernardo, RM",
        "descripcion": "Transporte nacional refrigerado.",
        "items": [
            {"tipo": "servicio", "servicio": "Transporte reefer", "capacidad": "35 camiones", "ubicacion": "RM"},
        ],
        "usci": None, "eori": None, "tax_id": None, "otros_id": None
    },
    "aduana@demo.cl": {
        "empresa": "AduanasFast",
        "rut": "82.555.666-7", "rut_file": None,
        "rol": "Agencia de Aduanas",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "email": "agencia@aduanasfast.cl",
        "telefono": "+56 2 2987 6543",
        "direccion": "Valparaíso",
        "descripcion": "Tramitación aduanera y asesoría.",
        "items": [
            {"tipo": "servicio", "servicio": "Despacho exportación", "capacidad": "Alta", "ubicacion": "Valparaíso"},
        ],
        "usci": None, "eori": None, "tax_id": None, "otros_id": None
    },
    "extraport@demo.cl": {
        "empresa": "PortHelper",
        "rut": "83.777.888-9", "rut_file": None,
        "rol": "Extraportuario",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "email": "info@porthelper.cl",
        "telefono": "+56 9 7000 2222",
        "direccion": "San Antonio",
        "descripcion": "Servicios extraportuarios y contenedores.",
        "items": [
            {"tipo": "servicio", "servicio": "Consolidación de contenedores", "capacidad": "120/día", "ubicacion": "San Antonio"},
        ],
        "usci": None, "eori": None, "tax_id": None, "otros_id": None
    },
}

COMPANIES = [
    {
        "slug": "agro-el-valle",
        "nombre": "Agro El Valle SPA",
        "rut": "76.123.456-7",
        "rol": "Productor",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "breve": "Uva, ciruela y berries.",
        "email": "ventas@agrovalle.cl",
        "telefono": "+56 9 6000 0001",
        "direccion": "Parcela 21, Vicuña",
        "items": [
            {"tipo": "oferta", "producto": "Uva Crimson",    "cantidad": "120 pallets", "origen": "IV Región", "precio": "A convenir"},
            {"tipo": "oferta", "producto": "Ciruela D’Agen", "cantidad": "80 pallets",  "origen": "VI Región", "precio": "USD 12/caja"},
        ],
        "descripcion": "Productores de uva, ciruela y berries."
    },
    {
        "slug": "packsmart",
        "nombre": "PackSmart S.A.",
        "rut": "79.456.789-0",
        "rol": "Packing",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "breve": "Packing, QA y etiquetado.",
        "email": "info@packsmart.cl",
        "telefono": "+56 9 6000 0002",
        "direccion": "Ruta 5 km 185, Rancagua",
        "items": [
            {"tipo": "servicio", "servicio": "Embalaje exportación", "capacidad": "30.000 cajas/día", "ubicacion": "Rancagua"},
            {"tipo": "oferta",   "producto": "Ciruela Angeleno",     "cantidad": "60 pallets",        "origen": "R.M.", "precio": "USD 10/caja"},
        ],
        "descripcion": "Servicios de packing, QA y etiquetado."
    },
    {
        "slug": "friopoint",
        "nombre": "FríoPoint Ltda.",
        "rut": "80.567.890-1",
        "rol": "Frigorífico",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "breve": "Almacenaje y logística en Valparaíso.",
        "email": "contacto@friopoint.cl",
        "telefono": "+56 32 444 5555",
        "direccion": "Puerto Central, Valparaíso",
        "items": [
            {"tipo": "servicio", "servicio": "Almacenaje en frío", "capacidad": "1.500 pallets", "ubicacion": "Valparaíso"},
            {"tipo": "servicio", "servicio": "Preenfriado",        "capacidad": "6 túneles",     "ubicacion": "Valparaíso"},
            {"tipo": "oferta",   "producto": "Uva Red Globe",      "cantidad": "40 pallets",     "origen": "V Región",  "precio": "USD 9/caja"},
        ],
        "descripcion": "Frigorífico con logística en puerto."
    },
    {
        "slug": "ocexport",
        "nombre": "OCExport Chile",
        "rut": "78.345.678-9",
        "rol": "Exportador",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "breve": "Exportación multiproducto.",
        "email": "export@ocexport.cl",
        "telefono": "+56 2 2345 6789",
        "direccion": "Av. Apoquindo 1234, Las Condes",
        "items": [
            {"tipo": "demanda", "producto": "Cereza Santina", "cantidad": "150 pallets", "origen": "VI-VII", "precio": "A convenir"},
        ],
        "descripcion": "Exportador multiproducto."
    },
    {
        "slug": "transveloz",
        "nombre": "TransVeloz",
        "rut": "81.222.333-4",
        "rol": "Transporte",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "breve": "Transporte reefer nacional.",
        "email": "operaciones@transveloz.cl",
        "telefono": "+56 9 5000 1111",
        "direccion": "San Bernardo, RM",
        "items": [
            {"tipo": "servicio", "servicio": "Transporte reefer", "capacidad": "35 camiones", "ubicacion": "RM"},
        ],
        "descripcion": "Flota de transporte refrigerado."
    },
    {
        "slug": "aduanasfast",
        "nombre": "AduanasFast",
        "rut": "82.555.666-7",
        "rol": "Agencia de Aduanas",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "breve": "Tramitación aduanera.",
        "email": "agencia@aduanasfast.cl",
        "telefono": "+56 2 2987 6543",
        "direccion": "Valparaíso",
        "items": [
            {"tipo": "servicio", "servicio": "Despacho exportación", "capacidad": "Alta", "ubicacion": "Valparaíso"},
        ],
        "descripcion": "Agencia de aduanas."
    },
    {
        "slug": "porthelper",
        "nombre": "PortHelper",
        "rut": "83.777.888-9",
        "rol": "Extraportuario",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "breve": "Consolidación y extraportuario.",
        "email": "info@porthelper.cl",
        "telefono": "+56 9 7000 2222",
        "direccion": "San Antonio",
        "items": [
            {"tipo": "servicio", "servicio": "Consolidación de contenedores", "capacidad": "120/día", "ubicacion": "San Antonio"},
        ],
        "descripcion": "Servicios extraportuarios."
    },
]

# =========================================================
# WRAPPER para evitar conflicto Jinja: dict.items (método) vs campo 'items' (lista)
# =========================================================
class ViewObj:
    """Convierte un dict en objeto con atributos. Asegura que .items sea la LISTA de ítems."""
    def __init__(self, data: dict):
        for k, v in data.items():
            setattr(self, k, v)
        # Garantiza que 'items' sea una lista (si existe)
        if hasattr(self, "items") and not isinstance(getattr(self, "items"), list):
            # Si por alguna razón viene como método/otro, intenta tomar del dict original
            real_list = data.get("items", [])
            setattr(self, "items", real_list)

def wrap_list(dict_list):
    return [ViewObj(d) for d in dict_list]

# =========================================================
# Helpers de sesión / carrito
# =========================================================
def is_logged():
    return "user" in session

def current_user_profile():
    u = session.get("user")
    prof = USER_PROFILES.get(u)
    return prof

def get_cart():
    return session.setdefault("cart", [])

def add_to_cart(item_dict):
    cart = get_cart()
    cart.append(item_dict)
    session["cart"] = cart

def clear_cart():
    session["cart"] = []

def remove_from_cart(index):
    cart = get_cart()
    try:
        idx = int(index)
        if 0 <= idx < len(cart):
            cart.pop(idx)
            session["cart"] = cart
            return True
    except Exception:
        pass
    return False

# =========================================================
# Rutas
# =========================================================
@app.route("/")
def home():
    return render_template("landing.html")

@app.route("/favicon.ico")
def favicon():
    return ("", 204)

# ---------- Auth ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        user = request.form.get("username", "").strip().lower()
        pwd = request.form.get("password", "").strip()
        udata = USERS.get(user)
        if udata and udata["password"] == pwd:
            session["user"] = user
            session["usuario"] = user
            flash(t("Bienvenido/a", "Welcome", "歡迎"))
            return redirect(url_for("dashboard"))
        error = t("Credenciales inválidas", "Invalid credentials", "帳密錯誤")
    return render_template("login.html", error=error)

@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    """Recuperar contraseña (dummy)."""
    msg = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        if email in USERS:
            flash(t("Te enviamos un enlace de recuperación (demo).", "We sent a recovery link (demo)."))
            return redirect(url_for("login"))
        else:
            msg = t("Correo no registrado.", "Email not found.")
    return render_template("forgot.html", mensaje=msg)

@app.route("/reset/<token>", methods=["GET", "POST"])
def reset(token):
    """Reset de contraseña (demo)."""
    info = t("Token de demostración recibido.", "Demo token received.")
    if request.method == "POST":
        newp = request.form.get("password", "").strip()
        if newp:
            flash(t("Contraseña actualizada (demo).", "Password updated (demo)."))
            return redirect(url_for("login"))
    return render_template("reset.html", info=info)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ---------- Registro (Router + Form con nacional/extranjero) ----------
@app.route("/register_router")
def register_router():
    return render_template("register_router.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    nacionalidad = request.args.get("nac")      # 'nacional' | 'extranjero'
    perfil_tipo  = request.args.get("tipo")     # 'compra_venta' | 'servicios'

    NACIONALIDAD_OPCIONES = ["nacional", "extranjero"]
    PERFIL_OPCIONES = ["compra_venta", "servicios"]
    ROLES_COMPRA_VENTA = ["Productor", "Planta", "Packing", "Frigorífico", "Exportador", "Cliente extranjero"]
    ROLES_SERVICIOS    = ["Packing", "Frigorífico", "Transporte", "Agencia de Aduanas", "Extraportuario"]

    if request.method == "POST":
        nacionalidad = request.form.get("nacionalidad") or nacionalidad or "nacional"
        perfil_tipo  = request.form.get("perfil_tipo")  or perfil_tipo  or "compra_venta"

        # Reglas de selección:
        if nacionalidad == "extranjero":
            # Forzar compra_venta + rol Cliente extranjero
            perfil_tipo = "compra_venta"

        username = (request.form.get("username", "") or "").strip().lower()
        password = (request.form.get("password", "") or "").strip()
        email    = (request.form.get("email", "") or "").strip()
        telefono = (request.form.get("phone", "") or "").strip()
        direccion= (request.form.get("address", "") or "").strip()
        pais     = (request.form.get("pais", "") or "").strip()
        rol      = (request.form.get("rol", "") or "").strip()

        # Documentos / IDs
        rut      = (request.form.get("rut", "") or "").strip() if nacionalidad == "nacional" else None
        usci     = (request.form.get("usci", "") or "").strip() if nacionalidad == "extranjero" else None
        eori     = (request.form.get("eori", "") or "").strip() if nacionalidad == "extranjero" else None
        tax_id   = (request.form.get("tax_id", "") or "").strip() if nacionalidad == "extranjero" else None
        otros_id = (request.form.get("otros_id", "") or "").strip() if nacionalidad == "extranjero" else None

        # Archivo RUT (solo nacional)
        rut_file_path = None
        if nacionalidad == "nacional" and "rut_file" in request.files:
            f = request.files["rut_file"]
            if f and f.filename and allowed_file(f.filename):
                fname = secure_filename(f.filename)
                # Evita colisiones
                fname = f"{uuid.uuid4().hex}_{fname}"
                f.save(os.path.join(UPLOAD_FOLDER, fname))
                rut_file_path = f"uploads/{fname}"

        if not pais:
            pais = "CL" if nacionalidad == "nacional" else "US"

        if not username or not password or not perfil_tipo or not nacionalidad:
            error = t("Completa los campos obligatorios.", "Please complete required fields.")
        elif perfil_tipo not in PERFIL_OPCIONES:
            error = t("Tipo de perfil inválido.", "Invalid profile type.")
        elif nacionalidad not in NACIONALIDAD_OPCIONES:
            error = t("Nacionalidad inválida.", "Invalid nationality.")
        elif username in USERS:
            error = t("El usuario ya existe.", "User already exists.")
        else:
            # Reglas de rol según nacionalidad/tipo
            if nacionalidad == "extranjero":
                rol = "Cliente extranjero"
            else:
                # Si es nacional y compra_venta, NO permitir "Cliente extranjero"
                if perfil_tipo == "compra_venta" and rol == "Cliente extranjero":
                    error = t("Rol inválido para perfil nacional.", "Invalid role for national profile.")
            if not error:
                USERS[username] = {
                    "password": password,
                    "rol": rol,
                    "perfil_tipo": perfil_tipo,
                    "pais": pais,
                }
                USER_PROFILES[username] = {
                    "empresa": username.split("@")[0].replace(".", " ").title(),
                    "rut": rut,
                    "rut_file": rut_file_path,
                    "rol": rol,
                    "perfil_tipo": perfil_tipo,
                    "pais": pais,
                    "email": email or username,
                    "telefono": telefono or "",
                    "direccion": direccion or "",
                    "descripcion": "Nuevo perfil.",
                    "items": [],
                    # IDs extranjeros
                    "usci": usci, "eori": eori, "tax_id": tax_id, "otros_id": otros_id
                }
                session["user"] = username
                session["usuario"] = username
                return redirect(url_for("dashboard"))

    return render_template(
        "register.html",
        error=error,
        nacionalidad=nacionalidad,
        perfil_tipo=perfil_tipo,
        nacionalidad_opciones=NACIONALIDAD_OPCIONES,
        perfil_opciones=PERFIL_OPCIONES,
        roles_cv=[r for r in ROLES_COMPRA_VENTA if r != "Cliente extranjero"],  # por defecto para nacionales
        roles_srv=ROLES_SERVICIOS,
        roles_all_cv=ROLES_COMPRA_VENTA  # por si lo necesitas
    )

# ---------- Dashboard ----------
@app.route("/dashboard")
def dashboard():
    if not is_logged():
        return redirect(url_for("login"))
    profile = current_user_profile()
    usuario = session.get("user")
    rol = USERS.get(usuario, {}).get("rol", "-")
    perfil_tipo = USERS.get(usuario, {}).get("perfil_tipo", "-")
    # wrap para que perfil.items sea lista en las plantillas
    my_company_view = ViewObj(profile) if profile else ViewObj({"items": []})
    return render_template(
        "dashboard.html",
        usuario=usuario,
        rol=rol,
        perfil_tipo=perfil_tipo,
        my_company=my_company_view,
        cart=get_cart(),
    )

# ---------- Accesos (listado simple) ----------
@app.route("/accesos/<tipo>")
def accesos(tipo):
    tipo = tipo.lower()
    if tipo not in ("ventas", "compras", "servicios"):
        abort(404)

    if tipo == "servicios":
        data = []
        for c in COMPANIES:
            if c["perfil_tipo"] == "servicios" or c["rol"] in ("Packing", "Frigorífico"):
                if any(it.get("tipo") == "servicio" for it in c.get("items", [])):
                    data.append(c)
    else:
        tag = "oferta" if tipo == "ventas" else "demanda"
        data = []
        for c in COMPANIES:
            if c["perfil_tipo"] == "compra_venta" or c["rol"] in ("Packing", "Frigorífico"):
                if any(it.get("tipo") == tag for it in c.get("items", [])):
                    data.append(c)

    return render_template("accesos.html", tipo=tipo, data=wrap_list(data))

# ---------- Detalles (tablas con botón Agregar) ----------
@app.route("/detalles/<tipo>")
def detalles(tipo):
    tipo = tipo.lower()
    if tipo not in ("ventas", "compras", "servicios"):
        abort(404)

    if tipo in ("ventas", "compras"):
        tag = "oferta" if tipo == "ventas" else "demanda"
        data = []
        for c in COMPANIES:
            if c["perfil_tipo"] == "compra_venta" or c["rol"] in ("Packing", "Frigorífico"):
                if any(it.get("tipo") == tag for it in c.get("items", [])):
                    data.append(c)
        tpl = "detalle_ventas.html" if tipo == "ventas" else "detalle_compras.html"
        return render_template(tpl, data=wrap_list(data))

    # servicios
    data = []
    for c in COMPANIES:
        if c["perfil_tipo"] == "servicios" or c["rol"] in ("Packing", "Frigorífico"):
            if any(it.get("tipo") == "servicio" for it in c.get("items", [])):
                data.append(c)
    return render_template("detalle_servicios.html", data=wrap_list(data))

# ---------- Perfil público por slug (empresa) ----------
@app.route("/empresa/<slug>")
def empresa(slug):
    comp = next((c for c in COMPANIES if c["slug"] == slug), None)
    if not comp:
        prof = USER_PROFILES.get(slug)
        if not prof:
            abort(404)
        return render_template("empresa.html", comp=ViewObj(prof), es_user=True)
    return render_template("empresa.html", comp=ViewObj(comp), es_user=False)

# ---------- Clientes (listado + detalle) ----------
@app.route("/clientes")
def clientes():
    lista = []
    for uname, prof in USER_PROFILES.items():
        if "cliente" in (prof.get("rol") or "").lower():
            item = prof.copy()
            item["username"] = uname
            lista.append(item)
    if not lista and "cliente@usa.com" in USER_PROFILES:
        item = USER_PROFILES["cliente@usa.com"].copy()
        item["username"] = "cliente@usa.com"
        lista.append(item)
    return render_template("clientes.html", clientes=wrap_list(lista))

@app.route("/cliente/<username>")
def cliente_detalle(username):
    prof = USER_PROFILES.get(username)
    if not prof:
        abort(404)
    comp = {
        "nombre": prof.get("empresa"),
        "rut": prof.get("rut"),
        "email": prof.get("email"),
        "telefono": prof.get("telefono"),
        "direccion": prof.get("direccion"),
        "descripcion": prof.get("descripcion"),
        "items": prof.get("items", []),
    }
    return render_template("cliente_detalle.html", comp=ViewObj(comp), username=username)

# ---------- Mi Perfil (edición + agregar ítems) ----------
@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    if not is_logged():
        return redirect(url_for("login"))
    prof = current_user_profile()
    if not prof:
        abort(404)

    mensaje = None
    if request.method == "POST":
        action = request.form.get("action")
        if action == "save_profile":
            prof["empresa"] = request.form.get("empresa", prof.get("empresa", "")).strip()
            prof["email"] = request.form.get("email", prof.get("email", "")).strip()
            prof["telefono"] = request.form.get("telefono", prof.get("telefono", "")).strip()
            prof["direccion"] = request.form.get("direccion", prof.get("direccion", "")).strip()
            prof["descripcion"] = request.form.get("descripcion", prof.get("descripcion", "")).strip()

            # Manejo de RUT y archivo
            if request.form.get("rut") is not None:
                rut_in = request.form.get("rut").strip()
                prof["rut"] = rut_in if rut_in else prof.get("rut")
            if "rut_file" in request.files:
                f = request.files["rut_file"]
                if f and f.filename and allowed_file(f.filename):
                    fname = secure_filename(f.filename)
                    fname = f"{uuid.uuid4().hex}_{fname}"
                    f.save(os.path.join(UPLOAD_FOLDER, fname))
                    prof["rut_file"] = f"uploads/{fname}"

            # IDs extranjeros
            for key in ("usci", "eori", "tax_id", "otros_id"):
                if request.form.get(key) is not None:
                    prof[key] = request.form.get(key).strip() or prof.get(key)

            mensaje = t("Perfil actualizado.", "Profile updated.")
        elif action == "add_item":
            perfil_tipo = prof.get("perfil_tipo")
            if perfil_tipo == "servicios":
                servicio = request.form.get("servicio", "").strip()
                capacidad = request.form.get("capacidad", "").strip()
                ubicacion = request.form.get("ubicacion", "").strip()
                if servicio:
                    prof.setdefault("items", []).append({
                        "tipo": "servicio",
                        "servicio": servicio,
                        "capacidad": capacidad,
                        "ubicacion": ubicacion
                    })
                    mensaje = t("Servicio agregado.", "Service added.")
            else:
                subtipo  = request.form.get("subtipo", "oferta")
                producto = request.form.get("producto", "").strip()
                cantidad = request.form.get("cantidad", "").strip()
                origen   = request.form.get("origen", "").strip()
                precio   = request.form.get("precio", "").strip()
                if producto:
                    prof.setdefault("items", []).append({
                        "tipo": subtipo,
                        "producto": producto,
                        "cantidad": cantidad,
                        "origen": origen,
                        "precio": precio
                    })
                    mensaje = t("Ítem agregado.", "Item added.")

    return render_template("perfil.html", perfil=ViewObj(prof), mensaje=mensaje)

# ---------- Carrito ----------
@app.route("/cart/add", methods=["POST"])
def cart_add():
    # Recibe campos ocultos desde tablas de detalle/perfil público
    item = request.form.to_dict()
    if "empresa" not in item:
        item["empresa"] = "?"
    add_to_cart(item)
    flash(t("Agregado al carrito", "Added to cart"))
    return redirect(request.referrer or url_for("carrito"))

@app.route("/carrito", methods=["GET", "POST"])
def carrito():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "clear":
            clear_cart()
            flash(t("Carrito vaciado", "Cart cleared"))
            return redirect(url_for("carrito"))
        if action and action.startswith("remove:"):
            idx = action.split(":", 1)[1]
            if remove_from_cart(idx):
                flash(t("Ítem eliminado", "Item removed"))
            return redirect(url_for("carrito"))
    return render_template("carrito.html", cart=get_cart())

# ---------- Ayuda ----------
@app.route("/ayuda", methods=["GET", "POST"])
def ayuda():
    msg = None
    if request.method == "POST":
        correo = request.form.get("correo", "").strip()
        mensaje = request.form.get("mensaje", "").strip()
        if correo and mensaje:
            msg = t("Hemos recibido tu mensaje. Te contactaremos pronto.", "We received your message. We'll contact you soon.")
        else:
            msg = t("Completa correo y mensaje.", "Please complete email and message.")
    return render_template("ayuda.html", mensaje=msg)

# ---------- Descarga segura de uploads (opcional) ----------
@app.route("/uploads/<path:filename>")
def uploads(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=False)

# =========================================================
# Errores
# =========================================================
@app.errorhandler(404)
def not_found(e):
    return render_template(
        "error.html",
        code=404,
        message=t("No encontrado", "Not found", "找不到頁面")
    ), 404

@app.errorhandler(500)
def server_error(e):
    return render_template(
        "error.html",
        code=500,
        message=t("Error interno", "Internal server error", "內部伺服器錯誤")
    ), 500

# =========================================================
# Run local
# =========================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
