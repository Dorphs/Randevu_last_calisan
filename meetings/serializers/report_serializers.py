from rest_framework import serializers
from ..models.reports import Report, ReportExecution, Dashboard, DashboardWidget
from .base_serializers import UserLightSerializer

class ReportExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportExecution
        fields = ['id', 'report', 'status', 'start_time', 'end_time',
                 'result_file', 'error_message', 'execution_parameters',
                 'created_at']
        read_only_fields = ['created_at']

class ReportSerializer(serializers.ModelSerializer):
    created_by = UserLightSerializer(read_only=True)
    recipients = UserLightSerializer(many=True, read_only=True)
    latest_execution = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = ['id', 'title', 'report_type', 'parameters', 'created_by',
                 'start_date', 'end_date', 'is_scheduled', 'schedule_frequency',
                 'recipients', 'latest_execution', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_latest_execution(self, obj):
        execution = obj.executions.order_by('-created_at').first()
        if execution:
            return ReportExecutionSerializer(execution).data
        return None

class DashboardWidgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardWidget
        fields = ['id', 'dashboard', 'title', 'widget_type', 'data_source',
                 'refresh_interval', 'position', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_refresh_interval(self, value):
        """Yenileme aralığını doğrula"""
        if value < 0:
            raise serializers.ValidationError("Yenileme aralığı negatif olamaz")
        if value > 3600:  # 1 saat
            raise serializers.ValidationError("Yenileme aralığı 1 saati geçemez")
        return value

class DashboardSerializer(serializers.ModelSerializer):
    owner = UserLightSerializer(read_only=True)
    shared_with = UserLightSerializer(many=True, read_only=True)
    widgets = DashboardWidgetSerializer(many=True, read_only=True)

    class Meta:
        model = Dashboard
        fields = ['id', 'title', 'layout', 'is_public', 'owner',
                 'shared_with', 'widgets', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_layout(self, value):
        """Dashboard yerleşimini doğrula"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Yerleşim bir sözlük olmalıdır")
        return value
