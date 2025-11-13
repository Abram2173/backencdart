from django.http import HttpResponse
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from backend.accounts import admin

def home(request):
    return HttpResponse("¡Bienvenido a Docagil Backend! API en /api/, Admin en /admin/.")

urlpatterns = [
    path('', home, name='home'),  # Nueva: home simple
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/admin/', include('accounts.urls')),
    path('api/solicitante/', include('accounts.urls')),
    path('api/aprobador/', include('accounts.urls')),
    path('api/auditor/', include('accounts.urls')),
    path('api/documents/', include('documents.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)