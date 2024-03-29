# Generated by Django 4.2 on 2023-05-16 15:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("authors", "0001_initial"),
        ("articles", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Affiliation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("value", models.CharField(max_length=255)),
                ("organization", models.CharField(max_length=255)),
                ("author_id", models.ManyToManyField(to="authors.author")),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="Country",
            fields=[
                (
                    "code",
                    models.CharField(
                        max_length=2, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
            ],
            options={
                "ordering": ["code"],
            },
        ),
        migrations.CreateModel(
            name="License",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("url", models.URLField(blank=True)),
                ("name", models.CharField(max_length=255)),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="Publisher",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="RelatedMaterial",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("doi", models.CharField(max_length=255)),
                (
                    "related_material_type",
                    models.CharField(
                        choices=[("dataset", "Dataset"), ("software", "Software")],
                        max_length=255,
                    ),
                ),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="PublicationInfo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("journal_volume", models.CharField(blank=True, max_length=255)),
                ("journal_title", models.CharField(max_length=255)),
                ("journal_issue", models.CharField(blank=True, max_length=255)),
                ("page_start", models.PositiveIntegerField()),
                ("page_end", models.PositiveIntegerField()),
                ("artid", models.CharField(max_length=255)),
                ("volume_year", models.CharField(max_length=255)),
                ("journal_issue_date", models.DateField()),
                (
                    "article_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="articles.article",
                    ),
                ),
                (
                    "publisher",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="misc.publisher"
                    ),
                ),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="InstitutionIdentifier",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "identifier_type",
                    models.CharField(choices=[("ROR", "Ror")], max_length=255),
                ),
                ("identifier_value", models.CharField(max_length=255)),
                (
                    "affiliation_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="misc.affiliation",
                    ),
                ),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="Funder",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("funder_identifier", models.CharField(max_length=255)),
                ("funder_name", models.CharField(max_length=255)),
                ("award_number", models.CharField(max_length=255)),
                ("article_id", models.ManyToManyField(to="articles.article")),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="ExperimentalCollaboration",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("experimental_collaboration_order", models.IntegerField()),
                ("article_id", models.ManyToManyField(to="articles.article")),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="Copyright",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("statement", models.CharField(max_length=255)),
                ("holder", models.CharField(max_length=255)),
                ("year", models.PositiveIntegerField()),
                (
                    "article_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="articles.article",
                    ),
                ),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="ArticleArxivCategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "category",
                    models.CharField(choices=[("qua.223", "Qua223")], max_length=255),
                ),
                ("primary", models.BooleanField()),
                (
                    "article_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="articles.article",
                    ),
                ),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.AddField(
            model_name="affiliation",
            name="country",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="misc.country"
            ),
        ),
        migrations.AddIndex(
            model_name="institutionidentifier",
            index=models.Index(
                fields=["affiliation_id", "identifier_type", "identifier_value"],
                name="misc_instit_affilia_b35011_idx",
            ),
        ),
    ]
