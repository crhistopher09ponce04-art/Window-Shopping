import os
from flask import Flask, render_template, request, redirect, url_for, session, abort

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave_secreta_window_shopping")

# -------- Datos de ejemplo --------
empresas = {
    "C001": {"id": "C001", "name": "Agrícola Montolín", "role": "Exportador", "city": "Maule", "country": "Chile",
             "fruit": "Ciruela", "variety": "Black Diamond", "volume_tons": 50, "price_box": 17500, "price_kg": 400,
             "phone": "+56 9 8765 4321", "email": "ventas@montolin.cl"},
    "X001": {"id": "X001", "name": "Chensen Ogen Ltd.", "role": "Cliente extranjero", "city": "Shenzhen", "country": "China",
             "product_requested": "Ciruela fresca", "variety_requested": "Black Diamond", "volume_requested_tons": 50,
             "phone": "+86 138 0000 1111", "email": "chen@ogen.cn"}
}

usuarios = {
    "productor1": {"password": "1234", "rol": "Productor", "company_id": "C001"},
    "cliente1": {"password": "1234", "rol": "Cliente extranjero", "company_id": "X001"},
}

# -------- Helpers --------
def current_user():
    u = session.get("usuario")
    return u, usuarios.get(u) if u else (None, None)

# -------- Rutas --------
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
        "company_id": "C001"  # por ahora asignamos demo
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
    return render_template("accesos.html", usuario=session["usuario"], rol=session["rol"], tipo=tipo, empresas=list(empresas.values()))

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
