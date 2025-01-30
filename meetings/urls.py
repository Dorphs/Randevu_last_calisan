from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'visitors', views.VisitorViewSet)
router.register(r'meetings', views.MeetingViewSet)
router.register(r'rooms', views.MeetingRoomViewSet)
router.register(r'notes', views.MeetingNoteViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
