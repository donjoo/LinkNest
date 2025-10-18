"""
Organization admin.

Moved from apps.links.admin - handles organization and membership admin interface.
"""
from django.contrib import admin
from .models import Organization, OrganizationMembership, Invite


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "created_at", "member_count"]
    list_filter = ["created_at"]
    search_fields = ["name", "owner__email"]
    readonly_fields = ["id", "created_at", "updated_at"]
    
    def member_count(self, obj):
        return obj.memberships.count()
    member_count.short_description = "Members"


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "organization", "role", "created_at"]
    list_filter = ["role", "created_at"]
    search_fields = ["user__email", "organization__name"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ["email", "organization", "role", "invited_by", "accepted", "used", "is_expired", "created_at"]
    list_filter = ["role", "accepted", "used", "created_at"]
    search_fields = ["email", "organization__name", "invited_by__email"]
    readonly_fields = ["id", "token", "created_at", "expires_at"]
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = "Expired"