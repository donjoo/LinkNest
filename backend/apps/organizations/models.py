"""
Organization models.

Moved from apps.links.models - handles organization, memberships, roles, and invitations.
"""
import uuid
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