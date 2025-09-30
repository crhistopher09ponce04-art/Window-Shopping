# Window Shopping – Demo Flask (Render)

Plataforma B2B (demo) según mockups: login/registro, panel por rol y listados de compras/ventas.

## Usuarios de prueba
- productor1 / 1234
- planta1 / 1234
- packing1 / 1234
- frigorifico1 / 1234
- exportador1 / 1234
- cliente1 / 1234

## Estructura
```
app.py
requirements.txt
render.yaml
.gitignore
templates/
static/
```

## Despliegue en Render (Blueprint recomendado)
1. Subir este repo a GitHub con los archivos **en la raíz**.
2. En Render → **New → Blueprint** → seleccionar el repo.
3. En el servicio, ir a **Environment** y definir `SECRET_KEY` con una cadena segura.
4. Render ejecuta:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:app`
5. Abrir la URL pública que Render entregue.

## Notas
- `SECRET_KEY` se toma desde variable de entorno (local usa un valor por defecto).
- Datos y usuarios son en memoria (demo). Para persistencia, agregaremos PostgreSQL.
