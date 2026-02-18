from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path("", views.dashboard, name="dashboard"),
    # Clientes
    path("clientes/", views.cliente_lista, name="cliente_lista"),
    path("clientes/nuevo/", views.cliente_crear, name="cliente_crear"),
    path("clientes/<int:pk>/", views.cliente_detalle, name="cliente_detalle"),
    path("clientes/<int:pk>/editar/", views.cliente_editar, name="cliente_editar"),
    path("clientes/<int:pk>/eliminar/", views.cliente_eliminar, name="cliente_eliminar"),
    # Citas
    path("citas/", views.cita_lista, name="cita_lista"),
    path("citas/nueva/", views.cita_crear, name="cita_crear"),
    path("citas/<int:pk>/", views.cita_detalle, name="cita_detalle"),
    path("citas/<int:pk>/editar/", views.cita_editar, name="cita_editar"),
    path("citas/<int:pk>/eliminar/", views.cita_eliminar, name="cita_eliminar"),
    path("citas/<int:pk>/whatsapp/", views.cita_whatsapp, name="cita_whatsapp"),
    path("citas/<int:pk>/asistencia/", views.registrar_asistencia, name="registrar_asistencia"),
    # Confirmación pública (sin login)
    path("citas/confirmar/<uuid:token>/", views.cita_confirmar, name="cita_confirmar"),
    # Reportes
    path("reportes/asistencia/", views.reporte_asistencia, name="reporte_asistencia"),
]
