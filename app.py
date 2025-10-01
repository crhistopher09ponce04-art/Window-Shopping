from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

app = Flask(__name__)
app.secret_key = "clave_secreta_super_segura"

# -------------------------------------------------
# Rutas principales
# -------------------------------------------------
@app.route("/")
def home():
    return render_template("landing.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # 🚨 Aquí deberías validar con tu base de datos real
        if username == "exportador1" and password == "1234":
            session["user"] = username
            flash("Inicio de sesión exitoso ✅", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Usuario o contraseña incorrectos ❌", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente 👋", "info")
    return redirect(url_for("home"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user_type = request.form["user_type"]

        # 🚨 Aquí deberías guardar en la base de datos
        flash(f"Usuario {username} registrado exitosamente como {user_type} ✅", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        flash("Debes iniciar sesión para acceder al panel ⚠️", "warning")
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session["user"])

# -------------------------------------------------
# Nueva ruta Centro de Ayuda
# -------------------------------------------------
@app.route("/help")
def help():
    return render_template("help.html")

# -------------------------------------------------
# Manejo de errores
# -------------------------------------------------
@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", code=404, message="Página no encontrada 🚫"), 404

@app.errorhandler(500)
def server_error(error):
    return render_template("error.html", code=500, message="Error interno ⚠️"), 500

# -------------------------------------------------
# Inicialización
# -------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
