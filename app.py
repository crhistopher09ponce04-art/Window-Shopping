import os
from flask import Flask, render_template, request, redirect, url_for, session, abort

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")

# ---------------------------
# Idiomas y traducciones
# ---------------------------
SUPPORTED_LANGS = ["es", "en", "zh"]
DEFAULT_LANG = "es"

def get_lang():
    return session.get("lang", DEFAULT_LANG)

def t(es_text, en_text, zh_text=None):
    lang = get_lang()
    if lang == "en":
        return en_text
    if lang == "zh":
        return zh_text or en_text
    return es_text

@app.route("/lang/<lang>")
def set_lang(lang):
    if lang not in SUPPORTED_LANGS:
        lang = DEFAULT_LANG
    session["lang"] = lang
    return redirect(request.referrer or url_for("home"))

# ---------------------------
# Datos ficticios para demo
# ---------------------------
COMPANIES = [
    {
        "slug": "agro-andes",
        "nombre": "Agro Andes SPA",
        "rut": "76.123.456-7",
        "rol": "Productor",
        "perfil_tipo": "compra_venta",
        "pais": "CL",
        "breve": "Productores de uva de mesa.",
        "items": [
            {"tipo": "oferta", "producto": "Uva Crimson", "cantidad": "80 pallets", "origen": "IV Región", "precio": "A convenir"},
            {"tipo": "demanda", "producto": "Cajas plásticas", "cantidad": "15.000 und", "origen": "CL", "precio": "Oferta"}
        ]
    },
    {
        "slug": "friopoint",
        "nombre": "FríoPoint Ltda.",
        "rut": "77.654.321-0",
        "rol": "Frigorífico",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "breve": "Frío y logística en Valparaíso.",
        "items": [
            {"tipo": "servicio", "servicio": "Almacenaje en frío", "capacidad": "1.200 pallets", "ubicacion": "Valparaíso"},
            {"tipo": "servicio", "servicio": "Preenfriado", "capacidad": "8 túneles", "ubicacion": "Valparaíso"},
        ]
    },
    {
        "slug": "pack-smart",
        "nombre": "PackSmart",
        "rut": "78.987.654-3",
        "rol": "Packing",
        "perfil_tipo": "servicios",
        "pais": "CL",
        "breve": "Servicios de packing para exportación.",
        "items": [
            {"tipo": "servicio", "servicio": "Embalaje exportación", "capacidad": "30.000 cajas/día", "ubicacion": "R.M."}
        ]
    }
]

# Carrito (demo, por sesión)
def get_cart():
    return session.setdefault("cart", [])

# ---------------------------
# Rutas principales
# ---------------------------
@app.route("/")
def home():
    return render_template("landing.html", t=t)

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", data=COMPANIES, cart=get_cart(), t=t)

@app.route("/detalles/<tipo>")
def detalles(tipo):
    if tipo == "ventas":
        data = [c for c in COMPANIES if c["perfil_tipo"] == "compra_venta"]
        return render_template("detalle_ventas.html", data=data, t=t)
    elif tipo == "compras":
        data = [c for c in COMPANIES if c["perfil_tipo"] == "compra_venta"]
        return render_template("detalle_compras.html", data=data, t=t)
    elif tipo == "servicios":
        data = [c for c in COMPANIES if c["perfil_tipo"] == "servicios"]
        return render_template("detalle_servicios.html", data=data, t=t)
    else:
        abort(404)

@app.route("/empresa/<slug>")
def empresa(slug):
    comp = next((c for c in COMPANIES if c["slug"] == slug), None)
    if not comp:
        abort(404)
    return render_template("empresa.html", comp=comp, t=t)

@app.route("/carrito")
def carrito():
    return render_template("carrito.html", cart=get_cart(), t=t)

@app.route("/cart/add", methods=["POST"])
def cart_add():
    item = request.form.to_dict()
    cart = get_cart()
    cart.append(item)
    session["cart"] = cart
    return redirect(request.referrer or url_for("dashboard"))

@app.route("/perfil")
def perfil():
    usuario = {
        "empresa": "Demo Export SPA",
        "rut": "76.555.111-9",
        "rol": "Exportador",
        "pais": "CL",
        "email": "contacto@demo.cl",
        "telefono": "+56 9 5555 5555",
        "direccion": "Santiago Centro",
        "descripcion": "Empresa ficticia para demo.",
        "items": [
            {"tipo": "oferta", "producto": "Cerezas", "cantidad": "100 pallets", "origen": "VI Región", "precio": "A convenir"}
        ]
    }
    return render_template("perfil.html", perfil=usuario, t=t)

@app.route("/ayuda", methods=["GET", "POST"])
def ayuda():
    msg = None
    if request.method == "POST":
        msg = "✅ Gracias, hemos recibido tu solicitud."
    return render_template("ayuda.html", mensaje=msg, t=t)

# ---------------------------
# Errores
# ---------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message=t("No encontrado", "Not found"), t=t), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message=t("Error interno", "Internal server error"), t=t), 500

# ---------------------------
# Run local
# ---------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
