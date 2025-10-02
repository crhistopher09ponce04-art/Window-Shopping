from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "clave_secreta"

# ---- Traducción ----
def t(es, en, zh=""):
    lang = session.get("lang", "es")
    if lang == "es":
        return es
    elif lang == "en":
        return en
    elif lang == "zh":
        return zh if zh else en
    return es

@app.context_processor
def inject_globals():
    return dict(t=t)

# ---- Datos ficticios ----
ventas_data = [
    {"empresa": "Frutas Chile SpA", "producto": "Cerezas", "variedad": "Regina", "precio": "USD 4.5/kg"},
    {"empresa": "Exportadora Andes", "producto": "Uvas", "variedad": "Red Globe", "precio": "USD 2.8/kg"},
]

compras_data = [
    {"empresa": "Mercado Beijing Ltd.", "producto": "Ciruelas", "cantidad": "50 toneladas"},
    {"empresa": "Distribuidora Shanghái", "producto": "Kiwis", "cantidad": "30 toneladas"},
]

servicios_data = [
    {"empresa": "Packing del Maule", "servicio": "Embalaje premium", "precio": "USD 0.30/kg"},
    {"empresa": "FrioSur", "servicio": "Almacenaje en frío", "precio": "USD 0.10/kg/día"},
]

usuarios = {
    "demo": {"password": "1234", "empresa": "Frutas Chile SpA", "rut": "76.543.210-K", "rol": "exportador"}
}

# ---- Rutas principales ----
@app.route("/")
def home():
    return render_template("landing.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]
        if user in usuarios and usuarios[user]["password"] == pwd:
            session["user"] = user
            return redirect(url_for("dashboard"))
        return render_template("login.html", error=t("Credenciales inválidas", "Invalid credentials", "憑證無效"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=usuarios[session["user"]])

@app.route("/perfil")
def perfil():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("perfil.html", user=usuarios[session["user"]])

# ---- Rutas de detalles ----
@app.route("/detalles/ventas")
def detalles_ventas():
    return render_template("detalle_ventas.html", items=ventas_data)

@app.route("/detalles/compras")
def detalles_compras():
    return render_template("detalle_compras.html", items=compras_data)

@app.route("/detalles/servicios")
def detalles_servicios():
    return render_template("detalle_servicios.html", items=servicios_data)

# ---- Carrito ----
@app.route("/carrito")
def carrito():
    return render_template("carrito.html", carrito=session.get("carrito", []))

# ---- Error Handler ----
@app.errorhandler(500)
def server_error(e):
    return render_template("error.html",
                           code=500,
                           message=t("Error interno", "Internal server error", "內部伺服器錯誤")), 500

if __name__ == "__main__":
    app.run(debug=True)
