from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if not user or not user.is_active or not user.is_approved:
            raise serializers.ValidationError("Credenciales inválidas o cuenta no aprobada")
        data['user'] = user
        return data

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone', 'department', 'role', 'username', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        lower_email = value.lower().strip()
        
        if not (lower_email.endswith('@instituto.edu.mx') or lower_email.endswith('.tecnm.mx')):
            raise serializers.ValidationError("Solo correos institucionales del TecNM")
        
        if User.objects.filter(email__iexact=lower_email).exists():
            raise serializers.ValidationError("Este correo ya está registrado")
        
        return lower_email

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        user.is_approved = False
        user.save()
        return user