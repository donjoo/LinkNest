"""
URL patterns.

Moved from apps.links.urls - handles namespace and short URL endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NamespaceViewSet, ShortURLViewSet

app_name = "urls"

router = DefaultRouter()
router.register(r'namespaces', NamespaceViewSet)
router.register(r'short-urls', ShortURLViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
