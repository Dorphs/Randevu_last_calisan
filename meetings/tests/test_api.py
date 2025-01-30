import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from ..models import Visitor, Meeting, MeetingRoom
from datetime import timedelta

@pytest.mark.django_db
class TestVisitorAPI:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    def test_create_visitor(self, api_client):
        url = reverse('visitor-list')
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'company': 'Test Company',
            'phone': '1234567890'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Test User'

    def test_list_visitors(self, api_client):
        Visitor.objects.create(
            name='Test User',
            email='test@example.com'
        )
        url = reverse('visitor-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

@pytest.mark.django_db
class TestMeetingAPI:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def visitor(self):
        return Visitor.objects.create(
            name='Test User',
            email='test@example.com'
        )

    @pytest.fixture
    def room(self):
        return MeetingRoom.objects.create(
            name='Test Room',
            capacity=10
        )

    def test_create_meeting(self, api_client, visitor, room):
        url = reverse('meeting-list')
        now = timezone.now()
        data = {
            'title': 'Test Meeting',
            'visitor': visitor.id,
            'location': room.id,
            'start_time': now.isoformat(),
            'end_time': (now + timedelta(hours=1)).isoformat(),
            'meeting_type': 'INTERNAL'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Test Meeting'

    def test_meeting_conflict(self, api_client, visitor, room):
        now = timezone.now()
        Meeting.objects.create(
            title='First Meeting',
            visitor=visitor,
            location=room,
            start_time=now,
            end_time=now + timedelta(hours=1)
        )

        url = reverse('meeting-list')
        data = {
            'title': 'Second Meeting',
            'visitor': visitor.id,
            'location': room.id,
            'start_time': (now + timedelta(minutes=30)).isoformat(),
            'end_time': (now + timedelta(hours=1, minutes=30)).isoformat(),
            'meeting_type': 'INTERNAL'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_409_CONFLICT
