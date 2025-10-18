"""
URL redirect views.

Moved from apps.links.redirect_views - handles short URL redirects.
"""
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404
from .models import ShortURL


def redirect_short_url(request, namespace_name, short_code):
    """Handle short URL redirects."""
    try:
        short_url = get_object_or_404(
            ShortURL,
            namespace__name=namespace_name,
            short_code=short_code,
            is_active=True
        )
        
        # Increment click count
        short_url.increment_click_count()
        
        # Redirect to the original URL
        return redirect(short_url.original_url)
        
    except ShortURL.DoesNotExist:
        raise Http404("Short URL not found or inactive")
