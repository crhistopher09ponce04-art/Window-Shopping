# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, session, abort

# Crear la aplicación Flask
app = Flask(__name__)

# Clave secreta (usa la variable de entorno de Render o un valor por defecto)
app.secret_key = os.environ.get("SECRET_KEY", "clave_secreta_window_shopping")

# Ruta principal
@app.route("/")
def home():
    return render_template("login.html")  # asegúrate que login.html está en la carpeta "templates"

# Iniciar la aplicación en el puerto que Render asigna automáticamente
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render define el puerto
    app.run(host="0.0.0.0", port=port, debug=True)
