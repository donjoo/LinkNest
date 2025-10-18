"""
Organization URL patterns.

Moved from apps.links.urls - handles organization and membership endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrganizationViewSet

app_name = "organizations"

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
