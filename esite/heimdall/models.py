import uuid
from datetime import timedelta

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import models
from django.utils import timezone
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import FieldPanel

from esite.user.models import SNEKCustomer
from esite.utils.edit_handlers import ReadOnlyPanel


def one_year_from_today():
    return timezone.now() + timedelta(days=365)


class License(models.Model):
    key = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(default=False)
    owner = ParentalKey(SNEKCustomer, related_name="heimdall_licenses")
    license_expire_date = models.DateTimeField(default=one_year_from_today)

    panels = [
        ReadOnlyPanel(
            "key", "Licence key", help_text="Generated automatically when saving"
        ),
        FieldPanel("is_active"),
        FieldPanel("owner"),
        FieldPanel("license_expire_date"),
    ]

    @classmethod
    def validate(cls, license_key: str):
        license = cls.objects.filter(key=license_key).first()

        if (
            license
            and license.is_active
            and license.license_expire_date > timezone.now()
        ):
            return True

        return False


class AsyncHeimdallGeneration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    introspection = models.JSONField()
    bridge_drop_binary_name = models.CharField(max_length=255, null=True)
    bridge_drop_binary = models.BinaryField(null=True)
    bridge_drop_binary_saved = models.BooleanField(default=False)

    def save_bridge_drop(self):
        if not self.bridge_drop_binary_saved:
            content = ContentFile(self.bridge_drop_binary)
            self.bridge_drop_binary_name = default_storage.save(
                self.bridge_drop_binary_name, content
            )

            self.bridge_drop_binary_saved = True
            self.save()

        return settings.BASE_URL + default_storage.url(self.bridge_drop_binary_name)
