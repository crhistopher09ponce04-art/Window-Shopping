import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime
from itertools import count

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# -----------------------------
# i18n mínimo (ES/EN/ZH)
# -----------------------------
LANGS = ["es", "en", "zh"]
DEFAULT_LANG = "es"

STRINGS = {
    "title": {"es": "Window Shopping", "en": "Window Shopping", "zh": "橱窗市场"},
    "login": {"es": "Iniciar sesión", "en": "Log in", "zh": "登录"},
    "register": {"es": "Registrarse", "en": "Register", "zh": "注册"},
    "logout": {"es": "Salir", "en": "Log out", "zh": "退出"},
    "welcome": {
        "es": "Conecta productores, plantas, exportadores y clientes.",
        "en": "Connect producers, plants, exporters and clients.",
        "zh": "连接生产商、工厂、出口商与客户。"
    },
    "hero_cta_login": {"es": "🔐 Ingresar", "en": "🔐 Sign in", "zh": "🔐 登录"},
    "hero_cta_register": {"es": "📝 Registrarse", "en": "📝 Register", "zh": "📝 注册"},
    "forgot": {"es": "¿Olvidaste tu contraseña?", "en": "Forgot your password?", "zh": "忘记密码？"},
    "send_link": {"es": "Enviar enlace", "en": "Send link", "zh": "发送链接"},
    "back": {"es": "Volver", "en": "Back", "zh": "返回"},
    "dashboard": {"es": "Panel", "en": "Dashboard", "zh": "面板"},
    "contact": {"es": "Contáctanos", "en": "Contact us", "zh": "联系我们"},
    "register_choice": {"es": "Elige tu registro", "en": "Choose your sign-up", "zh": "选择注册类型"},
    "national": {"es": "Nacional", "en": "National", "zh": "本地"},
    "foreign": {"es": "Extranjero", "en": "Foreign", "zh": "海外"},
    "services": {"es": "Servicios", "en": "Services", "zh": "服务"},
    "buy": {"es": "Compra", "en": "Buy", "zh": "采购"},
    "sell": {"es": "Venta", "en": "Sell", "zh": "销售"},
    "password_reset_sent": {
        "es": "Hemos enviado un correo con un enlace para restablecer tu contraseña.",
        "en": "We sent an email with a link to reset your password.",
        "zh": "我们已发送重置密码链接到你的邮箱。"
    },
    "password_updated": {
        "es": "Contraseña actualizada. Inicia sesión nuevamente.",
        "en": "Password updated. Please sign in again.",
        "zh": "密码已更新，请重新登录。"
    },
    "ticket_ok": {
        "es": "Tu solicitud fue recibida. Ticket N°",
        "en": "Your request was received. Ticket #",
        "zh": "已收到你的请求。工单号 #"
    },
}

def t(es, en=None, zh=None):
    code = session.get("lang", DEFAULT_LANG)
    # si viene clave, devolver según actual
    if zh is None and en is None:
        # es = clave
        key = es
        bundle = STRINGS.get(key)
        if not bundle:
            return key
        return bundle.get(code, bundle.get("es", key))
    # compat rápido con plantillas antiguas
    if code == "en" and en is not None:
        return en
    if code == "zh" and zh is not None:
        return zh
    return es

@app.context_processor
def inject_helpers():
    return {"t": t, "LANGS": LANGS}

# -----------------------------
# Mock: usuarios demo
# -----------------------------
USERS = {
    "exportador1": {"password": "1234", "rol": "Exportador", "nacional": True},
    "exportador2": {"password": "1234", "rol": "Exportador", "nacional": True},
    "planta1": {"password": "1234", "rol": "Planta", "nacional": True},
    "packing1": {"password": "1234", "rol": "Packing", "nacional": True},
    "frigorifico1": {"password": "1234", "rol": "Frigorífico", "nacional": True},
    "aduana1": {"password": "1234", "rol": "Agencia de aduana", "nacional": True},
    "transporte1": {"password": "1234", "rol": "Transporte", "nacional": True},
    "extraportuario1": {"password": "1234", "rol": "Extraportuario", "nacional": True},
    "cliente1": {"password": "1234", "rol": "Cliente extranjero", "nacional": False},
}

# -----------------------------
# Tickets en memoria (mock)
# -----------------------------
_ticket_counter = count(1)
TICKETS = []  # dicts: {id, email, phone, message, created_at}

# -----------------------------
# Rutas
# -----------------------------
@app.route("/")
def home():
    return render_template("landing.html")

@app.route("/set-lang/<code>")
def set_lang(code):
    if code not in LANGS:
        code = DEFAULT_LANG
    session["lang"] = code
    # volver a la página anterior si existe
    ref = request.headers.get("Referer") or url_for("home")
    return redirect(ref)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        user = USERS.get(username)
        if user and user["password"] == password:
            session["usuario"] = username
            return redirect(url_for("dashboard"))
        error = t("Usuario o contraseña inválidos", "Invalid username or password", "账号或密码无效")
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/register-choice", methods=["GET", "POST"])
def register_choice():
    # Página intermedia: Nacional/Extranjero + modo (servicios/compra/venta)
    if request.method == "POST":
        scope = request.form.get("scope")  # services/buy/sell
        kind = request.form.get("kind")    # national/foreign
        if kind == "national":
            return redirect(url_for("register_national", scope=scope))
        return redirect(url_for("register_foreign", scope=scope))
    return render_template("register_choice.html")

@app.route("/register/national", methods=["GET", "POST"])
def register_national():
    scope = request.args.get("scope", "buy")
    msg = None
    if request.method == "POST":
        # Aquí validaciones reales + subida de PDF RUT (SII)
        # Por ahora mock + flash
        flash(t("Registro nacional enviado para validación.", "National signup submitted for validation.", "本地注册已提交审核。"))
        return redirect(url_for("login"))
    return render_template("register_national.html", scope=scope, msg=msg)

@app.route("/register/foreign", methods=["GET", "POST"])
def register_foreign():
    scope = request.args.get("scope", "buy")
    msg = None
    if request.method == "POST":
        # Aquí validaciones reales + subida de TAX ID (USCI/EORI/etc.)
        flash(t("Registro extranjero enviado para validación.", "Foreign signup submitted for validation.", "海外注册已提交审核。"))
        return redirect(url_for("login"))
    return render_template("register_foreign.html", scope=scope, msg=msg)

@app.route("/password/forgot", methods=["GET", "POST"])
def password_forgot():
    if request.method == "POST":
        email = request.form.get("email")
        # Mock “envío correo”
        flash(t("Hemos enviado un correo con un enlace para restablecer tu contraseña.",
                "We sent an email with a link to reset your password.",
                "我们已向你的邮箱发送重置链接。"))
        return redirect(url_for("password_reset_form", token="demo-token"))
    return render_template("password_reset_request.html")

@app.route("/password/reset/<token>", methods=["GET", "POST"])
def password_reset_form(token):
    if request.method == "POST":
        # Mock: actualizar password del usuario logeado o seleccionado
        flash(t("Contraseña actualizada. Inicia sesión nuevamente.",
                "Password updated. Please sign in again.",
                "密码已更新，请重新登录。"))
        return redirect(url_for("login"))
    return render_template("password_reset_form.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        message = request.form.get("message", "").strip()
        tid = next(_ticket_counter)
        TICKETS.append({
            "id": tid,
            "email": email,
            "phone": phone,
            "message": message,
            "created_at": datetime.utcnow().isoformat()
        })
        flash(f"{t('Tu solicitud fue recibida. Ticket N°', 'Your request was received. Ticket #', '已收到你的请求。工单号 #')} {tid}")
        return redirect(url_for("contact"))
    return render_template("contact.html", tickets=list(reversed(TICKETS[-5:])))

@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))
    username = session["usuario"]
    user = USERS.get(username, {})
    my_company = username.upper()
    return render_template("dashboard.html",
                           usuario=username,
                           rol=user.get("rol", "-"),
                           my_company=my_company)

@app.route("/accesos/<tipo>")
def accesos(tipo):
    # Mock de datos según tipo
    data = []
    if tipo == "ventas":
        data = ["Oferta A", "Oferta B", "Oferta C"]
    elif tipo == "compras":
        data = ["Demanda X", "Demanda Y"]
    elif tipo == "servicios":
        data = ["Transporte Frío", "Agencia Aduana", "Extraportuario"]
    return render_template("accesos.html", tipo=tipo, data=data)

# -----------------------------
# Errores
# -----------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="Página no encontrada"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message=t("Error interno", "Internal server error", "内部错误")), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
