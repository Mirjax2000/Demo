"""app_sprava_montazi_models"""

from decimal import Decimal
import hashlib

from rich.console import Console

# --- django
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import DecimalField, DateTimeField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import PROTECT, BooleanField, CharField, DateField, EmailField
from django.db.models import SlugField, PositiveIntegerField, ForeignKey, FileField
from django.db.models import JSONField, OneToOneField, TextField, TextChoices, Model

# --- pluginy
from simple_history.models import HistoricalRecords
from phonenumber_field.modelfields import PhoneNumberField

# --- šifrování osobních údajů (GDPR)
from app_sprava_montazi.encryption import EncryptedCharField, EncryptedEmailField

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

    def name_first_15(self) -> str:
        if self.name:
            if len(self.name) > 15:
                return f"{str(self.name)[:15]}..."
            return str(self.name)
        return "No Name"

    def __str__(self) -> str:
        return str(self.name)

    def save(self, *args, **kwargs):
        new_slug = slugify(self.name)
        if self.slug != new_slug:
            self.slug = new_slug
        super().save(*args, **kwargs)


class Client(Model):
    name = CharField(
        max_length=75,
        verbose_name="Jméno zákazníka",
    )
    street = EncryptedCharField(blank=True, verbose_name="Ulice")
    city = CharField(max_length=32, blank=True, verbose_name="Město")
    zip_code = CharField(max_length=5, verbose_name="PSČ")
    phone = EncryptedCharField(blank=True, verbose_name="Telefon")
    email = EncryptedEmailField(blank=True, verbose_name="E-mail")
    incomplete = BooleanField(default=True, verbose_name="Neúplný záznam")

    # --- GDPR ---
    consent_given = BooleanField(
        default=False,
        verbose_name="Souhlas se zpracováním",
        help_text="Zákazník udělil souhlas dle GDPR čl. 6",
    )
    consent_date = DateTimeField(
        null=True,
        blank=True,
        verbose_name="Datum souhlasu",
    )
    data_retention_until = DateField(
        null=True,
        blank=True,
        verbose_name="Uchovávat data do",
        help_text="Po tomto datu budou osobní údaje automaticky anonymizovány",
    )
    is_anonymized = BooleanField(
        default=False,
        verbose_name="Anonymizováno",
        help_text="Osobní údaje byly smazány dle GDPR",
    )

    history = HistoricalRecords()
    slug = SlugField(blank=True, unique=True)

    def first_15(self):
        if len(self.name) > 15:
            return f"{str(self.name)[:15]}..."
        return self.name

    def format_psc(self) -> str:
        number: str = str(self.zip_code)
        return f"{number[0:3]} {number[3:]}"

    def format_phone(self) -> str:
        if not self.phone:
            return ""
        number = str(self.phone)
        if number.startswith("+") and len(number) == 13:
            return f"{number[0:4]} {number[4:7]} {number[7:10]} {number[10:]}"
        return number

    def generate_slug(self) -> str:
        name_part = slugify(self.name)
        base = f"{self.name}{self.zip_code}"
        hash_part = hashlib.md5(base.encode()).hexdigest()[:10]
        return f"{name_part}-{hash_part}"

    def clean(self):
        if not self.name:
            raise ValidationError("Jméno zákazníka nesmí být prázdné.")
        if not self.zip_code:
            raise ValidationError("PSČ nesmí být prázdné.")
        if len(self.zip_code) != 5:
            raise ValidationError("PSČ musí mít přesně 5 znaků.")

    @staticmethod
    def normalize_phone(raw: str) -> str:
        """Normalizace telefonního čísla do E.164 (+420...)."""
        if not raw:
            return raw
        import phonenumbers
        try:
            parsed = phonenumbers.parse(raw, "CZ")
            if phonenumbers.is_valid_number(parsed):
                return phonenumbers.format_number(
                    parsed, phonenumbers.PhoneNumberFormat.E164
                )
        except phonenumbers.NumberParseException:
            pass
        return raw

    def save(self, *args, **kwargs):
        self.phone = self.normalize_phone(self.phone)
        self.incomplete = not all([self.street, self.city, self.phone])
        if not self.slug:
            self.slug = self.generate_slug()
        super().save(*args, **kwargs)

    def anonymize(self) -> None:
        """
        GDPR čl. 17 — Právo na výmaz (anonymizace).

        Nahradí osobní údaje za neidentifikovatelné hodnoty.
        Zachová vazby na zakázky pro statistické/účetní účely.
        """
        self.name = f"ANONYMIZOVÁNO-{self.pk}"
        self.street = ""
        self.city = ""
        self.phone = ""
        self.email = ""
        self.is_anonymized = True
        self.consent_given = False
        self.consent_date = None
        self.slug = slugify(f"anon-{self.pk}")
        self.save()
        # Anonymizovat i call logy
        self.calls.all().update(note="[ANONYMIZOVÁNO]")

    def __str__(self) -> str:
        return str(self.name)


class DataRetentionPolicy(Model):
    """
    GDPR čl. 5(1)(e) — Omezení uložení.

    Konfigurovatelná politika uchovávání osobních údajů.
    Po uplynutí doby se spustí automatická anonymizace.
    """

    RETENTION_CHOICES = [
        (365, "1 rok"),
        (730, "2 roky"),
        (1095, "3 roky"),
        (1825, "5 let"),
        (2555, "7 let"),
        (3650, "10 let"),
    ]

    name = CharField(
        max_length=100,
        unique=True,
        verbose_name="Název politiky",
    )
    retention_days = PositiveIntegerField(
        default=1825,
        choices=RETENTION_CHOICES,
        verbose_name="Doba uchovávání (dní)",
        help_text="Počet dní od poslední zakázky zákazníka",
    )
    description = TextField(
        blank=True,
        verbose_name="Popis",
    )
    is_active = BooleanField(
        default=True,
        verbose_name="Aktivní",
    )
    auto_anonymize = BooleanField(
        default=False,
        verbose_name="Automatická anonymizace",
        help_text="Po uplynutí doby automaticky anonymizovat osobní údaje",
    )
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Politika uchovávání dat"
        verbose_name_plural = "Politiky uchovávání dat"

    def __str__(self) -> str:
        return f"{self.name} ({self.get_retention_days_display()})"


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
    team = ForeignKey(
        Team,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        limit_choices_to={"active": True},
        verbose_name="Montážní tým",
    )

    mail_datum_sended = DateTimeField(
        blank=True,
        null=True,
        verbose_name="Protocol mail odeslan",
    )

    mail_team_sended = CharField(
        blank=True,
        verbose_name="jakemu tymu byl poslan email",
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

    evidence_termin = DateField(
        verbose_name="Termín evidence",
    )

    delivery_termin = DateField(
        blank=True,
        null=True,
        verbose_name="Termín doručení",
    )

    montage_termin = DateTimeField(
        blank=True,
        null=True,
        verbose_name="Termín montáže",
    )

    team_type = CharField(
        max_length=32,
        choices=TeamType.choices,
        default=TeamType.BY_ASSEMBLY_CREW,
        verbose_name="Realizace kým",
    )
    notes = TextField(blank=True, verbose_name="Poznámky")

    naklad = DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Náklad",
        help_text="Kolik zakázka stála (výdaje)",
    )
    vynos = DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Výnos",
        help_text="Kolik za zakázku dostanu zaplaceno (příjem)",
    )

    history = HistoricalRecords()

    def profit(self) -> Decimal:
        if self.vynos is not None and self.naklad is not None:
            return self.vynos - self.naklad
        return Decimal(0)

    def format_datetime(self, value) -> str:
        if value is None:
            return ""
        return value.strftime("%d.%m.%Y / %H:%M")

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

    def zaterminovano_with_montage_team(self) -> None:
        ready = (
            self.team
            and self.status == Status.NEW
            and self.team_type == TeamType.BY_ASSEMBLY_CREW
            and self.client
            and not self.client.incomplete
            and self.evidence_termin
            and self.delivery_termin
            and self.montage_termin
            and self.vynos is not None
            and self.naklad is not None
        )
        if ready:
            self.status = Status.ADVICED
            if settings.DEBUG:
                cons.log(
                    f"zakazka: {self.order_number} presla do stavu: {Status.ADVICED}",
                    style="blue",
                )

    def zaterminovano_with_delivery_team(self) -> None:
        ready = (
            not self.team
            and self.status == Status.NEW
            and self.team_type == TeamType.BY_DELIVERY_CREW
            and self.client
            and self.evidence_termin
            and self.delivery_termin
            and not self.montage_termin
            and self.vynos is not None
            and self.naklad is not None
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
        self.zaterminovano_with_montage_team()
        self.zaterminovano_with_delivery_team()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-evidence_termin"]


class Article(Model):
    order = ForeignKey(
        Order, on_delete=PROTECT, related_name="articles", verbose_name="zakazka"
    )
    name = CharField(max_length=32, verbose_name="Název artiklu")
    quantity = PositiveIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(99),
        ],
        verbose_name="Množství",
    )
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


class OrderPDFStorage(Model):
    order = OneToOneField(
        Order, on_delete=PROTECT, related_name="pdf", verbose_name="Objednávka"
    )
    team = CharField(blank=False, max_length=32, verbose_name="montazni tym")
    file = FileField(upload_to="stored_pdfs/", verbose_name="PDF soubor")
    created = DateTimeField(auto_now=True, verbose_name="Čas uložení")
    history = HistoricalRecords()

    def __str__(self):
        return (
            f"PDF pro objednávku {self.order.order_number} "
            f"s montaznim tymem {self.team}"
        )

    class Meta:
        ordering = ["-created"]


def upload_to_order_folder(instance, filename):
    order_number = instance.order.order_number.upper()
    return f"montage_images/{order_number}/{filename}"


class OrderMontazImage(Model):
    order = ForeignKey(
        Order,
        on_delete=PROTECT,
        related_name="montage_images",
        verbose_name="Fotky z montaze",
    )
    position = PositiveIntegerField(default=0)
    created = DateTimeField(auto_now_add=True, verbose_name="Cas ulozeni")
    alt_text = CharField(max_length=255, blank=True, verbose_name="Popis obrazku")

    image = FileField(upload_to=upload_to_order_folder)

    def __str__(self):
        return f"Fotka k zakázce {self.order.pk} z {self.created}"


class OrderBackProtocol(Model):
    order = OneToOneField(
        Order,
        on_delete=PROTECT,
        related_name="back_protocol",
        verbose_name="Objednávka",
    )
    file = FileField(upload_to="recieved_protocols/", verbose_name="Recieved protocols")
    alt_text = CharField(max_length=255, blank=True, verbose_name="Popis obrazku")
    created = DateTimeField(auto_now=True, verbose_name="Čas uložení")
    history = HistoricalRecords()

    def __str__(self):
        return f"Recieved protokol pro objednávku {self.order.order_number}"

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


class OrderBackProtocolToken(Model):
    order = OneToOneField("Order", on_delete=PROTECT)
    token = CharField(max_length=64, unique=True)
    created = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order} - {self.token}"


class AppSetting(Model):
    name: CharField = CharField(max_length=100, unique=True)
    data: JSONField = JSONField()
    history = HistoricalRecords()

    def __str__(self) -> str:
        return str(self.name)


class FinanceRevenueItem(Model):
    order = ForeignKey(
        Order,
        on_delete=PROTECT,
        related_name="revenue_items",
        verbose_name="Zakázka",
    )
    description = CharField(max_length=128, blank=True, verbose_name="Popis")
    amount = DecimalField(max_digits=10, decimal_places=2, verbose_name="Částka")
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["-created"]

    def __str__(self) -> str:
        return f"{self.order.order_number} - {self.amount}"


class FinanceCostItem(Model):
    order = ForeignKey(
        Order,
        on_delete=PROTECT,
        related_name="cost_items",
        verbose_name="Zakázka",
    )
    team = ForeignKey(Team, on_delete=PROTECT, null=True, blank=True, verbose_name="Tým")
    description = CharField(max_length=128, blank=True, verbose_name="Popis")
    amount = DecimalField(max_digits=10, decimal_places=2, verbose_name="Částka")
    carrier_confirmed = BooleanField(default=False, verbose_name="Potvrzeno dopravcem")
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["-created"]

    def __str__(self) -> str:
        return f"{self.order.order_number} - {self.amount}"
