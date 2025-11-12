from rest_framework import serializers
from .models import DocumentFlow, Report  # Importa tus modelos

class DocumentFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentFlow
        fields = '__all__'  # Incluye todos los campos (etapa, nombre, etc.)

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'  # Todos los campos para reports