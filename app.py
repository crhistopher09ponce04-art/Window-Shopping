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
        "cur_lang": get_lang(),
        "t": t
    }

@app.route("/lang/<code>")
def set_lang(code):
    session["lang"] = code if code in LANGS else "es"
    return redirect(request.args.get("next") or url_for("home"))

# ------------------------
# Usuarios demo
# ------------------------
usuarios = {
    "productor1": {"password": "1234", "rol": "Productor"},
    "exportador1": {"password": "1234", "rol": "Exportador"},
    "cliente1": {"password": "1234", "rol": "Cliente extranjero"}
}

# ------------------------
# Home & Login
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
        session.setdefault("cart", [])
        flash(t("Bienvenido", "Welcome"))
        return redirect(url_for("dashboard"))
    return render_template("login.html", error=t("Usuario o contraseña incorrectos", "Invalid credentials"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ------------------------
# Dashboard
# ------------------------
@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", usuario=session["usuario"], rol=session["rol"])

# ------------------------
# Nueva ruta: accesos
# ------------------------
@app.route("/accesos/<tipo>")
def accesos(tipo):
    if "usuario" not in session:
        return redirect(url_for("login"))

    # Datos de prueba
    if tipo == "ventas":
        data = ["Venta de ciruelas a China", "Venta de cerezas a EE.UU."]
    elif tipo == "compras":
        data = ["Compra de cajas", "Compra de servicio de transporte"]
    else:
        data = []

    return render_template("accesos.html", tipo=tipo, data=data)

# ------------------------
# Carrito
# ------------------------
@app.route("/cart", methods=["GET", "POST"])
def cart():
    if "usuario" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        action = request.form.get("action")
        if action == "clear":
            session["cart"] = []
            flash(t("Carrito vaciado.", "Cart cleared."))
    return render_template("cart.html", cart=session.get("cart", []))

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
