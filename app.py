import os
from flask import Flask, render_template, request, redirect, url_for, session, abort

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key-please-change")

# -------------------- i18n helper --------------------
def t(es: str, en: str, zh: str | None = None) -> str:
    lang = session.get("lang", "es")
    if lang == "zh" and zh is not None:
        return zh
    return es if lang == "es" else en

@app.context_processor
def inject_helpers():
    return dict(t=t)

# -------------------- Language -----------------------
@app.route("/lang/<lang>")
def set_lang(lang):
    if lang not in ("es", "en", "zh"):
        lang = "es"
    session["lang"] = lang
    # back to dashboard if logged in, else home
    return redirect(request.referrer or url_for("home"))

# -------------------- Mock data & users --------------
USERS = {
    # demo users (username -> dict)
    "productor1":   {"password": "1234", "rol": "Productor", "rut": "11.111.111-1", "email": "productor1@demo.cl", "address": "Parral, Maule", "phone": "+56 9 1111 1111"},
    "planta1":      {"password": "1234", "rol": "Planta", "rut": "22.222.222-2", "email": "planta1@demo.cl", "address": "Rengo, O'Higgins", "phone": "+56 9 2222 2222"},
    "packing1":     {"password": "1234", "rol": "Packing", "rut": "33.333.333-3", "email": "packing1@demo.cl", "address": "Curicó, Maule", "phone": "+56 9 3333 3333"},
    "frigorifico1": {"password": "1234", "rol": "Frigorífico", "rut": "44.444.444-4", "email": "frigorifico1@demo.cl", "address": "San Fernando", "phone": "+56 9 4444 4444"},
    "exportador1":  {"password": "1234", "rol": "Exportador", "rut": "55.555.555-5", "email": "exportador1@demo.cl", "address": "Santiago", "phone": "+56 9 5555 5555"},
    "cliente1":     {"password": "1234", "rol": "Cliente extranjero", "rut": "N/A",          "email": "cliente1@demo.com", "address": "Shanghai, CN", "phone": "+86 21 1234 5678"},
    "transporte1":  {"password": "1234", "rol": "Transporte", "rut": "66.666.666-6", "email": "transporte1@demo.cl", "address": "Quillota", "phone": "+56 9 6666 6666"},
    "aduana1":      {"password": "1234", "rol": "Agencia de aduanas", "rut": "77.777.777-7", "email": "aduana1@demo.cl", "address": "Valparaíso", "phone": "+56 9 7777 7777"},
    "extraportuario1":{"password": "1234", "rol": "Extraportuario", "rut": "88.888.888-8", "email": "extraportuario1@demo.cl", "address": "San Antonio", "phone": "+56 9 8888 8888"},
}

# demo marketplace items (coherent mixed data)
ITEMS = {
    "ventas": [
        {"id": "V001", "item": "Uva Red Globe", "company": "Viñedos Maule", "qty": "24 pallets", "price": "USD 18.50/box", "location": "San Javier", "spec": "18 lb, exportación"},
        {"id": "V002", "item": "Cereza Santina", "company": "Campos del Sur", "qty": "10 pallets", "price": "USD 6.20/kg", "location": "Curicó", "spec": "32mm+, pre-reserva"},
        {"id": "V003", "item": "Manzana Fuji", "company": "Frutícola Andes", "qty": "30 pallets", "price": "USD 10.90/box", "location": "Rengo", "spec": "Cal. 80-100, export"},
    ],
    "compras": [
        {"id": "C101", "item": "Limón Sutil", "company": "Retail Perú SAC", "qty": "15 pallets", "price": "USD 0.75/kg", "location": "Lima (FOB)", "spec": "semana 48-50"},
        {"id": "C102", "item": "Naranja Navel", "company": "Fresh UK Ltd", "qty": "40 pallets", "price": "USD 9.20/box", "location": "Valparaíso (FOB)", "spec": "pack 18kg"},
    ],
    "servicios": [
        {"id": "S201", "item": "Packing arándano", "company": "Packing Los Robles", "qty": "Capacidad 25 t/día", "price": "USD 0.38/kg", "location": "Los Ángeles", "spec": "BRC AA, clamshell"},
        {"id": "S202", "item": "Frío de tránsito", "company": "FrioSur", "qty": "Cámaras 1-8°C", "price": "USD 10/pallet/sem", "location": "Rancagua", "spec": "ATP, monitoreo 24/7"},
        {"id": "S203", "item": "Transporte reefer", "company": "LogisChile", "qty": "Ruta V-RM", "price": "USD 250/viaje", "location": "V Región", "spec": "GPS, 32 pallets"},
        {"id": "S204", "item": "Agenciamiento aduanas", "company": "Aduanas Valpo", "qty": "Export/Import", "price": "Desde USD 120", "location": "Valparaíso", "spec": "SILOGPORT, EDI"},
    ],
}

# which roles can ofrecer servicios
SERVICE_ROLES = {"Packing","Frigorífico","Transporte","Agencia de aduanas"}

# -------------------- Utils --------------------------
def ensure_session():
    session.setdefault("lang", "es")
    session.setdefault("cart", {"ventas": [], "compras": [], "servicios": []})
    session.setdefault("hidden", {"ventas": set(), "compras": set(), "servicios": set()})

def current_user():
    u = session.get("usuario")
    if not u: return None
    data = USERS.get(u, {}).copy()
    data["username"] = u
    return data

# -------------------- Routes -------------------------
@app.route("/")
def home():
    ensure_session()
    return render_template("landing.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    ensure_session()
    error = None
    if request.method == "POST":
        user = request.form.get("username","").strip()
        pw   = request.form.get("password","").strip()
        if user in USERS and USERS[user]["password"] == pw:
            session["usuario"] = user
            return redirect(url_for("dashboard"))
        error = t("Usuario o contraseña incorrectos","Incorrect username or password","用户名或密码不正确")
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# --- Registro (con filtro Nacional/Extranjero) ------
@app.route("/register_router")
def register_router():
    ensure_session()
    return render_template("register_router.html")

@app.route("/register", methods=["GET","POST"])
def register():
    ensure_session()
    kind = request.args.get("tipo","nacional")  # nacional | extranjero
    error = None
    if request.method == "POST":
        username = request.form.get("username","").strip()
        if not username or username in USERS:
            error = t("Nombre de usuario no válido o ya existe","Invalid or already taken username","用户名无效或已存在")
        else:
            USERS[username] = {
                "password": request.form.get("password",""),
                "rol": request.form.get("rol",""),
                "rut": request.form.get("rut",""),
                "email": request.form.get("email",""),
                "address": request.form.get("address",""),
                "phone": request.form.get("phone",""),
            }
            session["usuario"] = username
            return redirect(url_for("dashboard"))
    # roles visibles según tipo y categoría
    compra_venta_roles = ["Productor","Planta","Packing","Frigorífico","Exportador","Cliente extranjero"]
    servicio_roles = ["Packing","Frigorífico","Transporte","Agencia de aduanas"]
    return render_template("register.html", error=error, tipo=kind,
                           compra_venta_roles=compra_venta_roles, servicio_roles=servicio_roles)

# -------------------- Dashboard / Perfil -------------
@app.route("/dashboard")
def dashboard():
    ensure_session()
    if "usuario" not in session:
        return redirect(url_for("login"))
    user = current_user()
    my_company = user["rol"]
    return render_template("dashboard.html", usuario=user["username"], rol=user["rol"], my_company=my_company)

@app.route("/perfil", methods=["GET","POST"])
def perfil():
    ensure_session()
    if "usuario" not in session:
        return redirect(url_for("login"))
    user = current_user()

    # alta de ítems propios (demo, se agregan a ITEMS)
    if request.method == "POST":
        tipo = request.form.get("tipo")  # ventas/compras/servicios
        if tipo not in ITEMS: abort(400)
        new = {
            "id": (tipo[:1].upper()+str(len(ITEMS[tipo])+1001)),
            "item": request.form.get("item") or "Producto/Servicio",
            "company": request.form.get("company") or user["rol"],
            "qty": request.form.get("qty") or "",
            "price": request.form.get("price") or "",
            "location": request.form.get("location") or "",
            "spec": request.form.get("spec") or "",
        }
        # reglas: servicios sólo si el rol pertenece
        if tipo == "servicios" and user["rol"] not in SERVICE_ROLES:
            pass  # silencioso: no agrega
        else:
            ITEMS[tipo].insert(0, new)

    return render_template("perfil.html", user=user)

# -------------------- Accesos (ventas/compras/servicios) -----
@app.route("/accesos/<tipo>")
def accesos(tipo):
    ensure_session()
    if "usuario" not in session:
        return redirect(url_for("login"))
    if tipo not in ("ventas","compras","servicios"):
        abort(404)

    q = (request.args.get("q") or "").lower().strip()
    hidden_ids = session["hidden"][tipo]
    data = [x for x in ITEMS[tipo] if x["id"] not in hidden_ids]
    if q:
        data = [x for x in data if q in x["item"].lower() or q in x["company"].lower() or q in x["location"].lower() or q in x["spec"].lower() or q in x["id"].lower()]
    return render_template("accesos.html", tipo=tipo, data=data, q=q)

# carrito: add & hide-from-view
@app.route("/cart/add/<tipo>/<item_id>", methods=["POST"])
def cart_add(tipo, item_id):
    ensure_session()
    if "usuario" not in session:
        return redirect(url_for("login"))
    if tipo not in ITEMS: abort(404)
    if item_id not in session["cart"][tipo]:
        session["cart"][tipo].append(item_id)
    return ("",204)

@app.route("/hide/<tipo>/<item_id>", methods=["POST"])
def hide_item(tipo, item_id):
    ensure_session()
    if "usuario" not in session:
        return redirect(url_for("login"))
    if tipo not in ITEMS: abort(404)
    session["hidden"][tipo].add(item_id)
    return ("",204)

# -------------------- Errors -------------------------
@app.errorhandler(404)
def not_found(_):
    return render_template("error.html", code=404, message=t("No encontrado","Not found","未找到")), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message=t("Error interno","Internal server error","服务器内部错误")), 500

# -------------------- Run (local) --------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
