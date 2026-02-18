# Guia de Despliegue - Sistema de Citas

## MEJOR OPCION GRATIS PARA PROYECTO ESCOLAR: PYTHONANYWHERE

**PythonAnywhere es la mejor opcion para proyectos escolares:**
- Plan 100% GRATIS permanente
- Base de datos MySQL incluida GRATIS
- Facil configuracion
- No requiere tarjeta de credito
- Perfecto para proyectos pequeños/medianos
- 512MB de almacenamiento
- Dominio: tunombre.pythonanywhere.com

**IMPORTANTE**: Vercel NO funciona para Django (solo para frontend/Next.js)

---

## Tutorial Completo: PythonAnywhere (GRATIS)

### Paso 1: Crear cuenta

1. Ir a: https://www.pythonanywhere.com
2. Click en "Pricing & signup"
3. Seleccionar plan "Beginner" (FREE)
4. Registrarte con email

### Paso 2: Subir tu codigo

Opcion A - Usando Git (recomendado):

1. En PythonAnywhere, ir a "Consoles" > "Bash"
2. Clonar tu repositorio:
```bash
git clone https://github.com/tu-usuario/luwi.git
cd luwi
```

Opcion B - Subir archivos manualmente:
1. Ir a "Files"
2. Crear carpeta "luwi"
3. Subir todos tus archivos

### Paso 3: Configurar entorno virtual

En la consola Bash:
```bash
cd luwi
mkvirtualenv --python=/usr/bin/python3.10 luwi-env
pip install -r requirements.txt
```

### Paso 4: Configurar base de datos MySQL (GRATIS)

1. Ir a "Databases"
2. Click en "Initialize MySQL"
3. Crear password
4. Anotar: 
   - Database name: `tunombre$default`
   - Host: `tunombre.mysql.pythonanywhere-services.com`

5. Editar `config/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tunombre$default',
        'USER': 'tunombre',
        'PASSWORD': 'tu-password-mysql',
        'HOST': 'tunombre.mysql.pythonanywhere-services.com',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

# Agregar estos para produccion:
ALLOWED_HOSTS = ['tunombre.pythonanywhere.com']
DEBUG = False
```

6. Instalar conector MySQL:
```bash
pip install mysqlclient
```

### Paso 5: Ejecutar migraciones

```bash
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
```

### Paso 6: Configurar Web App

1. Ir a "Web"
2. Click "Add a new web app"
3. Seleccionar "Manual configuration"
4. Python 3.10
5. En la configuracion de la web app:

**Code section:**
- Source code: `/home/tunombre/luwi`
- Working directory: `/home/tunombre/luwi`

**Virtualenv section:**
- `/home/tunombre/.virtualenvs/luwi-env`

**Static files section:**
Agregar:
- URL: `/static/` 
- Directory: `/home/tunombre/luwi/staticfiles`

### Paso 7: Editar archivo WSGI

1. Click en el link del archivo WSGI
2. Borrar todo y reemplazar con:

```python
import os
import sys

# Path de tu proyecto
path = '/home/tunombre/luwi'
if path not in sys.path:
    sys.path.append(path)

# Configurar Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

3. Guardar

### Paso 8: Reload y probar

1. Click en el boton verde "Reload tunombre.pythonanywhere.com"
2. Visitar: https://tunombre.pythonanywhere.com
3. Login con tu superuser

LISTO! Tu app esta en linea!

---

## Alternativa: Railway (tambien gratis pero requiere tarjeta)

### Caracteristicas:
- $5 USD credito gratis mensual
- PostgreSQL incluido
- Deploy automatico desde GitHub
- Requiere tarjeta de credito (no cobra si no pasas el credito)

### Pasos rapidos:

1. Crear cuenta: https://railway.app
2. "New Project" > "Deploy from GitHub repo"
3. Seleccionar tu repo
4. Agregar PostgreSQL desde "New Service"
5. Variables de entorno automaticas
6. Deploy automatico

**Nota**: Railway te da $5/mes gratis, suficiente para proyectos escolares

---

## Por que NO usar Vercel para este proyecto?

**Vercel NO funciona para Django** porque:
- Vercel es para aplicaciones serverless (Node.js, Next.js, Python functions)
- Django necesita un servidor persistente
- No soporta WebSockets persistentes
- No tiene base de datos relacional incluida

Vercel es para:
- Frontend (React, Vue, Next.js)
- APIs serverless
- Sitios estaticos

Django necesita:
- Servidor tradicional (como PythonAnywhere, Railway, Heroku)
- Base de datos persistente
- Almacenamiento de archivos

---

## Resumen de opciones GRATIS:

| Plataforma | Gratis? | Base de Datos | Dificultad | Recomendado |
|-----------|---------|---------------|------------|-------------|
| PythonAnywhere | SI | MySQL gratis | Facil | SI - MEJOR |
| Railway | $5/mes credito | PostgreSQL | Facil | SI |
| Render | 750 hrs/mes | PostgreSQL | Media | SI |
| Heroku | NO (desde 2022) | - | - | NO |
| Vercel | NO para Django | - | - | NO |

---

## Cambios necesarios para produccion

Agregar a `requirements.txt`:
```
mysqlclient>=2.2.0
```

En `config/settings.py`:
```python
# Seguridad
SECURE_SSL_REDIRECT = False  # PythonAnywhere ya usa HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Para servir archivos estaticos
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
```

---

## Solucion de problemas comunes

### Error: "DisallowedHost"
Agregar tu dominio a ALLOWED_HOSTS en settings.py

### Error: "No module named mysqlclient"
```bash
pip install mysqlclient
```

### Error: "Static files not found"
```bash
python manage.py collectstatic --noinput
```

### La web se ve sin estilos
Verificar configuracion de Static files en PythonAnywhere

---

## Actualizar codigo en PythonAnywhere

1. Ir a consola Bash
2. ```bash
   cd luwi
   git pull
   ```
3. Si hay cambios en modelos:
   ```bash
   python manage.py migrate
   ```
4. Si hay cambios en archivos estaticos:
   ```bash
   python manage.py collectstatic --noinput
   ```
5. Ir a "Web" > Click "Reload"

---

## Recomendacion final

**Para proyecto escolar**: USA PYTHONANYWHERE
- 100% gratis
- No requiere tarjeta
- MySQL incluido
- Facil de configurar
- Suficiente para demostracion

Tu URL sera: `https://tunombre.pythonanywhere.com`
