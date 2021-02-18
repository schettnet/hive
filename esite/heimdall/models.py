import uuid
from datetime import timedelta

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

        if license and license.is_active and license.license_end > timezone.now():
            return True

        return False
