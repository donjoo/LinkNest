"""
URL admin.

Moved from apps.links.admin - handles namespace and short URL admin interface.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Namespace, ShortURL


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