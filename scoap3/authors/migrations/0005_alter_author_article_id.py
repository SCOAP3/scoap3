# Generated by Django 4.2.5 on 2024-09-18 12:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("articles", "0014_compliancereport_check_authors_affiliation_and_more"),
        ("authors", "0004_alter_authoridentifier_author_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="author",
            name="article_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="authors",
                to="articles.article",
            ),
        ),
    ]