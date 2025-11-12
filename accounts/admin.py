from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'is_approved', 'full_name']
    list_filter = ['role', 'is_approved']
    actions = ['approve_users']

    def approve_users(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, 'Usuarios aprobados')
    approve_users.short_description = "Aprobar usuarios seleccionados"