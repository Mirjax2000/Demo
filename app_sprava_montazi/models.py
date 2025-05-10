"""app_sprava_montazi_models"""

from django.db import models
from django.db.models import (
    PROTECT,
    SET_NULL,
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
    PositiveIntegerField,
    JSONField,
)
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# ---
User = get_user_model()
# ---


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
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, verbose_name="Vytvoreno kym"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Vytvoreno kdy")
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
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, verbose_name="Vytvoreno kym"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Vytvoreno kdy")
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
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, verbose_name="Vytvoreno kym"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Vytvoreno kdy")
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
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name="Kdo to vytvoril"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Vytvoreno kdy")

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Upraveno kdy",
    )

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

    def __str__(self) -> str:
        return str(self.order_number)

    class Meta:
        ordering = ["-order_number"]


class Article(Model):
    order = ForeignKey(
        Order,
        on_delete=PROTECT,
        related_name="articles",
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
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, verbose_name="Vytvoreno kym"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Vytvoreno kdy")

    def first_15(self) -> str:
        if self.note:
            if len(self.note) > 15:
                return f"{str(self.note)[:15]}..."
            return self.note
        return "-"

    def __str__(self) -> str:
        return str(self.name)


class Upload(models.Model):
    file = models.FileField(upload_to="uploads/")
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, verbose_name="Vytvoreno kym"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Vytvoreno kdy")

    def __str__(self) -> str:
        return f"{self.file}"

    class Meta:
        ordering = ["-created"]


class LogEntry(models.Model):
    action = models.CharField(max_length=100)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
