from flask import Flask, render_template, request, redirect, url_for, session, flash
import uuid

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ==== TRADUCCIONES ====
def t(es, en, zh):
    lang = session.get("lang", "es")
    if lang == "en": return en
    if lang == "zh": return zh
    return es

# ==== BASE DE DATOS TEMPORAL ====
usuarios = {
    "exportador1": {"password": "1234", "rol": "Exportador", "rut": "76.123.456-7", "correo": "exp1@mail.com"},
    "planta1": {"password": "1234", "rol": "Planta", "rut": "76.111.111-1", "correo": "planta@mail.com"},
    "packing1": {"password": "1234", "rol": "Packing", "rut": "76.222.222-2", "correo": "packing@mail.com"},
    "frigorifico1": {"password": "1234", "rol": "Frigorífico", "rut": "76.333.333-3", "correo": "frigo@mail.com"},
    "agenciaaduana1": {"password": "1234", "rol": "Agencia de Aduanas", "rut": "76.444.444-4", "correo": "aduana@mail.com"},
    "transporte1": {"password": "1234", "rol": "Transporte", "rut": "76.555.555-5", "correo": "transporte@mail.com"},
    "extraportuario1": {"password": "1234", "rol": "Extraportuario", "rut": "76.666.666-6", "correo": "extra@mail.com"},
    "clienteextranjero1": {"password": "1234", "rol": "Cliente Extranjero", "rut": "N/A", "correo": "cliente@mail.com"},
}

# ==== DETALLES (SEED DATA) ====
detalles = {
    "compra": [
        {"empresa": "ClienteExtranjero1", "item": "Cajas de Ciruelas", "cantidad": "500", "precio": "USD 10.000"},
    ],
    "venta": [
        {"empresa": "Exportador1", "item": "Cajas de Cerezas", "cantidad": "200", "precio": "USD 8.000"},
    ],
    "servicio": [
        {"empresa": "Transporte1", "item": "Flete marítimo Valparaíso - Shanghái", "precio": "USD 3.000"},
        {"empresa": "Packing1", "item": "Servicio de embalaje exportación", "precio": "USD 1.500"},
    ]
}

carritos = {}

# ==== RUTAS PRINCIPALES ====
@app.route("/")
def home():
    return render_template("landing.html", t=t)

@app.route("/set_lang/<code>")
def set_lang(code):
    session["lang"] = code
    return redirect(request.referrer or url_for("home"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"].lower()
        password = request.form["password"]
        if usuario in usuarios and usuarios[usuario]["password"] == password:
            session["usuario"] = usuario
            return redirect(url_for("dashboard"))
        else:
            flash("Usuario o contraseña incorrectos")
    return render_template("login.html", t=t)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))
    user = usuarios[session["usuario"]]
    return render_template("dashboard.html", usuario=user, t=t)

@app.route("/perfil/<empresa>")
def perfil_empresa(empresa):
    if empresa.lower() in usuarios:
        datos = usuarios[empresa.lower()]
        return render_template("empresa.html", empresa=empresa, datos=datos, t=t)
    return redirect(url_for("dashboard"))

@app.route("/detalles/<tipo>")
def detalles_tipo(tipo):
    if tipo not in detalles:
        return redirect(url_for("dashboard"))
    return render_template("accesos.html", tipo=tipo, lista=detalles[tipo], t=t)

@app.route("/carrito/add/<tipo>/<int:index>")
def add_carrito(tipo, index):
    user = session.get("usuario")
    if not user:
        return redirect(url_for("login"))
    if user not in carritos:
        carritos[user] = []
    item = detalles[tipo][index].copy()
    item["id"] = str(uuid.uuid4())
    carritos[user].append(item)
    return redirect(url_for("detalles_tipo", tipo=tipo))

@app.route("/carrito")
def ver_carrito():
    user = session.get("usuario")
    if not user:
        return redirect(url_for("login"))
    return render_template("carrito.html", carrito=carritos.get(user, []), t=t)

# ==== CENTRO DE AYUDA ====
tickets = []

@app.route("/help", methods=["GET","POST"])
def help_center():
    if request.method == "POST":
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        motivo = request.form["motivo"]
        ticket_id = len(tickets)+1
        tickets.append({"id":ticket_id,"nombre":nombre,"correo":correo,"motivo":motivo})
        flash(f"Ticket N°{ticket_id} creado correctamente. Te contactaremos pronto.")
        return redirect(url_for("help_center"))
    return render_template("help.html", tickets=tickets, t=t)

# ==== ERRORES ====
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="Página no encontrada", t=t), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message="Error interno", t=t), 500

if __name__ == "__main__":
    app.run(debug=True)
