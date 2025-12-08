from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import authenticate
from django.utils import timezone
from .serializers import LoginSerializer, RegisterSerializer
from .models import User
from documents.models import DocumentFlow

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    # Acepta tanto "email" como "username"
    email_or_username = request.data.get('email') or request.data.get('username')
    password = request.data.get('password')

    if not email_or_username or not password:
        return Response({'error': 'Faltan datos'}, status=400)

    # Busca por email o username
    try:
        if '@' in email_or_username:
            user = User.objects.get(email__iexact=email_or_username)
        else:
            user = User.objects.get(username=email_or_username)
    except User.DoesNotExist:
        return Response({'error': 'Credenciales incorrectas'}, status=400)

    if not user.check_password(password):
        return Response({'error': 'Credenciales incorrectas'}, status=400)

    if not user.is_active:
        return Response({'error': 'Cuenta desactivada'}, status=400)

    if not user.is_approved:
        return Response({'detail': 'Tu cuenta está pendiente de aprobación'}, status=403)

    token, _ = Token.objects.get_or_create(user=user)
    role = user.role if user.role else 'solicitante'

    return Response({
        'token': token.key,
        'role': role,
        'user_id': user.id,
        'full_name': user.full_name or user.get_full_name(),
        'email': user.email,
        'departamento': user.departamento or ''
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        role = request.data.get('role', 'solicitante')
        user.role = role
        user.is_approved = False   # ← AÑADE ESTA LÍNEA
        user.save()
        return Response({
            'message': 'Solicitud enviada. Espera aprobación del admin.',
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Admin Views (intacto)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def usuarios_view(request):
    if request.user.role != 'admin':
        return Response({'error': 'Acceso denegado solo para admins'}, status=status.HTTP_403_FORBIDDEN)
    users = User.objects.all().values('id', 'full_name', 'email', 'role', 'is_approved')
    for user in users:
        user['estado'] = 'Activo' if user['is_approved'] else 'Pendiente'
    return Response(list(users))

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def approve_user_view(request, pk):
    if request.user.role != 'admin':
        return Response({'error': 'Acceso denegado solo para admins'}, status=status.HTTP_403_FORBIDDEN)
    try:
        user = User.objects.get(id=pk)
        user.is_approved = True
        user.save()
        return Response({'message': 'Usuario aprobado'})
    except User.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reportes_view(request):
    if request.user.role != 'admin':
        return Response({'error': 'Acceso denegado solo para admins'}, status=status.HTTP_403_FORBIDDEN)
    
    # ← AHORA USA DocumentFlow EN VEZ DE Report
    docs = DocumentFlow.objects.all().order_by('-created_at')
    data = [{
        'id': d.id,
        'folio': d.folio,
        'titulo': d.nombre,
        'tipo': d.etapa,
        'fecha': d.created_at.strftime('%Y-%m-%d'),
        'status': d.status,
        'usuario': d.created_by.get_full_name() or d.created_by.username
    } for d in docs]
    
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def kpis_view(request):
    if request.user.role != 'admin':
        return Response({'error': 'Acceso denegado solo para admins'}, status=status.HTTP_403_FORBIDDEN)
    total_users = User.objects.count()
    total_docs = DocumentFlow.objects.count()
    return Response({
        'usuarios': total_users,
        'documentos': total_docs,
        'tiempo': "2.1 días",
        'cumplimiento': "98.5%"
    })

# Solicitante Views (intacto)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def solicitante_tramites_view(request):
    if request.user.role != 'solicitante':
        return Response({'error': 'Acceso denegado'}, status=403)
    
    tramites = DocumentFlow.objects.filter(created_by=request.user).order_by('-created_at')
    data = []
    for t in tramites:
        data.append({
            'id': t.id,
            'folio': t.folio,                    # ← ESTO FALTABA
            'titulo': t.nombre or "Sin título",
            'descripcion': t.descripcion,
            'tipo': t.etapa or "General",
            'estado': t.status,
            'fecha': t.created_at.strftime('%d/%m/%Y'),
            'archivo': t.archivo.url if t.archivo else None,
            'qr': t.folio  # ← Puedes dejarlo así o generar QR real
        })
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def solicitante_create_tramite(request):
    if request.user.role != 'solicitante':
        return Response({'error': 'Acceso denegado'}, status=403)

    try:
        titulo = request.data.get('titulo', '').strip()
        tipo = request.data.get('tipo', '1')
        contenido = request.data.get('contenido', '').strip()

        if not titulo or not contenido:
            return Response({'error': 'Faltan título o descripción'}, status=400)

        # GENERA FOLIO EN BACKEND (NUNCA CONFIAR EN FRONTEND)
        folio = f"SOL-{request.user.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"

        # Crea el trámite
        new_tramite = DocumentFlow.objects.create(
            nombre=titulo,
            descripcion=contenido,
            folio=folio,
            etapa=tipo,
            created_by=request.user,
            status='Pendiente'
        )

        # Manejo de archivo
        if 'archivo' in request.FILES:
            new_tramite.archivo = request.FILES['archivo']
            new_tramite.save()

        return Response({
            'message': 'Trámite creado exitosamente',
            'id': new_tramite.id,
            'folio': new_tramite.folio
        }, status=201)

    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def solicitante_notificaciones_view(request):
    if request.user.role != 'solicitante':
        return Response({'error': 'Acceso denegado'}, status=status.HTTP_403_FORBIDDEN)
    data = [
        {'id': 1, 'tipo': 'success', 'mensaje': 'Tu trámite fue aprobado', 'folio': 'FOL-001', 'fecha': '2025-11-10'},
        {'id': 2, 'tipo': 'warning', 'mensaje': 'Trámite en revisión', 'folio': 'FOL-002', 'fecha': '2025-11-09'}
    ]
    return Response(data)

# Aprobador Views (intacto)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def aprobador_pendientes_view(request):
    if request.user.role != 'aprobador':
        return Response({'error': 'Acceso denegado solo para aprobadores'}, status=status.HTTP_403_FORBIDDEN)
    tramites = DocumentFlow.objects.filter(status='Pendiente')
    data = [
        {
            'id': t.id,
            'folio': t.folio,
            'titulo': t.nombre,
            'tipo': t.etapa,
            'solicitante': t.created_by.username,
            'estado': t.status
        } for t in tramites
    ]
    return Response(data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def aprobador_approve_tramite(request, pk):
    if request.user.role != 'aprobador':
        return Response({'error': 'Acceso denegado solo para aprobadores'}, status=status.HTTP_403_FORBIDDEN)
    try:
        tramite = DocumentFlow.objects.get(id=pk)
        tramite.status = 'Aprobado'
        tramite.save()
        return Response({'message': 'Trámite aprobado'})
    except DocumentFlow.DoesNotExist:
        return Response({'error': 'Trámite no encontrado'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def aprobador_reject_tramite(request, pk):
    if request.user.role != 'aprobador':
        return Response({'error': 'Acceso denegado solo para aprobadores'}, status=status.HTTP_403_FORBIDDEN)
    try:
        tramite = DocumentFlow.objects.get(id=pk)
        tramite.status = 'Rechazado'
        tramite.save()
        return Response({'message': 'Trámite rechazado'})
    except DocumentFlow.DoesNotExist:
        return Response({'error': 'Trámite no encontrado'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def aprobador_historial_view(request):
    if request.user.role != 'aprobador':
        return Response({'error': 'Acceso denegado solo para aprobadores'}, status=status.HTTP_403_FORBIDDEN)
    tramites = DocumentFlow.objects.filter(status__in=['Aprobado', 'Rechazado'])
    data = [
        {
            'id': t.id,
            'folio': t.folio,
            'titulo': t.nombre,
            'tipo': t.etapa,
            'solicitante': t.created_by.username,
            'estado': t.status
        } for t in tramites
    ]
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def aprobador_bitacora_view(request):
    if request.user.role != 'aprobador':
        return Response({'error': 'Acceso denegado solo para aprobadores'}, status=status.HTTP_403_FORBIDDEN)
    data = [
        {'id': 1, 'action': 'Aprobado trámite FOL-001', 'user': 'aprobador', 'time': '2025-11-10 10:00'},
        {'id': 2, 'action': 'Rechazado trámite FOL-002', 'user': 'aprobador', 'time': '2025-11-10 09:30'}
    ]
    return Response(data)

# ← NUEVAS VIEWS PARA AUDITOR (agrega después de aprobador_bitacora_view)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def auditor_kpis_view(request):
    if request.user.role != 'auditor':
        return Response({'error': 'Acceso denegado solo para auditores'}, status=status.HTTP_403_FORBIDDEN)
    total_auditados = DocumentFlow.objects.filter(status='Auditado').count()
    total_no_conformes = DocumentFlow.objects.filter(status='No Conforme').count()
    total_documentos = DocumentFlow.objects.count()
    return Response({
        'tiempo': total_auditados,  # Placeholder para tiempo
        'rechazos': total_no_conformes,
        'documentos': total_documentos
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def auditor_reportes_view(request):
    if request.user.role != 'auditor':
        return Response({'error': 'Acceso denegado solo para auditores'}, status=status.HTTP_403_FORBIDDEN)
    reports = DocumentFlow.objects.all()
    data = [
        {
            'id': r.id,
            'titulo': r.titulo,
            'fecha': str(r.fecha),
            'tipo': r.tipo,
            'qr': r.id  # Placeholder para QR
        } for r in reports
    ]
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def auditor_bitacora_view(request):
    if request.user.role != 'auditor':
        return Response({'error': 'Acceso denegado solo para auditores'}, status=status.HTTP_403_FORBIDDEN)
    # Placeholder – hardcoded, crea model si quieres real
    data = [
        {'id': 1, 'action': 'Auditado trámite FOL-001', 'user': 'auditor', 'time': '2025-11-10 11:00'},
        {'id': 2, 'action': 'No conforme trámite FOL-002', 'user': 'auditor', 'time': '2025-11-10 10:30'}
    ]
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def usuarios_view(request):
    if request.user.role not in ['admin', 'auditor']: # ← FIX: Permite auditor
        return Response({'error': 'Acceso denegado solo para admins/auditores'}, status=status.HTTP_403_FORBIDDEN)
    users = User.objects.all().values('id', 'full_name', 'email', 'role', 'is_approved')
    return Response(users)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def kpis_view(request):
    if request.user.role not in ['admin', 'auditor']:  # ← FIX: Permite auditor
        return Response({'error': 'Acceso denegado solo para admins/auditores'}, status=status.HTTP_403_FORBIDDEN)
    # Tu lógica KPIs
    return Response({'usuarios': User.objects.count(), 'documentos': DocumentFlow.objects.count()})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reportes_view(request):
    if request.user.role not in ['admin', 'auditor']:  # ← FIX: Permite auditor
        return Response({'error': 'Acceso denegado solo para admins/auditores'}, status=status.HTTP_403_FORBIDDEN)
    # Tu lógica reportes
    return Response([]) 

# GESTOR DOCUMENTAL - ENDPOINTS REALES
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def gestor_subir_documento(request):
    if request.user.role not in ['gestor', 'admin']:
        return Response({'error': 'Solo el Gestor Documental puede subir documentos'}, status=403)

    from documents.models import DocumentFlow  # Asegúrate que exista
    titulo = request.data.get('titulo')
    codigo = request.data.get('codigo')
    tipo = request.data.get('tipo')
    archivo = request.FILES.get('archivo')

    if not all([titulo, codigo, tipo]):
        return Response({'error': 'Faltan datos'}, status=400)

    # Crea documento oficial (puedes usar DocumentFlow o crear uno nuevo)
    doc = DocumentFlow.objects.create(
        nombre=titulo,
        folio=codigo,
        descripcion=f"Documento oficial tipo: {tipo}",
        created_by=request.user,
        status="En revisión",
        archivo=archivo if archivo else None
    )

    return Response({
        'message': 'Documento oficial subido y enviado a aprobación',
        'folio': doc.folio,
        'titulo': doc.nombre,
        'estado': doc.status
    }, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gestor_catalogo(request):
    if request.user.role not in ['gestor', 'admin']:
        return Response({'error': 'Acceso denegado'}, status=403)

    docs = DocumentFlow.objects.filter(created_by__role__in=['gestor', 'admin'])
    data = [{
        'id': d.id,
        'folio': d.folio,
        'titulo': d.nombre,
        'estado': d.status,
        'fecha': d.created_at.strftime('%Y-%m-%d')
    } for d in docs]

    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gestor_tramites_view(request):
    # Acepta tanto 'gestor' como 'Gestor Documental'
    if request.user.role not in ['gestor', 'Gestor Documental']:
        return Response([], status=200)

    dept = request.user.departamento
    if not dept:
        return Response([], status=200)

    mapping = {
        'becas': 'becas',
        'inscripciones': 'inscripcion',
        'servicios_escolares': ['calificaciones', 'documentos', 'inscripcion'],
        'imss': 'seguridad_social',
        'biblioteca': 'recursos',
        'participacion': 'participacion',
    }

    categorias = mapping.get(dept, [])
    if not categorias:
        return Response([], status=200)

    if isinstance(categorias, list):
        tramites = DocumentFlow.objects.filter(etapa__in=categorias)
    else:
        tramites = DocumentFlow.objects.filter(etapa=categorias)

    data = [{
        'id': t.id,
        'folio': t.folio,
        'titulo': t.nombre,
        'estudiante': t.created_by.get_full_name() or t.created_by.username,
        'fecha': t.created_at.strftime('%d/%m/%Y')
    } for t in tramites.order_by('-created_at')]

    return Response(data)



# Vista para subdirector/director (visto bueno final)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def director_subdirector_tramites(request):
    if request.user.role not in ['subdirector', 'director']:
        return Response({'error': 'Acceso denegado'}, status=403)

    # Subdirector ve Becas, Inscripción, Servicios, IMSS, Biblioteca
    if request.user.role == 'subdirector':
        tramites = DocumentFlow.objects.filter(
            etapa__in=['becas', 'inscripcion', 'calificaciones', 'documentos', 'imss', 'biblioteca'],
            status='aprobado_aprobador'
        ).order_by('-created_at')
    # Director ve Quejas y permisos
    else:
        tramites = DocumentFlow.objects.filter(
            etapa='participacion',
            status='aprobado_aprobador'
        ).order_by('-created_at')

    data = [{
        'id': t.id,
        'folio': t.folio,
        'titulo': t.nombre,
        'estudiante': t.created_by.get_full_name() or t.created_by.username,
        'fecha': t.created_at.strftime('%d/%m/%Y')
    } for t in tramites]

    return Response(data)




from .permissions import RolePermission

# ← DIRECTOR (solo director)
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission(['director'])])
def director_view(request):
    return Response({"message": "Bienvenido Director", "data": "reportes globales"})

# ← SUBDIRECTOR
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission(['subdirector'])])
def subdirector_view(request):
    return Response({"message": "Bienvenido Subdirector"})

# ← GESTOR
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, RolePermission(['gestor'])])
def gestor_view(request):
    return Response({"message": "Gestor Documental"})

# ← COORDINADOR
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission(['coordinador'])])
def coordinador_view(request):
    return Response({"message": "Coordinador / Oficina"})

# ← APROBADOR
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission(['aprobador'])])
def aprobador_view(request):
    return Response({"message": "Revisor / Aprobador"})

# ← ESTUDIANTE
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission(['solicitante'])])
def solicitante_view(request):
    return Response({"message": "Estudiante"})

# ← AUDITOR
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission(['auditor'])])
def auditor_view(request):
    return Response({"message": "Auditor Interno"})

# ← ADMIN
@api_view(['GET'])
@permission_classes([IsAuthenticated, RolePermission(['admin'])])
def admin_view(request):
    return Response({"message": "Administrador del Sistema"})