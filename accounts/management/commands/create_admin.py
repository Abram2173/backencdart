# backend/accounts/management/commands/create_admin.py
from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = "Crea o actualiza el superusuario admin con contraseña 123"

    def handle(self, *args, **options):
        username = 'admin'
        email = 'admin@docagil.com'
        password = '123'

        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Usuario {username} actualizado → contraseña: {password}"))
        else:
            User.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS(f"Superusuario {username} creado → contraseña: {password}"))