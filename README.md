# Window Shopping

Plataforma B2B de exportación de frutas y servicios logísticos.  
Demo académico para mostrar un marketplace con perfiles de usuarios, compra/venta y servicios.

---

## 🚀 Usuarios de prueba

- productor1 / 1234  
- planta1 / 1234  
- packing1 / 1234  
- frigorifico1 / 1234  
- exportador1 / 1234  
- cliente1 / 1234  

---

## 📦 Despliegue en Render

1. Subir este repositorio a GitHub.  
2. Conectar a **Render → New → Blueprint**.  
3. Render detectará el archivo `render.yaml` automáticamente.  
4. Render instalará las dependencias de `requirements.txt`.  
5. Se ejecutará la app con `gunicorn app:app`.  
6. En **Environment Variables**, agregar la variable:
   - `SECRET_KEY=super_segura_123456`

---

## ▶️ Ejecución local (opcional)

Si quieres probar en tu computador:  

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la app
python app.py
