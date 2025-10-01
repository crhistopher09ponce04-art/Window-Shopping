from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps

app = Flask(__name__)
app.secret_key = "clave_secreta_demo"

# ---------------------------
# Usuarios de prueba
# ---------------------------
usuarios = {
    "productor1": {"password": "1234", "rol": "Productor"},
    "planta1": {"password": "1234", "rol": "Planta"},
    "packing1": {"password": "1234", "rol": "Packing"},
    "frigorifico1": {"password": "1234", "rol": "Frigorífico"},
    "exportador1": {"password": "1234", "rol": "Exportador"},
    "cliente1": {"password": "1234", "rol": "Cliente extranjero"},
    "transporte1": {"password": "1234", "rol": "Transporte"},
    "aduana1": {"password": "1234", "rol": "Agencia de aduana"},
    "extraportuario1": {"password": "1234", "rol": "Extraportuario"},
}

# ---------------------------
# Traducción rápida
# ---------------------------
def t(es, en):
    lang = session.get("lang", "es")
    return es if lang == "es" else en

@app.route("/set_lang/<code>")
def set_lang(code):
    session["lang"] = code
    return redirect(request.referrer or url_for("home"))

# ---------------------------
# Decorador para login requerido
# ---------------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "usuario" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# ---------------------------
# HOME / LANDING
# ---------------------------
@app.route("/")
def home():
    return render_template("landing.html", t=t)

# ---------------------------
# LOGIN
# ---------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = usuarios.get(username)
        if user and user["password"] == password:
            session["usuario"] = username
            return redirect(url_for("dashboard"))
        else:
            error = "Usuario o contraseña incorrectos"
    return render_template("login.html", error=error, t=t)

# ---------------------------
# LOGOUT
# ---------------------------
@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("home"))

# ---------------------------
# REGISTRO
# ---------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        rut = request.form["rut"]
        email = request.form["email"]
        address = request.form["address"]
        phone = request.form["phone"]
        rol = request.form["rol"]

        if username in usuarios:
            return render_template("register.html", error="El usuario ya existe.", t=t)

        usuarios[username] = {
            "password": password,
            "rol": rol,
            "rut": rut,
            "email": email,
            "address": address,
            "phone": phone
        }

        session["usuario"] = username
        return redirect(url_for("dashboard"))

    return render_template("register.html", t=t)

# ---------------------------
# DASHBOARD
# ---------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    username = session["usuario"]
    user = usuarios.get(username)
    return render_template("dashboard.html", usuario=username, rol=user["rol"], t=t)

# ---------------------------
# ACCESOS POR TIPO
# ---------------------------
@app.route("/accesos/<tipo>")
@login_required
def accesos(tipo):
    data = []

    if tipo == "ventas":
        data = ["Orden #123 - Cliente extranjero", "Orden #124 - Exportador"]
    elif tipo == "compras":
        data = ["Compra de insumos - Packing", "Contrato de transporte"]
    elif tipo == "servicios":
        data = ["Servicio de Agencia de Aduana", "Frigorífico contratado"]

    return render_template("accesos.html", tipo=tipo, data=data, t=t)

# ---------------------------
# ERROR HANDLER
# ---------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message=t("Página no encontrada", "Page not found"), t=t), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message=t("Error interno", "Internal server error"), t=t), 500

# ---------------------------
# MAIN
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
