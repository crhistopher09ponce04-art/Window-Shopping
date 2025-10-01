import os, sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, abort

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave_secreta_window_shopping")

DB_PATH = "data.db"

# ---------------------------
# DB helpers
# ---------------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db:
        db.close()

def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        rol TEXT NOT NULL,
        company_id TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS companies (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        city TEXT,
        country TEXT,
        phone TEXT,
        email TEXT
    );
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id TEXT NOT NULL,
        name TEXT NOT NULL,
        variety TEXT,
        measure TEXT NOT NULL,   -- kg | tons | boxes | units
        quantity REAL NOT NULL DEFAULT 0,
        price REAL NOT NULL DEFAULT 0,
        notes TEXT
    );
    """)
    db.commit()

def seed_demo():
    db = get_db()
    has_users = db.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0
    has_companies = db.execute("SELECT COUNT(*) FROM companies").fetchone()[0] > 0
    if not has_companies:
        companies = [
            ("C001","Agrícola Montolín","Productor","Maule","Chile","+56 9 8765 4321","ventas@montolin.cl"),
            ("C002","Planta Ejemplo","Planta","Talca","Chile","+56 9 5555 5555","planta@ejemplo.cl"),
            ("C003","Pukiyai Packing","Packing","Rancagua","Chile","+56 2 2345 6789","info@pukiyai.cl"),
            ("C004","Frigo Sur","Frigorífico","Curicó","Chile","+56 72 222 3333","contacto@frigosur.cl"),
            ("C005","Tuniche Fruit","Exportador","Valparaíso","Chile","+56 9 8123 4567","contacto@tuniche.cl"),
            ("X001","Chensen Ogen Ltd.","Cliente extranjero","Shenzhen","China","+86 138 0000 1111","chen@ogen.cn"),
            ("S001","Transporte Andes","Transporte","Santiago","Chile","+56 2 3456 7890","contacto@transporteandes.cl"),
            ("S002","Aduanas Chile Ltda.","Agencia de aduana","Valparaíso","Chile","+56 2 9999 1111","aduana@chile.cl"),
            ("S003","Puerto Seco SA","Extraportuario","San Antonio","Chile","+56 35 1234 567","info@puertoseco.cl"),
        ]
        db.executemany("INSERT INTO companies VALUES (?,?,?,?,?,?,?)", companies)
        db.commit()
    if not has_users:
        users = [
            ("productor1","1234","Productor","C001"),
            ("planta1","1234","Planta","C002"),
            ("packing1","1234","Packing","C003"),
            ("frigorifico1","1234","Frigorífico","C004"),
            ("exportador1","1234","Exportador","C005"),
            ("cliente1","1234","Cliente extranjero","X001"),
            ("transporte1","1234","Transporte","S001"),
            ("aduana1","1234","Agencia de aduana","S002"),
            ("extraportuario1","1234","Extraportuario","S003"),
        ]
        db.executemany("INSERT INTO users VALUES (?,?,?,?)", users)
        db.commit()
    # si no hay items, cargamos algunos demo
    has_items = get_db().execute("SELECT COUNT(*) FROM items").fetchone()[0] > 0
    if not has_items:
        items = [
            ("C001","Ciruela","Black Diamond","tons",50,400,"Calibre 50+, buena condición"),
            ("C003","Ciruela","Black Amber","tons",40,420,"Packing rápido y controlado"),
            ("C004","Frío","Servicio Frigorífico","units",1,16500,"Espacio disponible 60 tons"),
            ("C005","Ciruela","Angeleno","tons",30,380,"Listo para exportar"),
            ("S001","Transporte","Camión Reefer","units",1,0,"Rutas centro-sur"),
            ("S002","Agenciamiento","Despacho aduana","units",1,0,"Documentación completa"),
        ]
        db.executemany(
            "INSERT INTO items(company_id,name,variety,measure,quantity,price,notes) VALUES (?,?,?,?,?,?,?)",
            items
        )
        db.commit()

# ---------------------------
# Idiomas simples
# ---------------------------
LANGS = {"es": "Español", "en": "English"}

def get_lang():
    lang = session.get("lang","es")
    return lang if lang in LANGS else "es"

def tr(key):
    lang = get_lang()
    STR = {
        "es": {
            "home_title": "Plataforma B2B de fruta y servicios",
            "login": "Iniciar Sesión",
            "logout": "Cerrar Sesión",
            "dashboard": "Panel",
            "profile": "Mi Perfil",
            "explore": "Explorar Mercado",
            "cart": "Carrito",
            "help": "Centro de Ayuda",
            "register": "Registro",
            "back": "Volver"
        },
        "en": {
            "home_title": "B2B platform for produce & services",
            "login": "Log In",
            "logout": "Log Out",
            "dashboard": "Dashboard",
            "profile": "My Profile",
            "explore": "Explore Market",
            "cart": "Cart",
            "help": "Help Center",
            "register": "Register",
            "back": "Back"
        }
    }
    return STR.get(lang, STR["es"]).get(key, key)

@app.context_processor
def inject_globals():
    # Nota: '_' queda disponible por compatibilidad. Si pasas un string, lo devuelve tal cual.
    return {"LANGS": LANGS, "cur_lang": get_lang(), "tr": tr, "_": lambda s: s}

@app.route("/lang/<code>")
def set_lang(code):
    session["lang"] = code if code in LANGS else "es"
    return redirect(request.args.get("next") or url_for("home"))

# ---------------------------
# Utilidades
# ---------------------------
def require_login():
    if "usuario" not in session:
        flash("Inicia sesión para continuar.")
        return False
    return True

def next_company_id():
    db = get_db()
    n = db.execute("SELECT COUNT(*) FROM companies").fetchone()[0] + 1
    return f"C{n:03d}"

# ---------------------------
# Rutas públicas
# ---------------------------
@app.route("/")
def home():
    if "usuario" in session:
        return redirect(url_for("dashboard"))
    return render_template("landing.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    u = (request.form.get("username") or "").strip()
    p = (request.form.get("password") or "").strip()
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username=?", (u,)).fetchone()
    if user and user["password"] == p:
        session["usuario"] = u
        session["rol"] = user["rol"]
        session["company_id"] = user["company_id"]
        session.setdefault("cart", [])
        flash("¡Bienvenido!")
        return redirect(url_for("dashboard"))
    return render_template("login.html", error="Usuario o contraseña incorrectos")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    # crear user + company
    db = get_db()
    username = (request.form.get("username") or "").strip()
    password = (request.form.get("password") or "").strip()
    rol = request.form.get("rol")
    name = (request.form.get("name") or "").strip()
    city = (request.form.get("city") or "").strip()
    country = (request.form.get("country") or "").strip()
    phone = (request.form.get("phone") or "").strip()
    email = (request.form.get("email") or "").strip()

    if not username or not password or not rol or not name:
        return render_template("register.html", error="Completa los campos obligatorios.")

    exists = db.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone()
    if exists:
        return render_template("register.html", error="Ese usuario ya existe.")

    cid = next_company_id()
    db.execute("INSERT INTO companies(id,name,role,city,country,phone,email) VALUES (?,?,?,?,?,?,?)",
               (cid, name, rol, city, country, phone, email))
    db.execute("INSERT INTO users(username,password,rol,company_id) VALUES (?,?,?,?)",
               (username, password, rol, cid))
    db.commit()
    flash("Cuenta creada, ya puedes iniciar sesión.")
    return redirect(url_for("login"))

@app.route("/help")
def help_center():
    return render_template("help_center.html")

@app.route("/manual")
def manual():
    return render_template("manual.html")

# ---------------------------
# Rutas privadas
# ---------------------------
@app.route("/dashboard")
def dashboard():
    if not require_login(): return redirect(url_for("home"))
    db = get_db()
    me = db.execute("SELECT * FROM companies WHERE id=?", (session["company_id"],)).fetchone()
    my_items = db.execute("SELECT * FROM items WHERE company_id=? ORDER BY id DESC", (session["company_id"],)).fetchall()
    return render_template("dashboard.html", me=me, items=my_items, usuario=session["usuario"], rol=session["rol"])

@app.route("/mi-perfil", methods=["GET","POST"])
def mi_perfil():
    if not require_login(): return redirect(url_for("home"))
    db = get_db()
    cid = session["company_id"]
    company = db.execute("SELECT * FROM companies WHERE id=?", (cid,)).fetchone()
    if request.method == "POST":
        db.execute("""UPDATE companies SET name=?, city=?, country=?, phone=?, email=? WHERE id=?""",
                   (request.form.get("name"), request.form.get("city"), request.form.get("country"),
                    request.form.get("phone"), request.form.get("email"), cid))
        db.commit()
        flash("Perfil actualizado.")
        return redirect(url_for("mi_perfil"))
    my_items = db.execute("SELECT * FROM items WHERE company_id=? ORDER BY id DESC", (cid,)).fetchall()
    return render_template("mi_perfil.html", company=company, items=my_items)

@app.route("/mi-perfil/items", methods=["POST"])
def add_item():
    if not require_login(): return redirect(url_for("home"))
    db = get_db()
    name = request.form.get("name")
    variety = request.form.get("variety")
    measure = request.form.get("measure") or "kg"
    try:
        quantity = float(request.form.get("quantity") or 0)
    except:
        quantity = 0
    try:
        price = float(request.form.get("price") or 0)
    except:
        price = 0
    notes = request.form.get("notes")
    if not name:
        flash("El producto/servicio es obligatorio.")
        return redirect(url_for("mi_perfil"))
    db.execute("""INSERT INTO items(company_id,name,variety,measure,quantity,price,notes)
                  VALUES (?,?,?,?,?,?,?)""",
               (session["company_id"], name, variety, measure, quantity, price, notes))
    db.commit()
    flash("Ítem agregado.")
    return redirect(url_for("mi_perfil"))

@app.route("/mi-perfil/items/<int:item_id>/delete", methods=["POST"])
def delete_item(item_id):
    if not require_login(): return redirect(url_for("home"))
    db = get_db()
    # seguridad: que sea mío
    owner = db.execute("SELECT company_id FROM items WHERE id=?", (item_id,)).fetchone()
    if not owner: abort(404)
    if owner["company_id"] != session["company_id"]:
        abort(403)
    db.execute("DELETE FROM items WHERE id=?", (item_id,))
    db.commit()
    flash("Ítem eliminado.")
    return redirect(url_for("mi_perfil"))

@app.route("/explorar")
def explorar():
    if not require_login(): return redirect(url_for("home"))
    db = get_db()
    q = (request.args.get("q") or "").strip().lower()
    role = (request.args.get("role") or "").strip()
    measure = (request.args.get("measure") or "").strip()
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")

    params = []
    sql = """
        SELECT i.*, c.name as company_name, c.role as company_role, c.city, c.country
        FROM items i JOIN companies c ON c.id = i.company_id
        WHERE i.company_id != ?
    """
    params.append(session["company_id"])

    if q:
        sql += " AND (LOWER(i.name) LIKE ? OR LOWER(i.variety) LIKE ? OR LOWER(c.name) LIKE ? OR LOWER(c.city) LIKE ? OR LOWER(c.country) LIKE ?)"
        like = f"%{q}%"
        params += [like, like, like, like, like]

    if role:
        sql += " AND c.role = ?"
        params.append(role)

    if measure:
        sql += " AND i.measure = ?"
        params.append(measure)

    def to_float(v):
        try: return float(v)
        except: return None

    lo = to_float(min_price)
    hi = to_float(max_price)
    if lo is not None:
        sql += " AND i.price >= ?"
        params.append(lo)
    if hi is not None:
        sql += " AND i.price <= ?"
        params.append(hi)

    sql += " ORDER BY i.id DESC"
    rows = db.execute(sql, tuple(params)).fetchall()

    # opciones de filtros
    roles = [r[0] for r in db.execute("SELECT DISTINCT role FROM companies ORDER BY role").fetchall()]
    return render_template("explorar.html", items=rows, roles=roles, values=request.args)

@app.route("/detalle/<int:item_id>", methods=["GET","POST"])
def detalle(item_id):
    if not require_login(): return redirect(url_for("home"))
    db = get_db()
    item = db.execute("""
        SELECT i.*, c.name as company_name, c.role as company_role, c.city, c.country, c.phone, c.email
        FROM items i JOIN companies c ON c.id = i.company_id
        WHERE i.id=?
    """, (item_id,)).fetchone()
    if not item: abort(404)
    if request.method == "POST":
        cart = session.get("cart", [])
        cart.append({
            "item_id": item["id"],
            "company_id": item["company_id"],
            "name": item["name"],
            "variety": item["variety"],
            "measure": item["measure"],
            "quantity": request.form.get("quantity") or "1",
            "price": item["price"],
            "company_name": item["company_name"]
        })
        session["cart"] = cart
        flash("Agregado al carrito.")
        return redirect(url_for("cart"))
    return render_template("detalle.html", item=item)

@app.route("/cart", methods=["GET","POST"])
def cart():
    if not require_login(): return redirect(url_for("home"))
    if request.method == "POST":
        action = request.form.get("action")
        if action == "clear":
            session["cart"] = []
            flash("Carrito vaciado.")
        elif action == "checkout":
            session["cart"] = []
            flash("¡Solicitud enviada! Te contactaremos a la brevedad.")
            return redirect(url_for("dashboard"))
        elif action and action.startswith("remove:"):
            idx = int(action.split(":")[1])
            cart = session.get("cart", [])
            if 0 <= idx < len(cart):
                cart.pop(idx)
            session["cart"] = cart
            flash("Ítem eliminado.")
    return render_template("cart.html", cart=session.get("cart", []))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ---------------------------
# Errores
# ---------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="Recurso no encontrado"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message="Error interno"), 500

# ---------------------------
# Start
# ---------------------------
if __name__ == "__main__":
    with app.app_context():
        init_db()
        seed_demo()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
