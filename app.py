from flask import Flask, render_template, request, redirect, url_for, session, abort
import os

app = Flask(__name__)
app.secret_key = "clave_super_secreta"

# Traducciones básicas (ES, EN, ZH)
def t(es, en, zh=None):
    lang = session.get("lang", "es")
    if lang == "es":
        return es
    elif lang == "en":
        return en
    elif lang == "zh" and zh is not None:
        return zh
    else:
        return es

# Usuarios de prueba
usuarios_demo = {
    "productor1": {"password": "1234", "rol": "productor"},
    "planta1": {"password": "1234", "rol": "planta"},
    "packing1": {"password": "1234", "rol": "packing"},
    "frigorifico1": {"password": "1234", "rol": "frigorifico"},
    "exportador1": {"password": "1234", "rol": "exportador"},
    "cliente1": {"password": "1234", "rol": "cliente"},
    "transporte1": {"password": "1234", "rol": "transporte"},
    "aduana1": {"password": "1234", "rol": "agencia_aduana"},
    "extraportuario1": {"password": "1234", "rol": "extraportuario"}
}

# ---------------- Rutas principales ---------------- #

@app.route("/")
def home():
    return render_template("landing.html", t=t)

@app.route("/set_lang/<code>")
def set_lang(code):
    session["lang"] = code
    return redirect(request.referrer or url_for("home"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in usuarios_demo and usuarios_demo[username]["password"] == password:
            session["user"] = username
            session["rol"] = usuarios_demo[username]["rol"]

            session["carrito"] = []
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", t=t, error=t("Credenciales inválidas", "Invalid credentials", "凭证无效"))
    return render_template("login.html", t=t)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", t=t, user=session["user"], rol=session["rol"])

# ---------------- Accesos ---------------- #

@app.route("/accesos/<tipo>")
def accesos(tipo):
    if "user" not in session:
        return redirect(url_for("login"))

    if tipo == "ventas":
        data = ["Cajas de manzana - 1000kg", "Trufas negras - 200kg", "Uvas verdes - 500kg"]
    elif tipo == "compras":
        data = ["Demanda de cerezas - 300kg", "Demanda de trufas - 50kg"]
    elif tipo == "servicios":
        data = ["Servicio de packing - Planta Central", "Transporte refrigerado", "Agencia de aduanas"]
    else:
        data = []

    return render_template("accesos.html", t=t, tipo=tipo, data=data)

# ---------------- Carrito ---------------- #

@app.route("/carrito/add/<item>")
def add_carrito(item):
    if "carrito" not in session:
        session["carrito"] = []
    carrito = session["carrito"]
    if item not in carrito:
        carrito.append(item)
    session["carrito"] = carrito
    return redirect(url_for("carrito"))

@app.route("/carrito")
def carrito():
    if "carrito" not in session:
        session["carrito"] = []
    return render_template("carrito.html", t=t, items=session["carrito"])

@app.route("/carrito/remove/<item>")
def remove_carrito(item):
    if "carrito" in session:
        carrito = session["carrito"]
        if item in carrito:
            carrito.remove(item)
        session["carrito"] = carrito
    return redirect(url_for("carrito"))

# ---------------- Errores ---------------- #

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message=t("Página no encontrada", "Page not found", "未找到页面"), t=t), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message=t("Error interno", "Internal server error", "内部服务器错误"), t=t), 500


if __name__ == "__main__":
    app.run(debug=True)
