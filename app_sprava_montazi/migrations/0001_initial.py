# Generated by Django 5.2 on 2025-05-08 14:42

import django.db.models.deletion
import phonenumber_field.modelfields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Client",
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
                    "name",
                    models.CharField(max_length=75, verbose_name="Jméno zákazníka"),
                ),
                (
                    "street",
                    models.CharField(blank=True, max_length=50, verbose_name="Ulice"),
                ),
                (
                    "city",
                    models.CharField(blank=True, max_length=32, verbose_name="Město"),
                ),
                ("zip_code", models.CharField(max_length=5, verbose_name="PSČ")),
                (
                    "phone",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=17, region=None, verbose_name="Telefon"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="E-mail"
                    ),
                ),
                (
                    "incomplete",
                    models.BooleanField(default=True, verbose_name="Neúplný záznam"),
                ),
                ("slug", models.SlugField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="DistribHub",
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
                ("code", models.CharField(max_length=3, unique=True)),
                ("city", models.CharField(max_length=32)),
                ("slug", models.SlugField(blank=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Team",
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
                    "name",
                    models.CharField(
                        max_length=32, unique=True, verbose_name="Společnost"
                    ),
                ),
                ("city", models.CharField(max_length=32, verbose_name="Město")),
                (
                    "region",
                    models.CharField(blank=True, max_length=32, verbose_name="Region"),
                ),
                (
                    "phone",
                    phonenumber_field.modelfields.PhoneNumberField(
                        max_length=17, region=None, verbose_name="Telefon"
                    ),
                ),
                (
                    "email",
                    models.EmailField(blank=True, max_length=64, verbose_name="E-mail"),
                ),
                ("active", models.BooleanField(default=True, verbose_name="Aktivní")),
                (
                    "price_per_hour",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=6,
                        null=True,
                        verbose_name="Cena za hodinu",
                    ),
                ),
                (
                    "price_per_km",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=6,
                        null=True,
                        verbose_name="Cena za km",
                    ),
                ),
                ("notes", models.TextField(blank=True, verbose_name="Poznámka")),
                ("slug", models.SlugField(blank=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Upload",
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
                ("file", models.FileField(upload_to="uploads/")),
                ("created", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-created"],
            },
        ),
        migrations.CreateModel(
            name="Order",
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
                    "order_number",
                    models.CharField(
                        max_length=32, unique=True, verbose_name="Číslo zakázky"
                    ),
                ),
                ("mandant", models.CharField(max_length=4, verbose_name="Mandant")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("New", "Nový"),
                            ("Adviced", "Zatermínováno"),
                            ("Realized", "Realizováno"),
                            ("Billed", "Vyúčtovaný"),
                            ("Canceled", "Zrušeno"),
                            ("Hidden", "Skryto"),
                        ],
                        default="New",
                        max_length=32,
                        verbose_name="Stav",
                    ),
                ),
                (
                    "delivery_termin",
                    models.DateField(
                        blank=True, null=True, verbose_name="Termín doručení"
                    ),
                ),
                ("evidence_termin", models.DateField(verbose_name="Termín evidence")),
                (
                    "montage_termin",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Termín montáže"
                    ),
                ),
                (
                    "team_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("By_customer", "Zákazníkem"),
                            ("By_delivery_crew", "Dopravcem"),
                            ("By_assembly_crew", "Montážníky"),
                        ],
                        default="By_assembly_crew",
                        max_length=32,
                        verbose_name="Realizace kým",
                    ),
                ),
                ("notes", models.TextField(blank=True, verbose_name="Poznámky")),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, verbose_name="Vytvořeno"),
                ),
                (
                    "updated",
                    models.DateTimeField(auto_now=True, verbose_name="Upraveno"),
                ),
                (
                    "client",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="app_sprava_montazi.client",
                        verbose_name="Zákazník",
                    ),
                ),
                (
                    "distrib_hub",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="app_sprava_montazi.distribhub",
                        verbose_name="Místo určení",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to={"active": True},
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="app_sprava_montazi.team",
                        verbose_name="Montážní tým",
                    ),
                ),
            ],
            options={
                "ordering": ["-order_number"],
            },
        ),
        migrations.CreateModel(
            name="Article",
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
                ("name", models.CharField(max_length=32, verbose_name="Název artiklu")),
                (
                    "price",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=10,
                        null=True,
                        verbose_name="Cena",
                    ),
                ),
                (
                    "quantity",
                    models.PositiveIntegerField(default=1, verbose_name="Množství"),
                ),
                ("note", models.TextField(blank=True, verbose_name="Popis")),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="articles",
                        to="app_sprava_montazi.order",
                    ),
                ),
            ],
        ),
    ]
