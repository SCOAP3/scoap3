# Generated by Django 4.2.5 on 2024-07-19 11:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("misc", "0017_alter_copyright_article_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="publicationinfo",
            name="volume_year",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
