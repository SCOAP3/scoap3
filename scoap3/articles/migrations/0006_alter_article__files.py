# Generated by Django 4.2.2 on 2023-07-05 14:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("articles", "0005_articlefile_rename_created_at_article__created_at_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="article",
            name="_files",
            field=models.ManyToManyField(blank=True, to="articles.articlefile"),
        ),
    ]
