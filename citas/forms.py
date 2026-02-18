from django import forms
from django.utils import timezone
from datetime import date, timedelta, time
import re
from .models import Cliente, Cita


class ClienteForm(forms.ModelForm):
    """Formulario para crear/editar clientes."""

    class Meta:
        model = Cliente
        fields = ["nombre", "telefono", "email", "notas", "activo"]
        widgets = {
            "nombre": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre completo"}
            ),
            "telefono": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: 521234567890 (con código de país)",
                }
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "correo@ejemplo.com"}
            ),
            "notas": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Notas sobre el cliente...",
                }
            ),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
    
    def clean_nombre(self):
        """Validar nombre del cliente."""
        nombre = self.cleaned_data.get("nombre", "").strip()
        if not nombre:
            raise forms.ValidationError("El nombre es obligatorio.")
        if len(nombre) < 3:
            raise forms.ValidationError("El nombre debe tener al menos 3 caracteres.")
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$", nombre):
            raise forms.ValidationError("El nombre solo puede contener letras y espacios.")
        return nombre
    
    def clean_telefono(self):
        """Validar formato de teléfono."""
        telefono = self.cleaned_data.get("telefono", "").strip()
        # Eliminar espacios, guiones, paréntesis
        telefono_limpio = re.sub(r"[\s\-\(\)]+", "", telefono)
        
        # Verificar que solo tenga dígitos y +
        if not re.match(r"^\+?\d+$", telefono_limpio):
            raise forms.ValidationError("El teléfono solo puede contener números y el símbolo +")
        
        # Verificar longitud (mínimo 10 dígitos)
        digitos = re.sub(r"\D", "", telefono_limpio)
        if len(digitos) < 10:
            raise forms.ValidationError("El teléfono debe tener al menos 10 dígitos.")
        if len(digitos) > 15:
            raise forms.ValidationError("El teléfono no puede tener más de 15 dígitos.")
        
        return telefono_limpio
    
    def clean_email(self):
        """Validar email si se proporciona."""
        email = self.cleaned_data.get("email", "").strip().lower()
        if email:
            # Verificar formato básico
            if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
                raise forms.ValidationError("Ingrese un correo electrónico válido.")
        return email if email else None


class CitaForm(forms.ModelForm):
    """Formulario para crear/editar citas."""
    
    # Horarios de trabajo
    HORA_INICIO = time(8, 0)  # 8:00 AM
    HORA_FIN = time(20, 0)    # 8:00 PM
    DIAS_MAXIMOS_FUTURO = 365  # 1 año

    class Meta:
        model = Cita
        fields = ["cliente", "fecha", "hora", "motivo", "notas"]
        widgets = {
            "cliente": forms.Select(attrs={"class": "form-select"}),
            "fecha": forms.DateInput(
                attrs={"class": "form-control", "type": "date"},
                format="%Y-%m-%d",
            ),
            "hora": forms.TimeInput(
                attrs={"class": "form-control", "type": "time"},
                format="%H:%M",
            ),
            "motivo": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Motivo de la cita"}
            ),
            "notas": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Notas adicionales...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cliente"].queryset = Cliente.objects.filter(activo=True)
        # Establecer fecha mínima de hoy
        self.fields["fecha"].widget.attrs["min"] = date.today().isoformat()
    
    def clean_fecha(self):
        """Validar que la fecha no sea del pasado ni muy lejana."""
        fecha = self.cleaned_data.get("fecha")
        if not fecha:
            raise forms.ValidationError("La fecha es obligatoria.")
        
        hoy = date.today()
        if fecha < hoy:
            raise forms.ValidationError("No puedes crear citas en fechas pasadas.")
        
        fecha_maxima = hoy + timedelta(days=self.DIAS_MAXIMOS_FUTURO)
        if fecha > fecha_maxima:
            raise forms.ValidationError(f"No puedes crear citas con más de {self.DIAS_MAXIMOS_FUTURO} días de anticipación.")
        
        return fecha
    
    def clean_hora(self):
        """Validar horario de trabajo y que no sea pasada."""
        hora = self.cleaned_data.get("hora")
        if not hora:
            raise forms.ValidationError("La hora es obligatoria.")
        
        # Validar horario de trabajo
        if hora < self.HORA_INICIO or hora >= self.HORA_FIN:
            raise forms.ValidationError(f"Las citas solo se pueden agendar entre {self.HORA_INICIO.strftime('%H:%M')} y {self.HORA_FIN.strftime('%H:%M')}.")
        
        # Validar que no sea en el pasado para citas de hoy
        fecha = self.cleaned_data.get("fecha")
        if fecha and fecha == date.today():
            from datetime import datetime
            ahora = timezone.now()
            hora_cita = datetime.combine(fecha, hora)
            hora_cita = timezone.make_aware(hora_cita)
            if hora_cita < ahora:
                raise forms.ValidationError("No puedes crear citas en horas pasadas.")
        
        return hora
    
    def clean_motivo(self):
        """Validar motivo de la cita."""
        motivo = self.cleaned_data.get("motivo", "").strip()
        if not motivo:
            raise forms.ValidationError("El motivo es obligatorio.")
        if len(motivo) < 5:
            raise forms.ValidationError("El motivo debe tener al menos 5 caracteres.")
        if len(motivo) > 300:
            raise forms.ValidationError("El motivo no puede exceder 300 caracteres.")
        return motivo
    
    def clean(self):
        """Validaciones que requieren múltiples campos."""
        cleaned_data = super().clean()
        cliente = cleaned_data.get("cliente")
        fecha = cleaned_data.get("fecha")
        hora = cleaned_data.get("hora")
        
        if cliente and fecha and hora:
            # Verificar si ya existe una cita para este cliente en esta fecha/hora
            from datetime import datetime, timedelta
            
            # Buscar citas existentes (excluyendo la actual si es edición)
            citas_existentes = Cita.objects.filter(
                cliente=cliente,
                fecha=fecha,
                hora=hora
            ).exclude(estado="cancelada")
            
            # Si estamos editando, excluir la cita actual
            if self.instance and self.instance.pk:
                citas_existentes = citas_existentes.exclude(pk=self.instance.pk)
            
            if citas_existentes.exists():
                raise forms.ValidationError(
                    f"Ya existe una cita para {cliente.nombre} el {fecha.strftime('%d/%m/%Y')} a las {hora.strftime('%H:%M')}."
                )
            
            # Verificar si hay otra cita muy cercana (dentro de 30 minutos)
            hora_inicio = datetime.combine(fecha, hora) - timedelta(minutes=30)
            hora_fin = datetime.combine(fecha, hora) + timedelta(minutes=30)
            
            citas_cercanas = Cita.objects.filter(
                cliente=cliente,
                fecha=fecha,
                hora__gte=hora_inicio.time(),
                hora__lt=hora_fin.time()
            ).exclude(estado="cancelada")
            
            if self.instance and self.instance.pk:
                citas_cercanas = citas_cercanas.exclude(pk=self.instance.pk)
            
            if citas_cercanas.exists():
                raise forms.ValidationError(
                    f"El cliente {cliente.nombre} ya tiene una cita muy cercana a esta hora. Deja al menos 30 minutos entre citas."
                )
        
        return cleaned_data


class AsistenciaForm(forms.Form):
    """Formulario para registrar asistencia."""

    ASISTENCIA_CHOICES = [
        ("", "-- Seleccionar --"),
        ("si", "Sí asistió"),
        ("no", "No asistió"),
    ]
    asistencia = forms.ChoiceField(
        choices=ASISTENCIA_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="¿El cliente asistió?",
    )


class ReporteForm(forms.Form):
    """Formulario para filtrar reportes."""

    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        label="Desde",
    )
    fecha_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        label="Hasta",
    )
    estado = forms.ChoiceField(
        required=False,
        choices=[("", "Todos")] + Cita.ESTADO_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Estado",
    )
    cliente = forms.ModelChoiceField(
        required=False,
        queryset=Cliente.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Cliente",
        empty_label="Todos",
    )
