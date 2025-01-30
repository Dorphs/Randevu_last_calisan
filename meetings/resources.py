from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DateTimeWidget
from .models import Meeting, Visitor, MeetingRoom

class VisitorResource(resources.ModelResource):
    class Meta:
        model = Visitor
        import_id_fields = ('email',)
        fields = ('id', 'name', 'email', 'company', 'phone', 'created_at')
        export_order = fields

class MeetingResource(resources.ModelResource):
    visitor = fields.Field(
        column_name='visitor',
        attribute='visitor',
        widget=ForeignKeyWidget(Visitor, 'email')
    )
    
    location = fields.Field(
        column_name='location',
        attribute='location',
        widget=ForeignKeyWidget(MeetingRoom, 'name')
    )
    
    start_time = fields.Field(
        column_name='start_time',
        attribute='start_time',
        widget=DateTimeWidget(format='%Y-%m-%d %H:%M')
    )
    
    end_time = fields.Field(
        column_name='end_time',
        attribute='end_time',
        widget=DateTimeWidget(format='%Y-%m-%d %H:%M')
    )

    class Meta:
        model = Meeting
        fields = ('id', 'title', 'visitor', 'location', 'start_time', 'end_time',
                 'meeting_type', 'status', 'priority', 'description')
        export_order = fields
