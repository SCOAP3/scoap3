# Generated by Django 4.2.2 on 2023-07-10 15:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("misc", "0014_alter_affiliation_value_alter_publisher_name_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="experimentalcollaboration",
            name="name",
            field=models.TextField(blank=True, default=""),
        ),
    ]
