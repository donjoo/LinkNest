import uuid
import string
import random
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Organization(models.Model):
    """Organization model for grouping users and namespaces."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text=_("Organization name"))
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_organizations",
        help_text=_("Organization owner")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")

    def __str__(self):
        return self.name

    def get_members(self):
        """Get all members of this organization."""
        return User.objects.filter(organizationmembership__organization=self)

    def get_admin_members(self):
        """Get all admin members of this organization."""
        return User.objects.filter(
            organizationmembership__organization=self,
            organizationmembership__role=OrganizationMembership.Role.ADMIN
        )


class OrganizationMembership(models.Model):
    """Membership model for users in organizations with roles."""
    
    class Role(models.TextChoices):
        ADMIN = "admin", _("Admin")
        EDITOR = "editor", _("Editor")
        VIEWER = "viewer", _("Viewer")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="organization_memberships"
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships"
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.VIEWER,
        help_text=_("User role in the organization")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "organization"]
        ordering = ["-created_at"]
        verbose_name = _("Organization Membership")
        verbose_name_plural = _("Organization Memberships")

    def __str__(self):
        return f"{self.user.email} - {self.organization.name} ({self.role})"

    def clean(self):
        """Validate that the organization owner is always an admin."""
        if self.organization.owner == self.user and self.role != self.Role.ADMIN:
            raise ValidationError(_("Organization owner must be an admin."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Namespace(models.Model):
    """Namespace model for organizing short URLs within organizations."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="namespaces"
    )
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text=_("Globally unique namespace name")
    )
    description = models.TextField(blank=True, help_text=_("Namespace description"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Namespace")
        verbose_name_plural = _("Namespaces")

    def __str__(self):
        return f"{self.organization.name}/{self.name}"

    def get_short_urls(self):
        """Get all short URLs in this namespace."""
        return self.shorturls.all()


class ShortURL(models.Model):
    """Short URL model for storing shortened URLs."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    namespace = models.ForeignKey(
        Namespace,
        on_delete=models.CASCADE,
        related_name="shorturls"
    )
    original_url = models.URLField(help_text=_("Original URL to be shortened"))
    short_code = models.CharField(
        max_length=50,
        help_text=_("Short code for the URL (unique within namespace)")
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_short_urls"
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Optional title for the short URL")
    )
    description = models.TextField(
        blank=True,
        help_text=_("Optional description for the short URL")
    )
    is_active = models.BooleanField(default=True, help_text=_("Whether the short URL is active"))
    click_count = models.PositiveIntegerField(default=0, help_text=_("Number of clicks"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["namespace", "short_code"]
        ordering = ["-created_at"]
        verbose_name = _("Short URL")
        verbose_name_plural = _("Short URLs")

    def __str__(self):
        return f"{self.namespace.name}/{self.short_code}"

    def get_full_short_url(self):
        """Get the full short URL."""
        # This would typically use your domain, for now using localhost
        return f"http://localhost:8000/{self.namespace.name}/{self.short_code}"

    def increment_click_count(self):
        """Increment the click count."""
        self.click_count += 1
        self.save(update_fields=["click_count"])

    @staticmethod
    def generate_short_code(length=6):
        """Generate a random alphanumeric short code."""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    def clean(self):
        """Validate the short code and ensure it's unique within the namespace."""
        if not self.short_code:
            # Generate a short code if not provided
            self.short_code = self.generate_short_code()
        
        # Ensure short code is unique within the namespace
        if ShortURL.objects.filter(
            namespace=self.namespace,
            short_code=self.short_code
        ).exclude(pk=self.pk).exists():
            raise ValidationError(
                _("Short code must be unique within the namespace.")
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
