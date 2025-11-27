from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('solicitante', 'Solicitante'),
        ('aprobador', 'Aprobador'),
        ('auditor', 'Auditor'),
        ('gestor', 'Gestor Documental'),   # ← AÑADE ESTA LÍNEA
        ('admin', 'Admin'),
    ]
    full_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='solicitante')
    is_approved = models.BooleanField(default=False)
    email = models.EmailField(unique=True)

    def save(self, *args, **kwargs):
        if self.email and not self.email.endswith('@instituto.edu.mx'):
            raise ValueError("Email institucional requerido")
        super().save(*args, **kwargs)

def detect_role_from_username(self):
    lower = self.username.lower()
    if 'aprobador' in lower: return 'aprobador'
    if 'auditor' in lower: return 'auditor'
    if 'admin' in lower: return 'admin'
    if 'solicitante' in lower: return 'solicitante'
    if 'gestor' in lower: return'gestor'
    return self.role  # ← FIX: Fallback al role del model (registrado)