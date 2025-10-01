import os
from flask import Flask, render_template, request, redirect, url_for, session, abort

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave_secreta_window_shopping")

# ------------------------
# Empresas de prueba
# ------------------------
empresas = {
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
    "X001": {"id": "X001", "name": "Chensen Ogen Ltd.", "role": "Cliente extranjero", "city": "Shenzhen", "country": "China",
             "product_requested": "Ciruela fresca", "variety_requested": "Black Diamond", "volume_requested_tons": 50,
             "phone": "+86 138 0000 1111", "email": "chen@ogen.cn"},
    "S001": {"id": "S001", "name": "Transporte Andes", "role": "Transporte", "city": "Santiago", "country": "Chile",
             "service": "Camiones refrigerados", "phone": "+56 2 3456 7890", "email": "contacto@transporteandes.cl"},
    "S002": {"id": "S002", "name": "Aduanas Chile Ltda.", "role": "Agencia de aduana", "city": "Valparaíso", "country": "Chile",
             "service": "Gestión documental y trámites", "phone": "+56 2 9999 1111", "email": "aduana@chile.cl"},
    "S003": {"id": "S003", "name": "Puerto Seco SA", "role": "Extraportuario", "city": "San Antonio", "country": "Chile",
             "service": "Almacenaje extraportuario", "phone": "+56 35 1234 567", "email": "info@puertoseco.cl"}
}

# ------------------------
# Usuarios de prueba
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
VENTAS = {
    "Productor": ["Packing", "Frigorífico", "Exportador"],
    "Planta": ["Packing", "Frigorífico", "Exportador"],
    "Packing": ["Frigorífico", "Exportador"],
    "Frigorífico": ["Packing", "Exportador"],
    "Exportador": ["Cliente extranjero"],
    "Cliente extranjero": [],
    "Transporte": ["Exportador", "Packing", "Frigorífico", "Planta"],
    "Agencia de aduana": ["Exportador"],
    "Extraportuario": ["Exportador"]
}

COMPRAS = {
    "Packing": ["Productor", "Planta", "Frigorífico"],
    "Frigorífico": ["Productor", "Planta", "Packing"],
    "Exportador": ["Productor", "Planta", "Packing", "Frigorífico", "Transporte", "Agencia de aduana", "Extraportuario"],
    "Cliente extranjero": ["Exportador"],
    "Productor": [],
    "Planta": [],
    "Transporte": [],
    "Agencia de aduana": [],
    "Extraportuario": []
}

# ------------------------
# Helpers
# ------------------------
def current_user():
    u = session.get("usuario")
    return u, usuarios.get(u) if u else (None, None)

def companies_for_roles(roles):
    return [c for c in empresas.values() if c["role"] in roles]

# ------------------------
# Rutas
# ------------------------
@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    u = usuarios.get(username)
    if u and u["password"] == password:
        session["usuario"] = username
        session["rol"] = u["rol"]
        session["company_id"] = u["company_id"]
        return redirect(url_for("dashboard"))
    return render_template("login.html", error="Usuario o contraseña incorrectos")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    # guardar usuario
    username = request.form["usuario"]
    if username in usuarios:
        return render_template("register.html", error="Usuario ya existe")
    usuarios[username] = {
        "password": request.form["password"],
        "rol": request.form["rol"],
        "company_id": "C001"  # demo
    }
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("home"))
    user = usuarios[session["usuario"]]
    my_company = empresas.get(user["company_id"])
    return render_template("dashboard.html", usuario=session["usuario"], rol=user["rol"], my_company=my_company)

@app.route("/accesos/<tipo>")
def accesos(tipo):
    if "usuario" not in session:
        return redirect(url_for("home"))
    rol = session["rol"]
    if tipo == "ventas":
        roles_destino = VENTAS.get(rol, [])
    else:
        roles_destino = COMPRAS.get(rol, [])
    lista = companies_for_roles(roles_destino)
    return render_template("accesos.html", usuario=session["usuario"], rol=rol, tipo=tipo, empresas=lista)

@app.route("/detalle/<company_id>")
def detalle(company_id):
    if "usuario" not in session:
        return redirect(url_for("home"))
    c = empresas.get(company_id)
    if not c:
        abort(404)
    return render_template("detalle.html", company=c)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
