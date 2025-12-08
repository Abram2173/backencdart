# accounts/permissions.py
from rest_framework.permissions import BasePermission
from .models import User  # ← Esta línea te falta

class RolePermission(BasePermission):
    """
    Permite acceso solo a ciertos roles
    """
    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        user_role = request.user.role
        
        # Acepta tanto la clave ('gestor') como el texto ('Gestor Documental')
        return user_role in self.allowed_roles or user_role in [choice[1] for choice in User.ROLE_CHOICES if choice[0] in self.allowed_roles]