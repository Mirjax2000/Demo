from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Status(models.TextChoices):
    NEW = "New", "Nový"
    ADVICED = "Adviced", "Zatermínováno"
    REALIZED = "Realized", "Realizováno"
    CANCELED = "Canceled", "Zrušeno"
    BILLED = "Billed", "Vyúčtovaný"


class AdviceStatus(models.TextChoices):
    SUCCESS = "Success", "Úspěšný"
    FAILED = "Failed", "Neúspěšný"


class TeamType(models.TextChoices):
    EMPTY = "Empty", "Nevyplneno"
    BY_CUSTOMER = "By customer", "Zákazníkem"
    BY_DELIVERY_CREW = "By delivery crew", "Dopravcem"
    BY_ASSEMBLY_CREW = "By assembly crew", "Montážníky"


WHOM_CHOICES: list[tuple[str, str]] = [
    ("To customer", "Zákazníkovi"),
    ("To delivery crew", "Dopravci"),
    ("To assembly crew", "Montážníkům"),
    ("To customer care", "Zákaznickému servisu"),
]


class Team(models.Model):
    company = models.CharField(max_length=32, verbose_name="Společnost")
    city = models.CharField(max_length=32, verbose_name="Město")
    region = models.CharField(max_length=32, blank=True, verbose_name="Region")
    phone = PhoneNumberField(blank=True)
    email = models.EmailField(max_length=64, blank=True, verbose_name="E-mail")
    web = models.CharField(max_length=64, blank=True, verbose_name="Web")
    active = models.BooleanField(default=True, verbose_name="Aktivní")
    price_per_hour = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Cena za hodinu",
    )
    price_per_km = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Cena za km",
    )
    termin = models.TextField(blank=True, verbose_name="Termín")
    notes = models.TextField(blank=True, verbose_name="Poznámka")

    def __str__(self) -> str:
        return str(self.company)


class Order(models.Model):
    """Zakazka"""

    order_number = models.CharField(
        max_length=32,
        unique=True,
        verbose_name="Číslo zakázky",
    )
    mandant = models.CharField(max_length=4, verbose_name="Mandant")
    # store = models.ForeignKey(
    #     "Store",
    #     on_delete=models.SET_NULL,
    #     verbose_name="OD/sklad",
    # )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.NEW,
        blank=True,
        verbose_name="Stav",
    )
    customer_name = models.CharField(max_length=64, verbose_name="Jméno zákazníka")
    zip_code = models.CharField(max_length=5, verbose_name="PSČ")
    # place = models.ForeignKey(
    #     "Place",
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=False,
    #     verbose_name="Oblast",
    # )
    # contact = models.ForeignKey(
    #     "Contact",
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     verbose_name="Kontakt",
    # )
    evidence_termin = models.DateField(
        null=True, blank=False, verbose_name="Termín evidence"
    )
    delivery_termin = models.DateField(
        null=True, blank=True, verbose_name="Termín doručení"
    )
    # article = models.ForeignKey(
    #     "Article",
    #     on_delete=models.SET_NULL,
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
        default=TeamType.EMPTY,
        verbose_name="Realizace kým",
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Montážní tým",
    )
    notes = models.TextField(blank=True, verbose_name="Poznámky")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Vytvořeno")
    updated = models.DateTimeField(auto_now=True, verbose_name="Upraveno")

    def __str__(self):
        return self.order_number + " " + self.customer_name

    def __repr__(self):
        return self.order_number + " " + self.customer_name
