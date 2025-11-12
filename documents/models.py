from django.db import models
from django.conf import settings

class DocumentFlow(models.Model):
    ETAPAS = [
        (1, 'Etapa 1'),
        (2, 'Etapa 2'),
        (3, 'Etapa 3'),
        (4, 'Etapa 4'),
        (5, 'Etapa 5'),
        (6, 'Etapa 6'),
        ('otro', 'Otro')  # ← FIX: 'otro' como choice
    ]
    etapa = models.CharField(choices=ETAPAS, default='1', max_length=10)  # ← FIX: CharField con 'otro', default '1'
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    folio = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, default='Pendiente')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    archivo = models.FileField(upload_to='tramites/', blank=True, null=True)

    def __str__(self):
        return f"{self.folio} - {self.nombre}"

class Report(models.Model):
    titulo = models.CharField(max_length=255)
    fecha = models.DateField()
    tipo = models.CharField(max_length=10, default='PDF')
    status = models.CharField(max_length=20, default='generado')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.titulo} - {self.fecha}"