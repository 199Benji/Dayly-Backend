from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TrackerViewSet

# The router handles all the complex URL patterns for us
router = DefaultRouter()
router.register(r'my-trackers', TrackerViewSet, basename='tracker')

urlpatterns = [
    # This includes the 'log_action' and 'leaderboard' endpoints
    path('', include(router.urls)),
]