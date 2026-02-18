import uuid
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import re


class Cliente(models.Model):
    """Modelo para gestionar clientes."""

    nombre = models.CharField("Nombre completo", max_length=200)
    telefono = models.CharField("Teléfono (WhatsApp)", max_length=20)
    email = models.EmailField("Correo electrónico", blank=True, null=True)
    notas = models.TextField("Notas", blank=True, null=True)
    activo = models.BooleanField("Activo", default=True)
    creado = models.DateTimeField("Fecha de creación", auto_now_add=True)
    actualizado = models.DateTimeField("Última actualización", auto_now=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return f"{self.nombre} - {self.telefono}"

    def telefono_limpio(self):
        """Retorna el teléfono solo con dígitos para WhatsApp."""
        return "".join(filter(str.isdigit, self.telefono))
    
    def clean(self):
        """Validaciones a nivel de modelo."""
        super().clean()
        
        # Validar nombre
        if self.nombre:
            self.nombre = self.nombre.strip()
            if len(self.nombre) < 3:
                raise ValidationError({"nombre": "El nombre debe tener al menos 3 caracteres."})
        
        # Validar teléfono
        if self.telefono:
            telefono_limpio = re.sub(r'\D', '', self.telefono)
            if len(telefono_limpio) < 10:
                raise ValidationError({"telefono": "El teléfono debe tener al menos 10 dígitos."})
    
    def save(self, *args, **kwargs):
        """Override save para ejecutar validaciones."""
        self.full_clean()
        super().save(*args, **kwargs)


class Cita(models.Model):
    """Modelo para gestionar citas."""

    ESTADO_CHOICES = [
        ("pendiente", "Pendiente"),
        ("confirmada", "Confirmada"),
        ("cancelada", "Cancelada"),
        ("completada", "Completada"),
        ("no_asistio", "No asistió"),
    ]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="citas",
        verbose_name="Cliente",
    )
    fecha = models.DateField("Fecha de la cita")
    hora = models.TimeField("Hora de la cita")
    motivo = models.CharField("Motivo", max_length=300)
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=ESTADO_CHOICES,
        default="pendiente",
    )
    token_confirmacion = models.UUIDField(
        "Token de confirmación",
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    asistio = models.BooleanField("¿Asistió?", null=True, blank=True, default=None)
    notas = models.TextField("Notas adicionales", blank=True, null=True)
    creado = models.DateTimeField("Fecha de creación", auto_now_add=True)
    actualizado = models.DateTimeField("Última actualización", auto_now=True)

    class Meta:
        ordering = ["-fecha", "-hora"]
        verbose_name = "Cita"
        verbose_name_plural = "Citas"

    def __str__(self):
        return f"{self.cliente.nombre} - {self.fecha} {self.hora}"

    @property
    def es_pasada(self):
        """Verifica si la cita ya pasó."""
        ahora = timezone.now()
        from datetime import datetime

        fecha_cita = timezone.make_aware(
            datetime.combine(self.fecha, self.hora)
        )
        return ahora > fecha_cita

    @property
    def estado_asistencia(self):
        """Devuelve el estado de asistencia legible."""
        if self.asistio is True:
            return "Asistió"
        elif self.asistio is False:
            return "No asistió"
        elif self.es_pasada and self.estado in ("confirmada", "pendiente"):
            return "Sin confirmar asistencia"
        return "Pendiente"
    
    def clean(self):
        """Validaciones a nivel de modelo."""
        super().clean()
        from datetime import date, datetime
        
        # Validar que la fecha no sea muy antigua
        if self.fecha:
            if self.fecha < date.today():
                raise ValidationError({"fecha": "No puedes crear citas en fechas pasadas."})
        
        # Validar motivo
        if self.motivo:
            self.motivo = self.motivo.strip()
            if len(self.motivo) < 5:
                raise ValidationError({"motivo": "El motivo debe tener al menos 5 caracteres."})
        
        # Validar consistencia de estado y asistencia
        if self.estado == "completada" and self.asistio is None:
            raise ValidationError("Las citas completadas deben tener registro de asistencia.")
        
        if self.estado == "no_asistio" and self.asistio is not False:
            raise ValidationError("El estado 'no asistió' requiere que asistio sea False.")

    def generar_mensaje_whatsapp(self, base_url=""):
        """Genera el mensaje para enviar por WhatsApp."""
        url_confirmacion = f"{base_url}/citas/confirmar/{self.token_confirmacion}/"
        mensaje = (
            f"*Confirmacion de Cita*\n\n"
            f"Hola *{self.cliente.nombre}*,\n\n"
            f"Le recordamos que tiene una cita programada:\n\n"
            f"*Fecha:* {self.fecha.strftime('%d/%m/%Y')}\n"
            f"*Hora:* {self.hora.strftime('%H:%M')}\n"
            f"*Motivo:* {self.motivo}\n\n"
            f"Para confirmar su asistencia, haga clic en el siguiente enlace:\n"
            f"{url_confirmacion}\n\n"
            f"Si no puede asistir, por favor avisenos con anticipacion.\n\n"
            f"Gracias!"
        )
        return mensaje

    def generar_url_whatsapp(self, base_url=""):
        """Genera la URL de WhatsApp Web para enviar el mensaje."""
        import urllib.parse

        mensaje = self.generar_mensaje_whatsapp(base_url)
        telefono = self.cliente.telefono_limpio()
        mensaje_encoded = urllib.parse.quote(mensaje)
        return f"https://wa.me/{telefono}?text={mensaje_encoded}"
