from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),  # Login, register
    path('api/admin/', include('accounts.urls')),  # Admin: usuarios, kpis, reportes
    path('api/solicitante/', include('accounts.urls')),  # Solicitante: tramites, notificaciones
    path('api/aprobador/', include('accounts.urls')),  # Aprobador: pendientes, historial, bitacora
    path('api/auditor/', include('accounts.urls')),  # Auditor: kpis, reportes, bitacora
    path('api/documents/', include('documents.urls')),  # Flows
    path('api/gestor/', include('accounts.urls')),  # ← PARA EL JEFE DE DEPARTAMENTO
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)