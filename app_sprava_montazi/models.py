"""app_sprava_montazi_models"""

from rich.console import Console
from simple_history.models import HistoricalRecords

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import (
    PROTECT,
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    DecimalField,
    EmailField,
    FileField,
    ForeignKey,
    Model,
    PositiveIntegerField,
    SlugField,
    TextChoices,
    TextField,
)
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField

User = get_user_model()
cons: Console = Console()


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
    phone = PhoneNumberField(max_length=17, verbose_name="Telefon")
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
    history = HistoricalRecords()
    slug = SlugField(unique=True, blank=True)

    def price_per_km_float(self) -> float:
        if self.price_per_km is not None:
            return float(self.price_per_km)
        return 0.0

    def price_per_hour_float(self) -> float:
        if self.price_per_hour is not None:
            return float(self.price_per_hour)
        return 0.0

    def first_15(self) -> str:
        if self.notes:
            if len(self.notes) > 15:
                return f"{str(self.notes)[:15]}..."
            return str(self.notes)
        return "-"

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
    city = CharField(max_length=32, blank=True, verbose_name="Město")
    zip_code = CharField(max_length=5, verbose_name="PSČ")
    phone = PhoneNumberField(max_length=17, blank=True, verbose_name="Telefon")
    email = EmailField(blank=True, verbose_name="E-mail")
    incomplete = BooleanField(default=True, verbose_name="Neúplný záznam")
    history = HistoricalRecords()
    slug = SlugField(blank=True)

    def save(self, *args, **kwargs):
        self.incomplete = not all([self.street, self.city, self.phone])
        self.slug = slugify(f"{self.name}{self.city}{self.street}")
        super().save(*args, **kwargs)

    def first_15(self):
        if len(self.name) > 15:
            return f"{str(self.name)[:15]}..."
        return self.name

    def __str__(self) -> str:
        return str(self.name)


class DistribHub(Model):
    code = CharField(max_length=3, unique=True)
    city = CharField(max_length=32)
    history = HistoricalRecords()
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
        limit_choices_to={"active": True},
        verbose_name="Montážní tým",
    )
    notes = models.TextField(blank=True, verbose_name="Poznámky")

    history = HistoricalRecords()

    def notes_first_10(self) -> str:
        if self.notes:
            if len(self.notes) > 10:
                return f"{str(self.notes)[:10]}..."
            return self.notes
        return "-"

    def is_missing_team(self) -> bool:
        """
        Zkontroluje, jestli chybí tým pro montážní posádku.
        """
        return self.team is None and self.team_type == TeamType.BY_ASSEMBLY_CREW

    def zaterminovano(self) -> None:
        ready = (
            self.team
            and self.team_type == TeamType.BY_ASSEMBLY_CREW
            and self.status == Status.NEW
            and self.client
            and not self.client.incomplete
            and self.montage_termin
            and self.delivery_termin
        )
        if ready:
            self.status = Status.ADVICED
            if settings.DEBUG:
                cons.log(
                    f"zakazka: {self.order_number} presla do stavu: {Status.ADVICED}",
                    style="blue",
                )

    def __str__(self) -> str:
        return str(self.order_number)

    def save(self, *args, **kwargs):
        self.zaterminovano()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-order_number"]


class Article(Model):
    order = ForeignKey(
        Order, on_delete=PROTECT, related_name="articles", verbose_name="zakazka"
    )
    name = CharField(max_length=32, verbose_name="Název artiklu")
    price = DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Cena",
    )
    quantity = PositiveIntegerField(default=1, verbose_name="Množství")
    note = TextField(blank=True, verbose_name="Popis")
    history = HistoricalRecords()

    def first_15(self) -> str:
        if self.note:
            if len(self.note) > 15:
                return f"{str(self.note)[:15]}..."
            return self.note
        return "-"

    def __str__(self) -> str:
        return str(self.name)


class Upload(models.Model):
    file = FileField(upload_to="uploads/")
    created = DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return f"{self.file.name if self.file else 'No file'}"

    class Meta:
        ordering = ["-created"]


class CallLog(Model):
    client = ForeignKey(
        Client,
        on_delete=PROTECT,
        related_name="calls",
        verbose_name="Zákazník",
    )
    user = ForeignKey(User, on_delete=PROTECT, verbose_name="Uživatel")
    called_at = DateTimeField(auto_now_add=True, verbose_name="Čas volání")
    note = TextField(blank=True, verbose_name="Poznámka")
    was_successful = CharField(
        max_length=10, choices=AdviceStatus, verbose_name="Dovoláno"
    )
    history = HistoricalRecords()

    class Meta:
        ordering = ["-called_at"]

    def __str__(self):
        return f"{self.client.name} - {self.called_at.strftime('%Y-%m-%d %H:%M')}"
