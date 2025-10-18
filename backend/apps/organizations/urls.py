"""
Organization URL patterns.

Moved from apps.links.urls - handles organization and membership endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrganizationViewSet, 
    OrganizationMemberViewSet,
    InviteAcceptView, 
    InviteDeclineView,
    InviteRegisterView,
    InviteAcceptAfterVerificationView
)
from .test_views import TestAuthView, TestInviteView
from .test_invite_view import TestInviteCreateView

app_name = "organizations"

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet)
router.register(
    r'organizations/(?P<organization_pk>[^/.]+)/members', 
    OrganizationMemberViewSet, 
    basename='organization-members'
)

urlpatterns = [
    path('', include(router.urls)),
    path('invites/accept/', InviteAcceptView.as_view(), name='invite-accept'),
    path('invites/decline/', InviteDeclineView.as_view(), name='invite-decline'),
    path('invites/register/', InviteRegisterView.as_view(), name='invite-register'),
    path('invites/accept-after-verification/', InviteAcceptAfterVerificationView.as_view(), name='invite-accept-after-verification'),
    path('test-auth/', TestAuthView.as_view(), name='test-auth'),
    path('test-invite/', TestInviteView.as_view(), name='test-invite'),
    path('test-create-invite/', TestInviteCreateView.as_view(), name='test-create-invite'),
]
