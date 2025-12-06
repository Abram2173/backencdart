from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    # Admin
    path('usuarios/', views.usuarios_view, name='usuarios'),
    path('users/<int:pk>/approve/', views.approve_user_view, name='approve_user'),
    path('reportes/', views.reportes_view, name='reportes'),
    path('kpis/', views.kpis_view, name='kpis'),
    # Solicitante
    path('tramites/', views.solicitante_tramites_view, name='solicitante_tramites'),
    path('create-tramite/', views.solicitante_create_tramite, name='solicitante_create_tramite'),
    path('notificaciones/', views.solicitante_notificaciones_view, name='solicitante_notificaciones'),
    # Aprobador
    path('pendientes/', views.aprobador_pendientes_view, name='aprobador_pendientes'),
    path('tramite/<int:pk>/approve/', views.aprobador_approve_tramite, name='approve_tramite'),
    path('tramite/<int:pk>/reject/', views.aprobador_reject_tramite, name='reject_tramite'),
    path('historial/', views.aprobador_historial_view, name='aprobador_historial'),
    path('bitacora/', views.aprobador_bitacora_view, name='aprobador_bitacora'),
    # Auditor (paths exactos para frontend)
    path('kpis/', views.auditor_kpis_view, name='auditor_kpis'),
    path('reportes/', views.auditor_reportes_view, name='auditor_reportes'),
    path('bitacora/', views.auditor_bitacora_view, name='auditor_bitacora'),
    # accounts/urls.py → AGREGA AL FINAL
    path('gestor/subir/', views.gestor_subir_documento, name='gestor_subir'),
    path('gestor/catalogo/', views.gestor_catalogo, name='gestor_catalogo'),

    path('director/', views.director_view),
    path('subdirector/', views.subdirector_view),
    path('gestor/', views.gestor_view),
    path('coordinador/', views.coordinador_view),
    path('aprobador/', views.aprobador_view),
    path('solicitante/', views.solicitante_view),
    path('auditor/', views.auditor_view),
    path('administrador/', views.admin_view),

    path('gestor/tramites/', views.gestor_tramites_view, name='gestor_tramites'),
    path('direccion/tramites/', views.director_subdirector_tramites, name='direccion_tramites'),
    
]