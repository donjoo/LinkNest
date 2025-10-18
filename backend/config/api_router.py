from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

from apps.users.api.views import UserViewSet
from apps.organizations.views import OrganizationViewSet
from apps.urls.views import NamespaceViewSet, ShortURLViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("organizations", OrganizationViewSet)
router.register("namespaces", NamespaceViewSet)
router.register("short-urls", ShortURLViewSet)


app_name = "api"
urlpatterns = [
    path("", include(router.urls)),
    path("", include("apps.organizations.urls")),
]
