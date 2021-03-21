import uuid
from datetime import timedelta

from bifrost.models import BifrostFile
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import FieldPanel

from esite.user.models import SNEKCustomer
from esite.utils.edit_handlers import ReadOnlyPanel


def n_days_from_today(days):
    return timezone.now() + timedelta(days=days)


def fortnight_hence():
    return n_days_from_today(14)


def one_year_hence():
    return n_days_from_today(365)


class License(models.Model):
    key = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(default=False)
    owner = ParentalKey(SNEKCustomer, related_name="heimdall_licenses")
    remaining_uses = models.PositiveIntegerField(default=10)
    activate_remaining_uses_date = models.DateTimeField(
        default=fortnight_hence, blank=True
    )
    license_expire_date = models.DateTimeField(default=one_year_hence, blank=True)

    panels = [
        ReadOnlyPanel(
            "key", "Licence key", help_text="Generated automatically on save."
        ),
        FieldPanel("is_active"),
        FieldPanel("owner"),
        FieldPanel(
            "remaining_uses",
            help_text="Indicates how often this license can be used.",
        ),
        FieldPanel(
            "activate_remaining_uses_date",
            help_text="Indicates when the number of uses will be reduced on heimdall generation process.",
        ),
        FieldPanel("license_expire_date"),
    ]

    @classmethod
    def validate(cls, license_key: str):
        """Validate and get a license key.

        Args:
            license_key (str): A license key text.

        Returns:
            (License | Literal[False]): The validated licence or False.
        """
        license = cls.objects.filter(key=license_key).first()

        if (
            license
            and license.is_active
            and license.remaining_uses > 0
            and license.license_expire_date > timezone.now()
        ):
            return license

        return False

    @classmethod
    def use(cls, license_key: str):
        """Uses the license key regarding the remaining number of uses.

        Args:
            license_key (str):  A license key text.

        Returns:
            (int | bool): Remaining license uses or status on successful license usage.
        """
        license = cls.validate(license_key)

        if license:
            if license.activate_remaining_uses_date < timezone.now():
                license.remaining_uses -= 1
                license.save()

            return license

        return False


class AsyncHeimdallGeneration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    introspection = models.JSONField()
    bridge_drop_binary_name = models.CharField(max_length=255, null=True)
    bridge_drop_binary = models.BinaryField(null=True)
    bridge_drop_binary_saved = models.BooleanField(default=False)

    def save_bridge_drop(self):
        if not self.bridge_drop_binary_saved:
            private_file = BifrostFile()
            private_file.file.save(
                self.bridge_drop_binary_name, ContentFile(self.bridge_drop_binary)
            )

            self.bridge_drop_binary_name = private_file.file
            self.bridge_drop_binary_saved = True
            self.save()

        return private_file