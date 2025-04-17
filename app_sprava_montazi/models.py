"""app_sprava_montazi_models"""

from django.db import models
from django.db.models import (
    PROTECT,
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    DecimalField,
    EmailField,
    ForeignKey,
    IntegerField,
    Model,
    SlugField,
    TextChoices,
    TextField,
)
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField


class Status(TextChoices):
    NEW = "New", "Nový"
    ADVICED = "Adviced", "Zatermínováno"
    REALIZED = "Realized", "Realizováno"
    BILLED = "Billed", "Vyúčtovaný"
    CANCELED = "Canceled", "Zrušeno"


class TeamType(TextChoices):
    BY_CUSTOMER = "By customer", "Zákazníkem"
    BY_DELIVERY_CREW = "By delivery crew", "Dopravcem"
    BY_ASSEMBLY_CREW = "By assembly crew", "Montážníky"


class AdviceStatus(TextChoices):
    SUCCESS = "Success", "Úspěšný"
    FAILED = "Failed", "Neúspěšný"


class Whom(TextChoices):
    TO_CUSTOMER = "To customer", "Zákazníkovi"
    TO_DELIVERY_CREW = "To delivery crew", "Dopravci"
    TO_ASSEMBLY_CREW = "To assembly crew", "Montážníkům"
    TO_CUSTOMER_CARE = "To customer care", "Zákaznickému servisu"


class Team(Model):
    name = CharField(
        max_length=32,
        unique=True,
        verbose_name="Společnost",
    )
    city = CharField(max_length=32, verbose_name="Město")
    region = CharField(max_length=32, blank=True, verbose_name="Region")
    phone = PhoneNumberField(max_length=17)
    email = EmailField(max_length=64, verbose_name="E-mail")
    active = BooleanField(default=True, verbose_name="Aktivní")
    price_per_hour = DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Cena za hodinu",
    )
    price_per_km = DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Cena za km",
    )
    notes = TextField(blank=True, verbose_name="Poznámka")
    slug = SlugField(unique=True, blank=True)

    def __str__(self) -> str:
        return str(self.name)

    def save(self, *args, **kwargs):
        if self.slug != self.name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Client(Model):
    name = CharField(
        max_length=50,
        verbose_name="Jméno zákazníka",
    )
    street = CharField(max_length=50, blank=True, verbose_name="Ulice")
    number = CharField(
        max_length=6,
        blank=True,
        verbose_name="Číslo popisné",
    )
    city = CharField(max_length=32, verbose_name="Město")
    zip_code = CharField(max_length=5, verbose_name="PSČ")
    phone = PhoneNumberField(max_length=17, blank=True)
    email = EmailField(blank=True, verbose_name="E-mail")
    incomplete = BooleanField(default=True, verbose_name="Neúplný záznam")
    slug = SlugField(blank=True)

    def save(self, *args, **kwargs):
        self.incomplete = not all([self.street, self.number, self.city, self.phone])
        self.slug = slugify(f"{self.name}{self.city}{self.street}{self.number}")
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name}"


class Article(Model):
    article = CharField(max_length=32, verbose_name="Artikl")
    price = DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Cena",
    )
    quantity = IntegerField(null=True, blank=True, verbose_name="Množství")
    note = TextField(blank=True, verbose_name="Popis")

    def __str__(self) -> str:
        return str(self.article)


class Order(Model):
    """Zakazka"""

    order_number = CharField(
        max_length=32,
        unique=True,
        verbose_name="Číslo zakázky",
    )
    mandant = CharField(max_length=4, verbose_name="Mandant")
    distrib_hub = CharField(max_length=32, verbose_name="Místo určení")
    status = CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name="Stav",
    )
    client = ForeignKey(
        Client,
        null=True,
        blank=True,
        on_delete=PROTECT,
        verbose_name="Zákazník",
    )

    evidence_termin = DateField(
        null=True,
        blank=False,
        verbose_name="Termín evidence",
    )
    delivery_termin = DateTimeField(
        null=True,
        blank=True,
        verbose_name="Termín doručení",
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Artikl",
    )
    # advice = models.ForeignKey(
    #     "Advice",
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     verbose_name="Avizace",
    # )
    team_type = models.CharField(
        max_length=32,
        blank=True,
        choices=TeamType.choices,
        default=TeamType.BY_CUSTOMER,
        verbose_name="Realizace kým",
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Montážní tým",
    )
    notes = models.TextField(blank=True, verbose_name="Poznámky")
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Vytvořeno",
    )
    updated = models.DateTimeField(
        auto_now=True,
        verbose_name="Upraveno",
    )

    def __str__(self) -> str:
        return str(self.order_number)
