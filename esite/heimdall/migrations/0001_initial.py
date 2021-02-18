# Generated by Django 3.1.6 on 2021-02-18 20:05

from django.db import migrations, models
import django.db.models.deletion
import esite.heimdall.models
import modelcluster.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0002_snekcustomer'),
    ]

    operations = [
        migrations.CreateModel(
            name='License',
            fields=[
                ('key', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('is_active', models.BooleanField(default=False)),
                ('license_expire_date', models.DateTimeField(default=esite.heimdall.models.one_year_from_today)),
                ('owner', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='heimdall_licenses', to='user.snekcustomer')),
            ],
        ),
    ]
