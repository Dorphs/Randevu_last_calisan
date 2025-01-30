from rest_framework import serializers
from django.contrib.auth import get_user_model
from ...models.reports import Dashboard, DashboardWidget

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class DashboardWidgetSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField()
    
    class Meta:
        model = DashboardWidget
        fields = [
            'id', 'dashboard', 'title', 'widget_type',
            'position', 'refresh_interval', 'data',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_data(self, obj):
        from ...services.dashboard_service import DashboardService
        return DashboardService.refresh_widget(obj)

class DashboardSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    widgets = DashboardWidgetSerializer(many=True, read_only=True)
    shared_with = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Dashboard
        fields = [
            'id', 'title', 'description', 'owner',
            'widgets', 'shared_with', 'is_public',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class WidgetPositionSerializer(serializers.Serializer):
    x = serializers.IntegerField(min_value=0)
    y = serializers.IntegerField(min_value=0)
    w = serializers.IntegerField(min_value=1, max_value=12)
    h = serializers.IntegerField(min_value=1)
