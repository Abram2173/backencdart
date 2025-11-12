import stat
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import DocumentFlow

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def document_flows_view(request):
    if request.user.role not in ['admin', 'auditor']:
        return Response({'error': 'Acceso denegado'}, status=stat.HTTP_403_FORBIDDEN)
    flows = DocumentFlow.objects.all()
    data = [{'id': f.id, 'nombre': f.nombre, 'descripcion': f.descripcion, 'folio': f.folio, 'etapa': f.etapa, 'status': f.status} for f in flows]
    return Response(data)