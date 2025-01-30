from rest_framework import serializers
from .models import Visitor, Meeting, MeetingRoom, MeetingNote
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class VisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitor
        fields = '__all__'

class MeetingRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingRoom
        fields = '__all__'

class MeetingNoteSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = MeetingNote
        fields = '__all__'

class MeetingSerializer(serializers.ModelSerializer):
    visitor = VisitorSerializer(read_only=True)
    visitor_id = serializers.PrimaryKeyRelatedField(
        queryset=Visitor.objects.all(),
        source='visitor',
        write_only=True
    )
    created_by = UserSerializer(read_only=True)
    notes = MeetingNoteSerializer(many=True, read_only=True)

    class Meta:
        model = Meeting
        fields = '__all__'
        read_only_fields = ['created_by']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
