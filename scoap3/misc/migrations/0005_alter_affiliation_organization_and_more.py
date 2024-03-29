# Generated by Django 4.2.2 on 2023-06-14 10:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("misc", "0004_alter_affiliation_organization_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="affiliation",
            name="organization",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="copyright",
            name="holder",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="copyright",
            name="statement",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="experimentalcollaboration",
            name="name",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="license",
            name="name",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="publicationinfo",
            name="artid",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="publicationinfo",
            name="journal_issue",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="publicationinfo",
            name="journal_volume",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]
