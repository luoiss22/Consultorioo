# Sistema de Gestion de Citas

Sistema web para gestionar citas medicas/consultas con confirmacion de pacientes via WhatsApp.

## Caracteristicas

- Gestion de clientes (pacientes)
- Creacion y administracion de citas
- Confirmacion publica de citas (sin login)
- Envio de confirmaciones via WhatsApp
- Registro de asistencia
- Dashboard con estadisticas
- Reportes de asistencia
- Validaciones completas de datos

## Requisitos

- Python 3.8+
- Django 4.2+

## Instalacion

1. **Clonar el repositorio**
```bash
git clone <tu-repositorio>
cd luwi
```

2. **Crear entorno virtual**
```bash
python -m venv venv
```

3. **Activar entorno virtual**

Windows:
```bash
.\venv\Scripts\Activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

4. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

5. **Ejecutar migraciones**
```bash
python manage.py migrate
```

6. **Crear superusuario**
```bash
python manage.py createsuperuser
```

7. **Ejecutar servidor**
```bash
python manage.py runserver
```

8. **Abrir en navegador**
```
http://127.0.0.1:8000/
```

## Usuarios por Defecto

- **Usuario**: admin
- **Contraseña**: admin

ADVERTENCIA: Cambiar en produccion!

## Uso

### Crear una Cita

1. Login con credenciales de admin
2. Ir a "Clientes" -> Crear nuevo cliente
3. Ir a "Citas" -> Crear nueva cita
4. Seleccionar cliente, fecha, hora y motivo

### Enviar Confirmacion por WhatsApp

1. Abrir detalle de la cita
2. Hacer clic en boton "Enviar por WhatsApp"
3. Se abrira WhatsApp Web con mensaje pre-llenado
4. Enviar mensaje al paciente

### Confirmacion del Paciente

El paciente recibe un link unico que abre una pagina donde puede:
- Confirmar su asistencia
- Cancelar la cita

No requiere login ni registro.

### Registrar Asistencia

Despues de la cita:
1. Ir al detalle de la cita
2. Clic en "Registrar asistencia"
3. Marcar si asistio o no

## Validaciones Implementadas

### Clientes
- Nombre: minimo 3 caracteres, solo letras
- Telefono: minimo 10 digitos, maximo 15
- Email: formato valido

### Citas
- Fecha: no puede ser del pasado
- Fecha: maximo 1 año en el futuro
- Horario: solo entre 8:00 AM y 8:00 PM
- Motivo: minimo 5 caracteres
- No permite citas duplicadas (mismo cliente, fecha y hora)
- Minimo 30 minutos entre citas del mismo cliente
- Proteccion contra eliminacion de clientes con citas futuras
- No permite registrar asistencia para citas futuras

## Funcionalidades

### Dashboard
- Citas de hoy
- Citas pendientes
- Citas confirmadas
- Total de clientes activos
- Proximas citas (7 dias)

### Reportes
- Filtros por fecha, estado, cliente
- Estadisticas de asistencia
- Porcentaje de asistencia
- Citas sin confirmar asistencia

## WhatsApp

El sistema NO envia mensajes automaticamente. Funciona asi:

1. Genera un link unico de confirmacion
2. Abre WhatsApp Web con mensaje pre-llenado
3. El administrador envia el mensaje manualmente
4. El paciente recibe el link y puede confirmar/cancelar

**Formato de telefono**: Incluir codigo de pais
- Ejemplo Mexico: `5215551234567`
- Ejemplo USA: `15551234567`

## Seguridad

- Login requerido para area administrativa
- Tokens unicos (UUID) para confirmaciones publicas
- Validaciones en formularios y modelos
- Proteccion CSRF
- Proteccion XSS
- Validaciones de fecha/hora
- No permite modificar registros historicos

## Estructura del Proyecto

```
luwi/
├── citas/              # App principal
│   ├── models.py       # Modelos (Cliente, Cita)
│   ├── views.py        # Vistas y logica
│   ├── forms.py        # Formularios con validaciones
│   ├── urls.py         # URLs de la app
│   └── templates/      # Templates HTML
├── config/             # Configuracion Django
│   ├── settings.py     # Configuracion principal
│   └── urls.py         # URLs principales
├── templates/          # Templates globales
├── static/             # Archivos estaticos
├── manage.py           # Comando Django
└── requirements.txt    # Dependencias
```

## Despliegue

Para desplegar en produccion:

1. Cambiar `DEBUG = False` en settings.py
2. Configurar `ALLOWED_HOSTS`
3. Cambiar `SECRET_KEY`
4. Configurar base de datos (PostgreSQL recomendado)
5. Configurar archivos estaticos
6. Usar gunicorn/uwsgi
7. Configurar HTTPS

## Notas

- Zona horaria configurada: America/Mexico_City
- Idioma: Español
- Base de datos: SQLite (desarrollo)

## Problemas Conocidos

- El envio de WhatsApp requiere WhatsApp Web activo
- Los mensajes no se envian automaticamente
- Requiere conexion a internet para WhatsApp

## Desarrollo

Proyecto escolar - Sistema de gestion de citas

## Licencia

Proyecto educativo

