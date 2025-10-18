from django.contrib import admin
from django.utils.html import format_html
from .models import Organization, OrganizationMembership, Namespace, ShortURL


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


@admin.register(Namespace)
class NamespaceAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "created_at", "short_url_count"]
    list_filter = ["created_at", "organization"]
    search_fields = ["name", "organization__name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    
    def short_url_count(self, obj):
        return obj.shorturls.count()
    short_url_count.short_description = "Short URLs"


@admin.register(ShortURL)
class ShortURLAdmin(admin.ModelAdmin):
    list_display = ["short_code", "namespace", "original_url", "created_by", "click_count", "is_active", "created_at"]
    list_filter = ["is_active", "created_at", "namespace__organization"]
    search_fields = ["short_code", "original_url", "title", "created_by__email"]
    readonly_fields = ["id", "click_count", "created_at", "updated_at", "full_short_url"]
    
    def full_short_url(self, obj):
        if obj.pk:
            return format_html(
                '<a href="{}" target="_blank">{}</a>',
                obj.get_full_short_url(),
                obj.get_full_short_url()
            )
        return "-"
    full_short_url.short_description = "Full Short URL"
