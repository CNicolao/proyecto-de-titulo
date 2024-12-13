from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.conf.urls import handler404, handler403
from .forms import LoginForm, RegistroUsuarioForm
from .models import Ticket, Encuesta
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.core.paginator import Paginator
from django.db.models.signals import post_save

from django.http import HttpResponse
from .forms import UserImportForm
from .resources import CustomUserResource
from tablib import Dataset
from django.conf import settings
from django.core.mail import send_mail

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserImportForm
from .resources import CustomUserResource
from tablib import Dataset

CustomUser = get_user_model()

@receiver(post_save, sender=Ticket)
def notificar_coordinador(sender, instance, created, **kwargs):
    if created:
        subject = f"Nuevo Ticket #{instance.id} Creado"
        message = (
            f"Se ha creado un nuevo ticket.\n\n"
            f"Título: {instance.titulo}\n"
            f"Descripción: {instance.descripcion}\n\n"
            f"Para ver más detalles, visita: http://tusitio.com/ticket/{instance.id}/\n"
        )
        send_mail(
            subject,
            message,
            'coordinadorticket.sti@gmail.com',  # Remitente
            ['camilonicolao1@gmail.com']  # Destinatario
        )

def enviar_correo_a_tecnico(ticket):
    # Asumiendo que el ticket tiene un tecnico_asignado y éste tiene un email
    tecnico = ticket.tecnico_asignado
    if not tecnico or not tecnico.email:
        return  # No hacemos nada si no hay un técnico o no tiene email

    asunto = f"Se te ha asignado el Ticket #{ticket.id}"
    mensaje = (
        f"Estimado/a {tecnico.first_name or tecnico.username},\n\n"
        f"Se te ha asignado el siguiente ticket:\n\n"
        f"ID del Ticket: {ticket.id}\n"
        f"Título: {ticket.titulo}\n"
        f"Descripción: {ticket.descripcion}\n"
        f"Estado: {ticket.estado}\n"
        f"Prioridad: {ticket.prioridad}\n\n"
        "Por favor, revisa el sistema para gestionar este ticket.\n\n"
        "Saludos."
    )

    send_mail(
        asunto,
        mensaje,
        settings.DEFAULT_FROM_EMAIL,
        [tecnico.email],
        fail_silently=False
    )
def enviar_correo_calificacion(ticket):
    asunto = f"Tu Ticket #{ticket.id} ha sido resuelto"
    enlace_encuesta = f"http://tusitio.com/ticket/{ticket.id}/encuesta/"  # Ajusta el dominio y la ruta
    mensaje = (
        f"Hola {ticket.usuario.first_name or ticket.usuario.username},\n\n"
        f"Tu ticket con el ID #{ticket.id} ha sido marcado como Resuelto.\n\n"
        f"Título: {ticket.titulo}\n"
        f"Descripción: {ticket.descripcion}\n"
        f"Estado: {ticket.estado}\n"
        f"Prioridad: {ticket.prioridad}\n\n"
        f"Por favor, ayúdanos a mejorar calificando este servicio:\n"
        f"{enlace_encuesta}\n\n"
        "Gracias por utilizar nuestro servicio."
    )

    send_mail(
        asunto,
        mensaje,
        settings.DEFAULT_FROM_EMAIL,
        [ticket.usuario.email],
        fail_silently=False,
    )

def enviar_correo_ticket_en_progreso(ticket):
    if ticket.usuario and ticket.usuario.email:
        asunto = f"Tu Ticket #{ticket.id} está ahora En Progreso"
        
        # Mensaje base
        mensaje = (
            f"Hola {ticket.usuario.first_name or ticket.usuario.username},\n\n"
            f"Tu ticket ha cambiado de estado de Pendiente a En Progreso.\n\n"
            f"Detalles del Ticket:\n"
            f"ID: {ticket.id}\n"
            f"Título: {ticket.titulo}\n"
            f"Prioridad: {ticket.prioridad}\n"
            f"Estado Actual: {ticket.estado}\n\n"
        )

        # Agregar la descripción de la solución si existe
        if ticket.solucion:
            mensaje += f"Solución / Avance:\n{ticket.solucion}\n\n"

        # Verificar si requiere visita en terreno
        if ticket.visita_terreno:
            mensaje += "Se requiere una visita en terreno para atender su solicitud.\n\n"
        else:
            mensaje += "No se requiere una visita en terreno en este momento.\n\n"
            mensaje += "favor de enviar su anydesk en caso de no haberlo colocado en la descripcion del problema.\n\n"

        mensaje += "Nuestro equipo está trabajando en tu solicitud. Gracias por tu paciencia."

        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [ticket.usuario.email],
            fail_silently=False,
        )

def index_vista(request):
    return render(request, 'index.html')

# Decorador para verificar si el usuario es staff
def is_staff_user(user):
    if user.is_staff:
        return True
    raise PermissionDenied



def user_import_view(request):
    """
    Vista para manejar la importación de usuarios desde un archivo XLSX.
    """
    if request.method == 'POST':
        form = UserImportForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            if not file.name.endswith('.xlsx'):
                messages.error(request, 'El archivo debe ser un archivo Excel (.xlsx).')
                return redirect('user_import_export')

            # Leer los datos del archivo
            data = file.read()
            dataset = Dataset().load(data, format='xlsx')  # Cargar datos como XLSX
            user_resource = CustomUserResource()

            # Probar importación (dry_run)
            result = user_resource.import_data(dataset, dry_run=True)

            if not result.has_errors():
                # Realizar importación si no hay errores
                user_resource.import_data(dataset, dry_run=False)
                messages.success(request, 'Usuarios importados correctamente.')
            else:
                messages.error(request, 'Ha ocurrido un error al importar el archivo. Verifica el formato.')
            return redirect('user_import_export')
    else:
        form = UserImportForm()

    return render(request, 'user_import_export.html', {'form': form})


def user_export_view(request):
    """
    Vista para exportar todos los usuarios a un archivo XLSX.
    """
    user_resource = CustomUserResource()
    dataset = user_resource.export()
    response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') # type: ignore
    response['Content-Disposition'] = 'attachment; filename="usuarios.xlsx"'
    return response
# ---- Vistas de Autenticación ----
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user = CustomUser.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    if user.email == 'coordinador@sti.cl':
                        messages.success(request, f"Bienvenido {user.first_name or user.username}.")
                        return redirect('coordinador')
                    else:
                        messages.success(request, f"Bienvenido {user.first_name or user.username}.")
                        return redirect('home')
                messages.error(request, "Correo o contraseña incorrectos.")
            except CustomUser.DoesNotExist:
                messages.error(request, "Correo no registrado.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('login')

def registrarse_vista(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data['password'])
            usuario.save()
            messages.success(request, "Tu cuenta ha sido creada exitosamente.")
            return redirect('login')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'registrarse.html', {'usuario_form': form})

# ---- Vistas de Usuario ----
@login_required
def perfil_usuario(request):
    return render(request, 'perfil.html', {'user': request.user})


@login_required
def home_vista(request):
    if request.user.is_staff:
        # Mostrar sólo los tickets asignados al técnico actual
        tickets_qs = Ticket.objects.filter(tecnico_asignado=request.user)
    else:
        # Si no es técnico, mostramos todos o lo que necesites
        tickets_qs = Ticket.objects.filter(usuario=request.user)

    # Paginación: mostrar solo 5 tickets por página
    paginator = Paginator(tickets_qs.order_by("-fecha_creacion"), 5)  # 5 tickets por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "tickets_total": tickets_qs.count(),
        "tickets_pendientes": tickets_qs.filter(estado="Pendiente").count(),
        "tickets_resueltos": tickets_qs.filter(estado="Resuelto").count(),
        "tickets_en_proceso": tickets_qs.filter(estado="En Progreso").count(),
        "tickets_recientes": page_obj,
    }

    return render(request, "home.html", context)


# ---- Vistas de Tickets ----
@login_required
def ticket_vista(request):
    if request.method == "POST":
        titulo = request.POST.get("titulo")
        descripcion = request.POST.get("descripcion")
        if not (titulo and descripcion):
            messages.error(request, "El título y la descripción son obligatorios.")
        else:
            Ticket.objects.create(titulo=titulo, descripcion=descripcion, usuario=request.user)
            messages.success(request, "El ticket fue creado exitosamente.")
            return redirect("home")
    return render(request, "ticket1.html")

@login_required
@user_passes_test(is_staff_user)
def dashboard_vista(request):
    context = {
        'tickets_pendientes': Ticket.objects.filter(estado="Pendiente").count(),
        'tickets_en_proceso': Ticket.objects.filter(estado="En Progreso").count(),
        'tickets_resueltos': Ticket.objects.filter(estado="Resuelto").count(),
        'tickets_por_mes': (
            Ticket.objects.annotate(mes=TruncMonth('fecha_creacion'))
            .values('mes')
            .annotate(total=Count('id'))
            .order_by('mes')
        ),
        'tickets_por_tecnico': (
            Ticket.objects.values('tecnico_asignado__first_name', 'tecnico_asignado__last_name')
            .annotate(total=Count('id'))
            .order_by('-total')
        ),
        'tickets_por_empresa': (
            Ticket.objects.values('usuario__nombre_empresa')
            .annotate(total=Count('id'))
            .order_by('-total')
        ),
    }
    return render(request, 'dashboard.html', context)

@login_required
def detalle_ticket_vista(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Obtener lista de técnicos disponibles (is_staff=True y is_active=True)
    tecnicos_disponibles = CustomUser.objects.filter(is_staff=True, is_active=True)
    
    if request.method == 'POST' and request.user.is_staff:
        estado_anterior = ticket.estado
        ticket.estado = request.POST.get('estado')
        ticket.prioridad = request.POST.get('prioridad')
        ticket.solucion = request.POST.get('solucion')
        ticket.visita_terreno = 'visita_terreno' in request.POST

        # Obtener el técnico seleccionado del formulario (si existe)
        tecnico_id = request.POST.get('tecnico_asignado')
        if tecnico_id:
            try:
                tecnico_seleccionado = CustomUser.objects.get(id=tecnico_id, is_staff=True, is_active=True)
                tecnico_anterior = ticket.tecnico_asignado
                ticket.tecnico_asignado = tecnico_seleccionado # type: ignore
            except CustomUser.DoesNotExist:
                # Si el técnico no existe o no está activo/staff, no se asigna
                pass

        ticket.save()
        if ticket.tecnico_asignado and (tecnico_id or not tecnico_anterior or tecnico_anterior != ticket.tecnico_asignado): # type: ignore
            # Enviar correo al técnico asignado
            enviar_correo_a_tecnico(ticket)
        messages.success(request, "El ticket ha sido actualizado correctamente.")
        if estado_anterior == 'Pendiente' and ticket.estado == 'En Progreso':
            enviar_correo_ticket_en_progreso(ticket)
        if ticket.estado == 'Resuelto' and ticket.usuario.email:
            enviar_correo_calificacion(ticket)
        messages.success(request, "El ticket ha sido actualizado correctamente.")
        return redirect('dashboard')

    return render(request, 'detalle_ticket.html', {
        'ticket': ticket,
        'tecnicos': tecnicos_disponibles,
    })


@login_required
def eliminar_ticket_vista(request, ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        ticket.delete()
        messages.success(request, "El ticket ha sido eliminado exitosamente.")
    except Ticket.DoesNotExist:
        messages.error(request, "El ticket no existe.")
    return redirect('dashboard')

@login_required
def encuesta_vista(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if not request.user.is_staff and ticket.estado == "Resuelto":
        if request.method == "POST":
            Encuesta.objects.create(
                ticket=ticket,
                calificacion=request.POST.get("rating"),
                comentarios=request.POST.get("comments"),
            )
            messages.success(request, "¡Gracias por calificar el servicio!")
            return redirect("home")
        return render(request, "encuesta.html", {"ticket": ticket})
    messages.error(request, "No tienes permiso para calificar este ticket.")
    return redirect("home")

# ---- Manejo de Errores ----
def error_404_view(request, exception=None):
    return render(request, '404.html', status=404)

@login_required
def coordinador_vista(request):
    if request.user.is_staff:
        tickets_qs = Ticket.objects.all()
    else:
        tickets_qs = Ticket.objects.filter(usuario=request.user)

    # Leer el parámetro 'order' desde la URL. Ejemplo: ?order=asc o ?order=desc
    order = request.GET.get('order', 'desc')  # Por defecto descendente
    
    # Ajustar el orden según el parámetro
    if order == 'asc':
        tickets_qs = tickets_qs.order_by('fecha_creacion')
    else:
        tickets_qs = tickets_qs.order_by('-fecha_creacion')  # Orden descendente por defecto

    # Paginación
    paginator = Paginator(tickets_qs, 10)  # 10 tickets por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "tickets_total": tickets_qs.count(),
        "tickets_pendientes": tickets_qs.filter(estado="Pendiente").count(),
        "tickets_resueltos": tickets_qs.filter(estado="Resuelto").count(),
        "tickets_en_proceso": tickets_qs.filter(estado="En Progreso").count(),
        "tickets_recientes": page_obj,
        "order": order,  # Para saber el orden actual en el template
    }
    return render(request, "coordinador.html", context)

