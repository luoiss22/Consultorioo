from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Cliente, Cita
from .forms import ClienteForm, CitaForm, AsistenciaForm, ReporteForm


# ─── Dashboard ──────────────────────────────────────────────────────────────────


@login_required
def dashboard(request):
    """Vista principal con resumen del sistema."""
    hoy = timezone.now().date()
    citas_hoy = Cita.objects.filter(fecha=hoy).select_related("cliente")
    citas_pendientes = Cita.objects.filter(estado="pendiente").count()
    citas_confirmadas = Cita.objects.filter(estado="confirmada", fecha__gte=hoy).count()
    total_clientes = Cliente.objects.filter(activo=True).count()

    # Citas próximas (7 días)
    proxima_semana = hoy + timedelta(days=7)
    citas_proximas = (
        Cita.objects.filter(fecha__gte=hoy, fecha__lte=proxima_semana)
        .exclude(estado__in=["cancelada", "completada", "no_asistio"])
        .select_related("cliente")
        .order_by("fecha", "hora")[:10]
    )

    context = {
        "citas_hoy": citas_hoy,
        "citas_pendientes": citas_pendientes,
        "citas_confirmadas": citas_confirmadas,
        "total_clientes": total_clientes,
        "citas_proximas": citas_proximas,
    }
    return render(request, "citas/dashboard.html", context)


# ─── CRUD Clientes ──────────────────────────────────────────────────────────────


@login_required
def cliente_lista(request):
    """Lista de todos los clientes."""
    q = request.GET.get("q", "")
    clientes = Cliente.objects.all()
    if q:
        clientes = clientes.filter(
            Q(nombre__icontains=q) | Q(telefono__icontains=q) | Q(email__icontains=q)
        )
    return render(request, "citas/cliente_lista.html", {"clientes": clientes, "q": q})


@login_required
def cliente_crear(request):
    """Crear un nuevo cliente."""
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente creado exitosamente.")
            return redirect("cliente_lista")
    else:
        form = ClienteForm()
    return render(request, "citas/cliente_form.html", {"form": form, "titulo": "Nuevo Cliente"})


@login_required
def cliente_editar(request, pk):
    """Editar un cliente existente."""
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == "POST":
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente actualizado exitosamente.")
            return redirect("cliente_lista")
    else:
        form = ClienteForm(instance=cliente)
    return render(
        request, "citas/cliente_form.html", {"form": form, "titulo": "Editar Cliente", "cliente": cliente}
    )


@login_required
def cliente_eliminar(request, pk):
    """Eliminar un cliente."""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    # Verificar si tiene citas futuras
    hoy = timezone.now().date()
    citas_futuras = cliente.citas.filter(
        fecha__gte=hoy
    ).exclude(estado__in=["cancelada", "completada", "no_asistio"])
    
    if citas_futuras.exists():
        messages.error(
            request, 
            f"No puedes eliminar a {cliente.nombre} porque tiene {citas_futuras.count()} cita(s) futura(s). "
            f"Cancela o completa las citas primero."
        )
        return redirect("cliente_detalle", pk=cliente.pk)
    
    if request.method == "POST":
        nombre = cliente.nombre
        cliente.delete()
        messages.success(request, f"Cliente {nombre} eliminado exitosamente.")
        return redirect("cliente_lista")
    return render(request, "citas/cliente_confirmar_eliminar.html", {"cliente": cliente})


@login_required
def cliente_detalle(request, pk):
    """Ver detalle de un cliente con su historial de citas."""
    cliente = get_object_or_404(Cliente, pk=pk)
    citas = cliente.citas.all().order_by("-fecha", "-hora")
    return render(request, "citas/cliente_detalle.html", {"cliente": cliente, "citas": citas})


# ─── CRUD Citas ─────────────────────────────────────────────────────────────────


@login_required
def cita_lista(request):
    """Lista de todas las citas."""
    estado = request.GET.get("estado", "")
    citas = Cita.objects.select_related("cliente").all()
    if estado:
        citas = citas.filter(estado=estado)
    return render(request, "citas/cita_lista.html", {"citas": citas, "estado_filtro": estado})


@login_required
def cita_crear(request):
    """Crear una nueva cita."""
    if request.method == "POST":
        form = CitaForm(request.POST)
        if form.is_valid():
            cita = form.save()
            messages.success(request, "Cita creada exitosamente.")
            # Redirigir a la página de envío de WhatsApp
            return redirect("cita_whatsapp", pk=cita.pk)
    else:
        form = CitaForm()
        # Pre-seleccionar cliente si viene por parámetro
        cliente_id = request.GET.get("cliente")
        if cliente_id:
            form.fields["cliente"].initial = cliente_id
    return render(request, "citas/cita_form.html", {"form": form, "titulo": "Nueva Cita"})


@login_required
def cita_editar(request, pk):
    """Editar una cita existente."""
    cita = get_object_or_404(Cita, pk=pk)
    if request.method == "POST":
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            messages.success(request, "Cita actualizada exitosamente.")
            return redirect("cita_lista")
    else:
        form = CitaForm(instance=cita)
    return render(request, "citas/cita_form.html", {"form": form, "titulo": "Editar Cita", "cita": cita})


@login_required
def cita_eliminar(request, pk):
    """Eliminar una cita."""
    cita = get_object_or_404(Cita, pk=pk)
    
    # Verificar si la cita ya pasó y fue completada
    if cita.estado == "completada" and cita.asistio is not None:
        messages.error(
            request,
            "No puedes eliminar citas completadas con registro de asistencia. "
            "Esto es para mantener el historial."
        )
        return redirect("cita_detalle", pk=cita.pk)
    
    if request.method == "POST":
        cliente_nombre = cita.cliente.nombre
        fecha = cita.fecha
        cita.delete()
        messages.success(request, f"Cita de {cliente_nombre} del {fecha.strftime('%d/%m/%Y')} eliminada.")
        return redirect("cita_lista")
    return render(request, "citas/cita_confirmar_eliminar.html", {"cita": cita})


@login_required
def cita_detalle(request, pk):
    """Ver detalle de una cita."""
    cita = get_object_or_404(Cita, pk=pk)
    return render(request, "citas/cita_detalle.html", {"cita": cita})


# ─── WhatsApp y Confirmación ────────────────────────────────────────────────────


@login_required
def cita_whatsapp(request, pk):
    """Página para enviar notificación por WhatsApp."""
    cita = get_object_or_404(Cita, pk=pk)
    # Construir base_url dinámicamente
    base_url = request.build_absolute_uri("/").rstrip("/")
    url_whatsapp = cita.generar_url_whatsapp(base_url)
    mensaje = cita.generar_mensaje_whatsapp(base_url)
    return render(
        request,
        "citas/cita_whatsapp.html",
        {"cita": cita, "url_whatsapp": url_whatsapp, "mensaje": mensaje},
    )


def cita_confirmar(request, token):
    """Vista pública para que el cliente confirme su cita."""
    cita = get_object_or_404(Cita, token_confirmacion=token)

    # Verificar si la cita ya fue cancelada o completada
    if cita.estado in ["cancelada", "completada", "no_asistio"]:
        return render(request, "citas/confirmacion_resultado.html", {
            "cita": cita,
            "mensaje": f"Esta cita ya fue {cita.get_estado_display().lower()} y no puede ser modificada.",
            "tipo": "info",
        })

    if cita.es_pasada:
        return render(request, "citas/confirmacion_resultado.html", {
            "cita": cita,
            "mensaje": "Esta cita ya pasó y no puede ser confirmada ni cancelada.",
            "tipo": "warning",
        })

    if request.method == "POST":
        accion = request.POST.get("accion")
        if accion == "confirmar":
            if cita.estado == "confirmada":
                return render(request, "citas/confirmacion_resultado.html", {
                    "cita": cita,
                    "mensaje": "Esta cita ya había sido confirmada anteriormente.",
                    "tipo": "info",
                })
            cita.estado = "confirmada"
            cita.save()
            return render(request, "citas/confirmacion_resultado.html", {
                "cita": cita,
                "mensaje": "¡Su cita ha sido confirmada exitosamente!",
                "tipo": "success",
            })
        elif accion == "cancelar":
            cita.estado = "cancelada"
            cita.save()
            return render(request, "citas/confirmacion_resultado.html", {
                "cita": cita,
                "mensaje": "Su cita ha sido cancelada. Gracias por avisarnos.",
                "tipo": "danger",
            })

    return render(request, "citas/confirmacion_publica.html", {"cita": cita})


# ─── Asistencia ─────────────────────────────────────────────────────────────────


@login_required
def registrar_asistencia(request, pk):
    """Registrar si el cliente asistió o no a la cita."""
    cita = get_object_or_404(Cita, pk=pk)
    
    # Solo permitir registrar asistencia para citas pasadas o del día de hoy
    hoy = timezone.now().date()
    if cita.fecha > hoy:
        messages.error(request, "No puedes registrar asistencia para citas futuras.")
        return redirect("cita_detalle", pk=cita.pk)
    
    # No permitir modificar asistencia ya registrada
    if cita.asistio is not None:
        messages.warning(request, "La asistencia ya fue registrada para esta cita. Ve al detalle para ver el estado.")
        return redirect("cita_detalle", pk=cita.pk)

    if request.method == "POST":
        form = AsistenciaForm(request.POST)
        if form.is_valid():
            asistencia = form.cleaned_data["asistencia"]
            if asistencia == "si":
                cita.asistio = True
                cita.estado = "completada"
            else:
                cita.asistio = False
                cita.estado = "no_asistio"
            cita.save()
            messages.success(request, "Asistencia registrada exitosamente.")
            return redirect("cita_detalle", pk=cita.pk)
    else:
        form = AsistenciaForm()

    return render(request, "citas/registrar_asistencia.html", {"cita": cita, "form": form})


# ─── Reportes ───────────────────────────────────────────────────────────────────


@login_required
def reporte_asistencia(request):
    """Reporte de asistencia con filtros."""
    form = ReporteForm(request.GET or None)
    citas = Cita.objects.select_related("cliente").all()

    if form.is_valid():
        fecha_inicio = form.cleaned_data.get("fecha_inicio")
        fecha_fin = form.cleaned_data.get("fecha_fin")
        estado = form.cleaned_data.get("estado")
        cliente = form.cleaned_data.get("cliente")

        if fecha_inicio:
            citas = citas.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            citas = citas.filter(fecha__lte=fecha_fin)
        if estado:
            citas = citas.filter(estado=estado)
        if cliente:
            citas = citas.filter(cliente=cliente)

    # Estadísticas
    total = citas.count()
    asistieron = citas.filter(asistio=True).count()
    no_asistieron = citas.filter(asistio=False).count()
    sin_registro = citas.filter(asistio__isnull=True).count()
    confirmadas = citas.filter(estado="confirmada").count()
    pendientes = citas.filter(estado="pendiente").count()
    canceladas = citas.filter(estado="cancelada").count()

    # Citas pasadas sin registro de asistencia
    hoy = timezone.now().date()
    sin_confirmar_asistencia = citas.filter(
        fecha__lt=hoy,
        asistio__isnull=True,
        estado__in=["pendiente", "confirmada"],
    )

    context = {
        "form": form,
        "citas": citas.order_by("-fecha", "-hora"),
        "total": total,
        "asistieron": asistieron,
        "no_asistieron": no_asistieron,
        "sin_registro": sin_registro,
        "confirmadas": confirmadas,
        "pendientes": pendientes,
        "canceladas": canceladas,
        "sin_confirmar_asistencia": sin_confirmar_asistencia,
        "porcentaje_asistencia": round((asistieron / total * 100), 1) if total > 0 else 0,
    }
    return render(request, "citas/reporte_asistencia.html", context)
