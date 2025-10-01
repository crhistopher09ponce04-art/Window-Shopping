import os, sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, abort

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave_secreta_window_shopping")

DB_PATH = "data.db"

# -----------------------
# Conexión DB
# -----------------------
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
        password TEXT,
        rol TEXT,
        company_id TEXT
    );
    CREATE TABLE IF NOT EXISTS companies (
        id TEXT PRIMARY KEY,
        name TEXT, role TEXT, city TEXT, country TEXT,
        phone TEXT, email TEXT
    );
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id TEXT,
        name TEXT,
        variety TEXT,
        measure TEXT,
        quantity REAL,
        price REAL,
        notes TEXT
    );
    """)
    db.commit()

def seed_demo():
    db = get_db()
    if db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        demo_users = [
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
        demo_companies = [
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
        db.executemany("INSERT INTO users VALUES (?,?,?,?)", demo_users)
        db.executemany("INSERT INTO companies VALUES (?,?,?,?,?,?,?)", demo_companies)
        db.commit()

# -----------------------
# Idiomas
# -----------------------
LANGS = {"es": "Español", "en": "English"}
translations = {
    "home_title": {"es": "Bienvenido a Window Shopping", "en": "Welcome to Window Shopping"},
    "login": {"es": "Iniciar Sesión", "en": "Log In"},
    "logout": {"es": "Cerrar Sesión", "en": "Log Out"},
    "cart": {"es": "Carrito", "en": "Cart"},
    "profile": {"es": "Mi Perfil", "en": "My Profile"},
}

def get_lang():
    lang = session.get("lang","es")
    return lang if lang in LANGS else "es"

def t(key):
    lang = get_lang()
    return translations.get(key, {}).get(lang, key)

@app.context_processor
def inject_globals():
    return {"LANGS":LANGS,"cur_lang":get_lang(),"t":t}

@app.route("/lang/<code>")
def set_lang(code):
    session["lang"]=code if code in LANGS else "es"
    return redirect(request.args.get("next") or url_for("home"))

# -----------------------
# Helpers
# -----------------------
def require_login():
    if "usuario" not in session:
        flash("Inicia sesión primero.")
        return False
    return True

# -----------------------
# Rutas
# -----------------------
@app.route("/")
def home():
    if "usuario" in session:
        return redirect(url_for("dashboard"))
    return render_template("landing.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="GET":
        return render_template("login.html")
    u,p = request.form["username"], request.form["password"]
    db=get_db()
    user=db.execute("SELECT * FROM users WHERE username=?",(u,)).fetchone()
    if user and user["password"]==p:
        session["usuario"]=u
        session["rol"]=user["rol"]
        session["company_id"]=user["company_id"]
        session.setdefault("cart",[])
        return redirect(url_for("dashboard"))
    return render_template("login.html",error="Credenciales incorrectas")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if not require_login(): return redirect(url_for("home"))
    db=get_db()
    my_company=db.execute("SELECT * FROM companies WHERE id=?",(session["company_id"],)).fetchone()
    items=db.execute("SELECT * FROM items WHERE company_id=?",(session["company_id"],)).fetchall()
    return render_template("dashboard.html", usuario=session["usuario"], rol=session["rol"], my_company=my_company, items=items)

@app.route("/mi-perfil", methods=["GET","POST"])
def mi_perfil():
    if not require_login(): return redirect(url_for("home"))
    db=get_db()
    cid=session["company_id"]
    c=db.execute("SELECT * FROM companies WHERE id=?",(cid,)).fetchone()
    if request.method=="POST":
        db.execute("""UPDATE companies SET name=?,city=?,country=?,phone=?,email=? WHERE id=?""",
                   (request.form["name"],request.form["city"],request.form["country"],request.form["phone"],request.form["email"],cid))
        db.commit()
        flash("Perfil actualizado.")
        return redirect(url_for("mi_perfil"))
    return render_template("mi_perfil.html",company=c)

@app.route("/mi-perfil/items",methods=["POST"])
def add_item():
    if not require_login(): return redirect(url_for("home"))
    db=get_db()
    db.execute("INSERT INTO items(company_id,name,variety,measure,quantity,price,notes) VALUES (?,?,?,?,?,?,?)",
               (session["company_id"],request.form["name"],request.form["variety"],request.form["measure"],request.form["quantity"],request.form["price"],request.form["notes"]))
    db.commit()
    flash("Item agregado.")
    return redirect(url_for("mi_perfil"))

@app.route("/detalle/<int:item_id>",methods=["GET","POST"])
def detalle(item_id):
    if not require_login(): return redirect(url_for("home"))
    db=get_db()
    item=db.execute("SELECT i.*,c.name as company_name FROM items i JOIN companies c ON i.company_id=c.id WHERE i.id=?",(item_id,)).fetchone()
    if not item: abort(404)
    if request.method=="POST":
        cart=session.get("cart",[])
        cart.append(dict(item))
        session["cart"]=cart
        flash("Agregado al carrito.")
        return redirect(url_for("cart"))
    return render_template("detalle.html",item=item)

@app.route("/cart",methods=["GET","POST"])
def cart():
    if not require_login(): return redirect(url_for("home"))
    if request.method=="POST":
        if request.form.get("action")=="clear": session["cart"]=[]
        elif request.form.get("action")=="checkout":
            session["cart"]=[]
            flash("Pedido enviado.")
            return redirect(url_for("dashboard"))
    return render_template("cart.html",cart=session.get("cart",[]))

@app.route("/help")
def help_center():
    return render_template("help_center.html")

@app.route("/manual")
def manual():
    return render_template("manual.html")

# -----------------------
# Start
# -----------------------
if __name__=="__main__":
    with app.app_context():
        init_db()
        seed_demo()
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)),debug=True)
