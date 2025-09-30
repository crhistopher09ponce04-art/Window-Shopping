\
# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, request, redirect, url_for, session, abort

app = Flask(__name__)
# En producción (Render) toma la clave del entorno; local usa un valor por defecto.
app.secret_key = os.environ.get("SECRET_KEY", "clave_secreta_window_shopping")

# ---------------------------------------
# Datos base (empresas + usuarios)
# ---------------------------------------
empresas = {
    # Exportadores
    "C002": {"id": "C002", "name": "Tuniche Fruit", "role": "exportador", "city": "Valparaíso", "country": "Chile",
             "fruit": "Ciruela", "variety": "Angeleno", "volume_tons": 30, "price_box": 17000, "price_kg": 380,
             "phone": "+56 9 8123 4567", "email": "contacto@tuniche.cl", "tax_id": "RUT-TUNI-002"},
    "C001": {"id": "C001", "name": "Agrícola Montolín S.A.", "role": "exportador", "city": "Maule", "country": "Chile",
             "fruit": "Ciruela", "variety": "Black Diamond", "volume_tons": 50, "price_box": 17500, "price_kg": 400,
             "phone": "+56 9 8765 4321", "email": "ventas@montolin.cl", "tax_id": "RUT-MONTO-001"},

    # Packing / Frigorífico
    "C003": {"id": "C003", "name": "Pukiyai Packing Service", "role": "packing", "city": "Rancagua", "country": "Chile",
             "fruit": "Ciruela", "variety": "Black Amber", "volume_tons": 40, "price_box": 18000, "price_kg": 420,
             "phone": "+56 2 2345 6789", "email": "info@pukiyai.cl", "tax_id": "RUT-PUKI-003"},
    "C004": {"id": "C004", "name": "Frigo Sur", "role": "frigorifico", "city": "Talca", "country": "Chile",
             "fruit": "Ciruela", "variety": "Black Diamond", "volume_tons": 60, "price_box": 16500, "price_kg": 370,
             "phone": "+56 72 222 3333", "email": "contacto@frigosur.cl", "tax_id": "RUT-FRS-004"},

    # Productor / Planta
    "C006": {"id": "C006", "name": "Agrícola El Sol", "role": "productor", "city": "Curicó", "country": "Chile",
             "fruit": "Ciruela", "variety": "Angeleno", "volume_tons": 20, "price_box": 16000, "price_kg": 360,
             "phone": "+56 9 7000 1111", "email": "contacto@elsol.cl", "tax_id": "RUT-ELS-006"},
    "C007": {"id": "C007", "name": "Planta Ejemplo", "role": "planta", "city": "Talca", "country": "Chile",
             "fruit": "Ciruela", "variety": "D'Agen", "volume_tons": 28, "price_box": 16800, "price_kg": 390,
             "phone": "+56 9 5555 5555", "email": "planta@ejemplo.cl", "tax_id": "RUT-PLT-007"},

    # Clientes extranjeros (China)
    "X001": {"id": "X001", "name": "Chensen Ogen Ltd.", "role": "cliente", "city": "Shenzhen", "country": "China",
             "product_requested": "Ciruela fresca", "variety_requested": "Black Diamond", "volume_requested_tons": 50,
             "phone": "+86 138 0000 1111", "email": "chen@ogen.cn", "usci": "USCI-CHEN-001"},
    "X002": {"id": "X002", "name": "Jowin Mao Company", "role": "cliente", "city": "Guangzhou", "country": "China",
             "product_requested": "Ciruela fresca", "variety_requested": "Angeleno", "volume_requested_tons": 40,
             "phone": "+86 139 2222 3333", "email": "mao@joywin.cn", "usci": "USCI-JOW-002"},
}

usuarios = {
    "productor1":   {"password": "1234", "rol": "productor",   "company_id": "C006"},
    "planta1":      {"password": "1234", "rol": "planta",      "company_id": "C007"},
    "packing1":     {"password": "1234", "rol": "packing",     "company_id": "C003"},
    "frigorifico1": {"password": "1234", "rol": "frigorifico", "company_id": "C004"},
    "exportador1":  {"password": "1234", "rol": "exportador",  "company_id": "C002"},
    "cliente1":     {"password": "1234", "rol": "cliente",     "company_id": "X001"},
}

ocultos = {}

role_display = {
    "productor":   "Productor",
    "planta":      "Planta",
    "packing":     "Packing",
    "frigorifico": "Frigorífico",
    "exportador":  "Exportador",
    "cliente":     "Cliente extranjero",
}

VENTAS = {
    "productor":   ["packing", "frigorifico", "exportador"],
    "planta":      ["packing", "frigorifico", "exportador"],
    "packing":     ["frigorifico", "exportador"],
    "frigorifico": ["packing", "exportador"],
    "exportador":  ["cliente"],
    "cliente":     [],
}
COMPRAS = {
    "packing":     ["planta", "productor", "packing", "frigorifico"],
    "frigorifico": ["packing", "planta", "productor", "frigorifico"],
    "exportador":  ["productor", "planta", "packing", "frigorifico"],
    "cliente":     ["exportador"],
    "productor":   [],
    "planta":      [],
}

# ---------------------------------------
# Helpers
# ---------------------------------------
def current_user():
    u = session.get("usuario")
    return u, usuarios.get(u) if u else (None, None)

def next_company_id():
    base = len(empresas) + 1
    return f"C{base:03d}"

def companies_for_roles(roles, exclude_ids=None):
    exclude_ids = exclude_ids or set()
    result = []
    for c in empresas.values():
        if c["role"] in roles and c["id"] not in exclude_ids:
            result.append(c)
    result.sort(key=lambda x: x["name"].lower())
    return result

def ensure_user_hidden_set(user):
    if user not in ocultos:
        ocultos[user] = set()
    return ocultos[user]

# ---------------------------------------
# Rutas
# ---------------------------------------
@app.route("/")
def home():
    if "usuario" in session:
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    usuario = request.form.get("usuario", "").strip()
    password = request.form.get("password", "").strip()
    u = usuarios.get(usuario)
    if u and u["password"] == password:
        session["usuario"] = usuario
        session["rol"] = u["rol"]
        session["company_id"] = u["company_id"]
        return redirect(url_for("dashboard"))
    return render_template("login.html", error="Usuario o contraseña incorrectos")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("usuario", "").strip()
    if not username or username in usuarios:
        return render_template("register.html", error="Usuario inválido o ya existe.")

    password = request.form.get("password", "").strip()
    rol = request.form.get("rol", "").strip()   # productor/planta/packing/frigorifico/exportador/cliente
    name = request.form.get("empresa", "").strip()
    city = request.form.get("ciudad", "").strip()
    country = request.form.get("pais", "").strip()
    phone = request.form.get("telefono", "").strip()
    email = request.form.get("email", "").strip()

    new_id = next_company_id()
    c = {"id": new_id, "name": name, "role": rol, "city": city, "country": country, "phone": phone, "email": email}
    if rol == "cliente":
        c["product_requested"] = (request.form.get("product_requested", "Ciruela fresca") or "Ciruela fresca").strip()
        c["variety_requested"] = request.form.get("variety_requested", "").strip()
        try:
            c["volume_requested_tons"] = float(request.form.get("volume_requested_tons", "0") or 0)
        except:
            c["volume_requested_tons"] = 0.0
        c["usci"] = request.form.get("usci", "").strip()
    else:
        c["fruit"] = "Ciruela"
        c["variety"] = request.form.get("variety", "").strip()
        try:
            c["volume_tons"] = float(request.form.get("volume_tons", "0") or 0)
        except:
            c["volume_tons"] = 0.0
        try:
            c["price_box"] = float(request.form.get("price_box", "0") or 0)
        except:
            c["price_box"] = 0.0
        try:
            c["price_kg"] = float(request.form.get("price_kg", "0") or 0)
        except:
            c["price_kg"] = 0.0
        c["tax_id"] = request.form.get("tax_id", "").strip()

    empresas[new_id] = c
    usuarios[username] = {"password": password, "rol": rol, "company_id": new_id}
    session["usuario"] = username
    session["rol"] = rol
    session["company_id"] = new_id
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("home"))
    user = usuarios[session["usuario"]]
    my_company = empresas.get(user["company_id"])
    rol = user["rol"]
    can_buy = len(COMPRAS.get(rol, [])) > 0
    can_sell = len(VENTAS.get(rol, [])) > 0
    return render_template(
        "dashboard.html",
        usuario=session["usuario"],
        rol=rol,
        my_company=my_company,
        can_buy=can_buy,
        can_sell=can_sell,
        role_display=role_display
    )

@app.route("/acceso/<tipo>")
def acceso(tipo):
    if "usuario" not in session:
        return redirect(url_for("home"))

    rol = session["rol"]
    user = session["usuario"]
    hidden = ensure_user_hidden_set(user)

    if tipo == "ventas":
        roles_destino = VENTAS.get(rol, [])
    elif tipo == "compras":
        roles_destino = COMPRAS.get(rol, [])
    else:
        roles_destino = []

    # Excluir mi empresa y empresas ocultas por mí
    exclude = set(hidden)
    my_company_id = usuarios[user]["company_id"]
    exclude.add(my_company_id)

    lista = companies_for_roles(roles_destino, exclude_ids=exclude)

    # Render: accesos en LISTADO HORIZONTAL (tabla con encabezados)
    return render_template(
        "accesos.html",
        tipo=tipo,
        empresas=lista,
        role_display=role_display,
        COMPRAS=COMPRAS
    )

@app.route("/detalle/<company_id>")
def detalle(company_id):
    if "usuario" not in session:
        return redirect(url_for("home"))
    c = empresas.get(company_id)
    if not c:
        abort(404)

    mi_rol = session["rol"]
    puede_ocultar = c["role"] in COMPRAS.get(mi_rol, [])
    return render_template(
        "detalle.html",
        company=c,
        role_display=role_display,
        puede_ocultar=puede_ocultar
    )

@app.route("/delete/<company_id>", methods=["POST"])
def delete_company(company_id):
    if "usuario" not in session:
        return redirect(url_for("home"))
    user = session["usuario"]
    if company_id in empresas:
        ensure_user_hidden_set(user).add(company_id)
    next_url = request.args.get("next") or url_for("dashboard")
    return redirect(next_url)

# Entrypoint
if __name__ == "__main__":
    app.run(debug=True)
