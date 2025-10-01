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
    return {"LANGS": LANGS, "cur_lang": get_lang()}

@app.route("/lang/<code>")
def set_lang(code):
    session["lang"] = code if code in LANGS else "es"
    return redirect(request.args.get("next") or url_for("home"))

# ------------------------
# Roles
# ------------------------
FRUIT_ROLES = {"Productor", "Planta", "Packing", "Frigorífico", "Exportador", "Cliente extranjero"}
SERVICE_ROLES = {"Packing", "Frigorífico", "Transporte", "Agencia de aduana", "Extraportuario", "Planta", "Exportador"}

# ------------------------
# Empresas demo (seed)
# ------------------------
empresas = {
    "C001": {"id": "C001", "name": "Agrícola Montolín", "role": "Productor", "city": "Maule", "country": "Chile",
             "items": [{"fruit": "Ciruela", "variety": "Black Diamond", "volume_tons": 50, "price_box": 17500, "price_kg": 400}],
             "phone": "+56 9 8765 4321", "email": "ventas@montolin.cl"},
    "C002": {"id": "C002", "name": "Planta Ejemplo", "role": "Planta", "city": "Talca", "country": "Chile",
             "items": [{"fruit": "Ciruela", "variety": "D'Agen", "volume_tons": 28, "price_box": 16800, "price_kg": 390}],
             "phone": "+56 9 5555 5555", "email": "planta@ejemplo.cl"},
    "S001": {"id": "S001", "name": "Transporte Andes", "role": "Transporte", "city": "Santiago", "country": "Chile",
             "items": [{"service": "Camiones refrigerados", "available": "Sí"}],
             "phone": "+56 2 3456 7890", "email": "contacto@transporteandes.cl"}
}

# ------------------------
# Usuarios demo
# ------------------------
usuarios = {
    "productor1": {"password": "1234", "rol": "Productor", "company_id": "C001"},
    "planta1": {"password": "1234", "rol": "Planta", "company_id": "C002"},
    "transporte1": {"password": "1234", "rol": "Transporte", "company_id": "S001"}
}

# ------------------------
# Helpers
# ------------------------
def require_login():
    if "usuario" not in session:
        flash(t("Inicia sesión para continuar.", "Log in to continue."))
        return False
    return True

# ------------------------
# Rutas públicas
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
        session["company_id"] = u["company_id"]
        session.setdefault("cart", [])
        flash(t("Bienvenido", "Welcome"))
        return redirect(url_for("dashboard"))
    return render_template("login.html", error=t("Usuario o contraseña incorrectos", "Invalid credentials"))

@app.route("/register", methods=["GET", "POST"])
def register_router():
    if request.method == "GET":
        return render_template("register_router.html")
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    rut = request.form.get("rut", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    city = request.form.get("city", "").strip()
    country = request.form.get("country", "").strip()
    rol = request.form.get("rol", "").strip()

    if username in usuarios:
        return render_template("register_router.html", error="Usuario ya existe")

    company_id = f"U{len(empresas)+1:03d}"
    empresas[company_id] = {
        "id": company_id, "name": username, "role": rol, "city": city, "country": country,
        "items": [], "phone": phone, "email": email, "rut": rut
    }
    usuarios[username] = {"password": password, "rol": rol, "company_id": company_id}
    flash("Usuario registrado correctamente")
    return redirect(url_for("login"))

@app.route("/help")
def help_center():
    return render_template("help_center.html")

# ------------------------
# Rutas privadas
# ------------------------
@app.route("/dashboard")
def dashboard():
    if not require_login(): return redirect(url_for("home"))
    user = usuarios[session["usuario"]]
    my_company = empresas.get(user["company_id"])
    return render_template("dashboard.html", usuario=session["usuario"], rol=user["rol"], my_company=my_company)

@app.route("/detalle/<company_id>", methods=["GET", "POST"])
def detalle(company_id):
    if not require_login(): return redirect(url_for("home"))
    c = empresas.get(company_id)
    if not c: abort(404)
    if request.method == "POST":
        item = {
            "company_id": company_id,
            "name": c["name"],
            "role": c["role"],
            "quantity": request.form.get("quantity", "1"),
            "notes": request.form.get("notes", "")
        }
        cart = session.setdefault("cart", [])
        cart.append(item)
        session["cart"] = cart
        flash("Agregado al carrito.")
        return redirect(url_for("cart"))
    return render_template("detalle.html", company=c)

@app.route("/cart", methods=["GET", "POST"])
def cart():
    if not require_login(): return redirect(url_for("home"))
    if request.method == "POST":
        action = request.form.get("action")
        if action == "clear":
            session["cart"] = []
            flash("Carrito vaciado.")
        elif action and action.startswith("remove:"):
            idx = int(action.split(":")[1])
            cart = session.get("cart", [])
            if 0 <= idx < len(cart):
                cart.pop(idx)
                session["cart"] = cart
                flash("Ítem eliminado.")
        elif action == "checkout":
            session["cart"] = []
            flash("¡Solicitud enviada! Nuestro equipo te contactará.")
            return redirect(url_for("dashboard"))
    return render_template("cart.html", cart=session.get("cart", []))

@app.route("/mi-perfil", methods=["GET", "POST"])
def mi_perfil():
    if not require_login(): return redirect(url_for("home"))
    company_id = session["company_id"]
    c = empresas.get(company_id)
    if not c: abort(404)

    if request.method == "POST":
        new_item = {
            "fruit": request.form.get("fruit"),
            "variety": request.form.get("variety"),
            "volume_tons": request.form.get("volume_tons"),
            "price_box": request.form.get("price_box"),
            "price_kg": request.form.get("price_kg"),
            "service": request.form.get("service"),
        }
        c["items"].append(new_item)
        flash("Nuevo ítem agregado.")
        return redirect(url_for("mi_perfil"))

    return render_template("mi_perfil.html", company=c)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ------------------------
# Errores
# ------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="Recurso no encontrado"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message="Error interno"), 500

# ------------------------
# Entrypoint local
# ------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
