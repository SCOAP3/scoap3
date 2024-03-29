# Generated by Django 4.2.5 on 2023-12-18 13:39

from django.db import migrations
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from scoap3.users.models import User


def create_export_permission(apps, schema_editor):
    content_type = ContentType.objects.get_for_model(User)
    Permission.objects.get_or_create(
        codename='partner_export',
        name='Can partner export',
        content_type=content_type,
    )

class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_export_permission),
    ]
