from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.exceptions import HTTPException
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------------------
# Traducción simple (ES, EN, ZH)
# ---------------------------
def t(es, en, zh=None):
    lang = session.get("lang", "es")
    if lang == "en":
        return en
    elif lang == "zh" and zh:
        return zh
    return es

# ---------------------------
# Usuarios de prueba
# ---------------------------
USERS = {
    "productor_demo": {"password": "Demo1234", "rol": "Productor", "perfil_tipo": "compra_venta", "pais": "CL"},
    "packing_demo": {"password": "Demo1234", "rol": "Packing", "perfil_tipo": "servicios", "pais": "CL"},
    "frigorifico_demo": {"password": "Demo1234", "rol": "Frigorífico", "perfil_tipo": "servicios", "pais": "CL"},
    "exportador_demo": {"password": "Demo1234", "rol": "Exportador", "perfil_tipo": "compra_venta", "pais": "CL"},
    "cliente_ex_demo": {"password": "Demo1234", "rol": "Cliente extranjero", "perfil_tipo": "compra_venta", "pais": "US"},
    "transporte_demo": {"password": "Demo1234", "rol": "Transporte", "perfil_tipo": "servicios", "pais": "CL"},
    "aduana_demo": {"password": "Demo1234", "rol": "Agencia de Aduanas", "perfil_tipo": "servicios", "pais": "CL"},
    "extraport_demo": {"password": "Demo1234", "rol": "Extraportuario", "perfil_tipo": "servicios", "pais": "CL"},
}

# ---------------------------
# Datos ficticios de empresas y ofertas/demandas
# ---------------------------
empresas = [
    {"id": 1, "nombre": "AgroDemo Productores SPA", "rol": "Productor", "pais": "Chile",
     "descripcion": "Productores de uva y berries.", "email": "ventas@agrodemo.cl", "telefono": "+56 9 6000 0001",
     "items": [
         {"tipo": "oferta", "producto": "Uva Crimson", "cantidad": "120 pallets", "precio": "A convenir"},
         {"tipo": "oferta", "producto": "Arándanos", "cantidad": "30 pallets", "precio": "USD 0.95/kg"},
     ]},
    {"id": 2, "nombre": "PackDemo S.A.", "rol": "Packing", "pais": "Chile",
     "descripcion": "Servicios de packing y embalaje.", "email": "info@packdemo.cl", "telefono": "+56 9 6000 0002",
     "items": [
         {"tipo": "servicio", "servicio": "Embalaje y etiquetado", "capacidad": "25.000 cajas/día"},
     ]},
    {"id": 3, "nombre": "FríoDemo Ltda.", "rol": "Frigorífico", "pais": "Chile",
     "descripcion": "Almacenaje refrigerado y logística.", "email": "contacto@friodemo.cl", "telefono": "+56 32 444 5555",
     "items": [
         {"tipo": "servicio", "servicio": "Almacenaje en frío", "capacidad": "1.500 pallets"},
         {"tipo": "servicio", "servicio": "Preenfriado", "capacidad": "6 túneles"},
     ]},
    {"id": 4, "nombre": "OCExport Demo", "rol": "Exportador", "pais": "Chile",
     "descripcion": "Exportador con red en Europa y Asia.", "email": "export@ocexport.cl", "telefono": "+56 9 6000 0003",
     "items": [
         {"tipo": "demanda", "producto": "Cerezas", "cantidad": "200 pallets", "precio": "A convenir"},
     ]},
    {"id": 5, "nombre": "GlobalBuyer Co.", "rol": "Cliente extranjero", "pais": "EEUU",
     "descripcion": "Comprador mayorista en EEUU.", "email": "contact@globalbuyer.com", "telefono": "+1 555 0100",
     "items": [
         {"tipo": "demanda", "producto": "Uva Thompson", "cantidad": "400 pallets", "precio": "A convenir"},
     ]},
]

# Generamos listas separadas para ventas, compras y servicios
ventas = [ (e, it) for e in empresas for it in e["items"] if it["tipo"] == "oferta" ]
compras = [ (e, it) for e in empresas for it in e["items"] if it["tipo"] == "demanda" ]
servicios = [ (e, it) for e in empresas for it in e["items"] if it["tipo"] == "servicio" ]

# ---------------------------
# Carrito (simulación en sesión)
# ---------------------------
def get_cart():
    return session.get("cart", [])

def add_to_cart(item):
    cart = get_cart()
    cart.append(item)
    session["cart"] = cart

# ---------------------------
# Rutas principales
# ---------------------------
@app.route("/")
def home():
    return render_template("landing.html", t=t)

@app.route("/set_lang/<lang>")
def set_lang(lang):
    session["lang"] = lang
    return redirect(request.referrer or url_for("home"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]
        if user in USERS and USERS[user]["password"] == pwd:
            session["user"] = user
            return redirect(url_for("dashboard"))
        return render_template("login.html", error=t("Credenciales inválidas", "Invalid credentials"), t=t)
    return render_template("login.html", t=t)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", t=t, ventas=ventas, compras=compras, servicios=servicios)

@app.route("/perfil")
def perfil():
    if "user" not in session:
        return redirect(url_for("login"))
    # Perfil de ejemplo basado en empresas[0]
    return render_template("perfil.html", perfil=empresas[0], t=t)

@app.route("/empresa/<int:empresa_id>")
def empresa(empresa_id):
    empresa = next((e for e in empresas if e["id"] == empresa_id), None)
    if not empresa:
        return render_template("error.html", code=404, message="Empresa no encontrada", t=t), 404
    return render_template("empresa.html", comp=empresa, es_user=False, t=t)

@app.route("/detalles/ventas")
def detalle_ventas():
    return render_template("detalle_ventas.html", data=ventas, t=t)

@app.route("/detalles/compras")
def detalle_compras():
    return render_template("detalle_compras.html", data=compras, t=t)

@app.route("/detalles/servicios")
def detalle_servicios():
    return render_template("detalle_servicios.html", data=servicios, t=t)

@app.route("/carrito")
def carrito():
    return render_template("carrito.html", cart=get_cart(), t=t)

@app.route("/add_to_cart/<int:empresa_id>/<int:item_id>")
def add_item(empresa_id, item_id):
    empresa = next((e for e in empresas if e["id"] == empresa_id), None)
    if not empresa:
        return redirect(url_for("dashboard"))
    if 0 <= item_id < len(empresa["items"]):
        add_to_cart(empresa["items"][item_id])
    return redirect(url_for("carrito"))

# ---------------------------
# Manejo de errores
# ---------------------------
@app.errorhandler(HTTPException)
def handle_http(e):
    return render_template("error.html", code=e.code, message=e.description, t=t), e.code

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message=t("Error interno", "Internal server error"), t=t), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
