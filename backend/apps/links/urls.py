from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrganizationViewSet, NamespaceViewSet, ShortURLViewSet

app_name = "links"

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet)
router.register(r'namespaces', NamespaceViewSet)
router.register(r'short-urls', ShortURLViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
