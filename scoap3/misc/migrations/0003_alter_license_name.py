# Generated by Django 4.2 on 2023-06-05 14:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("misc", "0002_alter_publicationinfo_artid_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="license",
            name="name",
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
