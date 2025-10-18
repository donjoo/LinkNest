"""
Organization admin.

Moved from apps.links.admin - handles organization and membership admin interface.
"""
from django.contrib import admin
from .models import Organization, OrganizationMembership


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