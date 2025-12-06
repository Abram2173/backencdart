from django.db import models
from django.conf import settings

class DocumentFlow(models.Model):
    ETAPAS = [
        ('becas', 'Becas'),
        ('calendario', 'Calendario'),
        ('inscripcion', 'Inscripción'),
        ('calificaciones', 'Calificaciones'),
        ('documentos', 'Documentos'),
        ('seguridad_social', 'Seguridad Social'),
        ('recursos', 'Recursos'),
        ('participacion', 'Participación'),
    ]
    
    etapa = models.CharField(max_length=20, choices=ETAPAS, default='becas')  # ← CAMBIA DE 10 A 20
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    folio = models.CharField(max_length=50, unique=True, blank=True)
    status = models.CharField(max_length=20, default='Pendiente')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    archivo = models.FileField(upload_to='tramites/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.folio:
            from django.utils import timezone
            self.folio = f"DOC-{timezone.now().strftime('%Y%m%d%H%M%S')}-{self.created_by.id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.folio} - {self.nombre}"