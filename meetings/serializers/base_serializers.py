from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models.user_roles import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'role', 'department', 'phone', 'is_active']
        read_only_fields = ['is_active']

class UserLightSerializer(serializers.ModelSerializer):
    """Hafif kullanıcı serializerı - liste görünümleri için"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'full_name', 'email', 'role']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
