from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from .models import Encomienda, Empleado, HistorialEstado
from clientes.models import Cliente
from rutas.models import Ruta
from config.choices import EstadoEnvio

@login_required
def dashboard(request):
    hoy = timezone.now().date()
    context = {
        'total_activas': Encomienda.objects.activas().count(),
        'en_transito': Encomienda.objects.en_transito().count(),
        'con_retraso': Encomienda.objects.con_retraso().count(),
        'entregadas_hoy': Encomienda.objects.filter(
            estado=EstadoEnvio.ENTREGADO,
            fecha_entrega_real=hoy
        ).count(),
        'ultimas': Encomienda.objects.con_relaciones()[:5],
    }
    return render(request, 'envios/dashboard.html', context)
@login_required
def encomienda_lista(request):
    q = request.GET.get('q', '')
    estado = request.GET.get('estado', '')
    qs = Encomienda.objects.con_relaciones().all()
    if estado:
        qs = qs.filter(estado=estado)
    if q:
        qs = qs.filter(
            Q(codigo__icontains=q) |
            Q(remitente__apellidos__icontains=q) |
            Q(destinatario__apellidos__icontains=q)
        )
    paginator = Paginator(qs, 15)
    page = request.GET.get('page', 1)
    encomiendas = paginator.get_page(page)
    context = {
        'encomiendas': encomiendas,
        'estados': EstadoEnvio.choices,
        'estado_activo': estado,
        'q': q,
    }
    return render(request, 'envios/lista.html', context)
@login_required
def encomienda_detalle(request, pk):
    enc = get_object_or_404(
        Encomienda.objects.con_relaciones(), pk=pk
    )
    historial = enc.historial.select_related('empleado').all()
    return render(request, 'envios/detalle.html', {
        'encomienda': enc,
        'historial': historial,
        'estados_disponibles': EstadoEnvio.choices,
    })
@login_required
def encomienda_crear(request):
    from .forms import EncomiendaForm
    if request.method == 'POST':
        form = EncomiendaForm(request.POST)
        if form.is_valid():
            enc = form.save(commit=False)
            enc.empleado_registro = Empleado.objects.get(
                email=request.user.email
            )
            enc.save()
            messages.success(
                request,
                f'Encomienda {enc.codigo} registrada correctamente.'
            )
            return redirect('encomienda_detalle', pk=enc.pk)
    else:
        form = EncomiendaForm()
    return render(request, 'envios/form.html', {
        'form': form,
        'titulo': 'Nueva Encomienda',
    })
@require_POST
@login_required
def encomienda_cambiar_estado(request, pk):
    enc = get_object_or_404(Encomienda, pk=pk)
    nuevo_estado = request.POST.get('estado')
    observacion = request.POST.get('observacion', '')
    try:
        empleado = Empleado.objects.get(email=request.user.email)
        enc.cambiar_estado(nuevo_estado, empleado, observacion)
        messages.success(
            request,
            f'Estado actualizado a: {enc.get_estado_display()}'
        )
    except ValueError as e:
        messages.error(request, str(e))
    return redirect('encomienda_detalle', pk=pk)

@login_required
def encomienda_editar(request, pk):
    enc = get_object_or_404(Encomienda, pk=pk)
    if enc.estado != EstadoEnvio.PENDIENTE:
        raise PermissionDenied('Solo se puede editar encomiendas pendientes.')
    return redirect('encomienda_detalle', pk=enc.pk)


def buscar_por_codigo(request, codigo):
    enc = get_object_or_404(Encomienda, codigo=codigo.upper())
    return redirect('encomienda_detalle', pk=enc.pk)


def encomienda_api(request, uuid):
    try:
        enc = Encomienda.objects.con_relaciones().get(codigo__icontains=str(uuid)[:6])
        return JsonResponse({
            'codigo': enc.codigo,
            'estado': enc.estado,
            'display': enc.get_estado_display(),
            'retraso': enc.tiene_retraso,
            'dias': enc.dias_en_transito,
            'remitente': enc.remitente.nombre_completo,
            'destinatario': enc.destinatario.nombre_completo,
        })
    except Encomienda.DoesNotExist:
        return JsonResponse({'error': 'No encontrada'}, status=404)


