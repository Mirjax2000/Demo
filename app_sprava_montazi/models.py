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
    HIDDEN = "Hidden", "Skryto"


class TeamType(TextChoices):
    BY_CUSTOMER = "By_customer", "Zákazníkem"
    BY_DELIVERY_CREW = "By_delivery_crew", "Dopravcem"
    BY_ASSEMBLY_CREW = "By_assembly_crew", "Montážníky"


class AdviceStatus(TextChoices):
    SUCCESS = "Success", "Úspěšný"
    FAILED = "Failed", "Neúspěšný"


class Whom(TextChoices):
    TO_CUSTOMER = "To_customer", "Zákazníkovi"
    TO_DELIVERY_CREW = "To_delivery_crew", "Dopravci"
    TO_ASSEMBLY_CREW = "To_assembly_crew", "Montážníkům"
    TO_CUSTOMER_CARE = "To_customer_care", "Zákaznickému servisu"


class Team(Model):
    name = CharField(
        max_length=32,
        unique=True,
        verbose_name="Společnost",
    )
    city = CharField(max_length=32, verbose_name="Město")
    region = CharField(max_length=32, blank=True, verbose_name="Region")
    phone = PhoneNumberField(max_length=17)
    email = EmailField(max_length=64, blank=True, verbose_name="E-mail")
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
        max_length=75,
        verbose_name="Jméno zákazníka",
    )
    street = CharField(max_length=50, blank=True, verbose_name="Ulice")
    number = CharField(
        max_length=6,
        blank=True,
        verbose_name="Číslo popisné",
    )
    city = CharField(max_length=32, blank=True, verbose_name="Město")
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
        if len(self.name) > 15:
            return f"{str(self.name)[:15]} ..."
        return self.name


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


class DistribHub(Model):
    code = CharField(max_length=3, unique=True)
    city = CharField(max_length=32)
    slug = SlugField(blank=True, unique=True)

    def save(self, *args, **kwargs):
        if self.slug != slugify(f"{self.code}-{self.city}"):
            self.slug = slugify(f"{self.code}-{self.city}")
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.code}-{self.city}"


class Order(Model):
    """Zakazka"""

    order_number = CharField(
        max_length=32,
        unique=True,
        verbose_name="Číslo zakázky",
    )
    distrib_hub = ForeignKey(
        DistribHub,
        on_delete=PROTECT,
        verbose_name="Místo určení",
    )
    mandant = CharField(max_length=4, verbose_name="Mandant")
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

    delivery_termin = DateField(
        blank=True,
        null=True,
        verbose_name="Termín doručení",
    )
    evidence_termin = DateField(
        verbose_name="Termín evidence",
    )
    montage_termin = DateTimeField(
        blank=True,
        null=True,
        verbose_name="Termín montáže",
    )
    # article = models.ForeignKey(
    #     Article,
    #     on_delete=models.PROTECT,
    #     null=True,
    #     blank=True,
    #     verbose_name="Artikl",
    # )
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
        default=TeamType.BY_ASSEMBLY_CREW,
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

    def notes_first_10(self) -> str | None:
        if self.notes:
            notes: str = str(self.notes)[:10]
            return notes
        return None

    def is_missing_team(self) -> bool:
        """
        Zkontroluje, jestli chybí tým pro montážní posádku.
        Tato metoda ověřuje, zda není přiřazen žádný tým, pokud je team_type nastaven na BY_ASSEMBLY_CREW.
        """
        return self.team is None and self.team_type == TeamType.BY_ASSEMBLY_CREW

    def __str__(self) -> str:
        return str(self.order_number)

    class Meta:
        ordering = ["-created"]


class Upload(models.Model):
    file = models.FileField(upload_to="uploads/")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.file}"

    class Meta:
        ordering = ["-created"]
