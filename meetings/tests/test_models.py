import pytest
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from ..models import Visitor, Meeting, MeetingRoom
from datetime import timedelta

@pytest.mark.django_db
class TestVisitor:
    def test_visitor_creation(self):
        visitor = Visitor.objects.create(
            name="Test User",
            email="test@example.com",
            company="Test Company",
            phone="1234567890"
        )
        assert visitor.name == "Test User"
        assert visitor.email == "test@example.com"

    def test_visitor_str(self):
        visitor = Visitor.objects.create(
            name="Test User",
            email="test@example.com"
        )
        assert str(visitor) == "Test User"

@pytest.mark.django_db
class TestMeeting:
    @pytest.fixture
    def visitor(self):
        return Visitor.objects.create(
            name="Test User",
            email="test@example.com"
        )

    @pytest.fixture
    def room(self):
        return MeetingRoom.objects.create(
            name="Test Room",
            capacity=10
        )

    def test_meeting_creation(self, visitor, room):
        now = timezone.now()
        meeting = Meeting.objects.create(
            title="Test Meeting",
            visitor=visitor,
            location=room,
            start_time=now,
            end_time=now + timedelta(hours=1),
            meeting_type="INTERNAL"
        )
        assert meeting.title == "Test Meeting"
        assert meeting.status == "PENDING"

    def test_invalid_meeting_time(self, visitor, room):
        now = timezone.now()
        with pytest.raises(ValidationError):
            Meeting.objects.create(
                title="Test Meeting",
                visitor=visitor,
                location=room,
                start_time=now,
                end_time=now - timedelta(hours=1)
            )

    def test_meeting_conflict(self, visitor, room):
        now = timezone.now()
        Meeting.objects.create(
            title="First Meeting",
            visitor=visitor,
            location=room,
            start_time=now,
            end_time=now + timedelta(hours=1)
        )
        
        with pytest.raises(ValidationError):
            Meeting.objects.create(
                title="Second Meeting",
                visitor=visitor,
                location=room,
                start_time=now + timedelta(minutes=30),
                end_time=now + timedelta(hours=1, minutes=30)
            )
