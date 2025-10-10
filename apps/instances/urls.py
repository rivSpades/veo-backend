"""
Instances app URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InstanceViewSet, InstanceMemberViewSet

router = DefaultRouter()
router.register(r'instances', InstanceViewSet, basename='instances')
router.register(r'instance-members', InstanceMemberViewSet, basename='instance-members')

urlpatterns = [
    path('', include(router.urls)),
]
