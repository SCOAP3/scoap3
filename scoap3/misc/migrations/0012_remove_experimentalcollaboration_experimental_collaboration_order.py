# Generated by Django 4.2.2 on 2023-07-05 14:06

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("misc", "0011_alter_country_options_alter_affiliation_author_id_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="experimentalcollaboration",
            name="experimental_collaboration_order",
        ),
    ]
