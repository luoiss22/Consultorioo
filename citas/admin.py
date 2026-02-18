from django.contrib import admin
from .models import Cliente, Cita


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "telefono", "email", "activo", "creado")
    search_fields = ("nombre", "telefono", "email")
    list_filter = ("activo",)


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ("cliente", "fecha", "hora", "motivo", "estado", "asistio")
    search_fields = ("cliente__nombre", "motivo")
    list_filter = ("estado", "asistio", "fecha")
    date_hierarchy = "fecha"
