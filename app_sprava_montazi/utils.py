"""utilitky"""

from io import BytesIO
from PIL.ImageFile import ImageFile
from PIL import Image, ImageOps
import cv2
from rich.console import Console

# --- django
from django.db.models import Q, F
from django.conf import settings
from django.db import transaction
from django.db.models import QuerySet
from django.core.files.base import ContentFile

# --- models
from .models import Order, Status, OrderPDFStorage, Client, TeamType

# ---
cons: Console = Console()

# region: nepouzivane funkce - just in case
# def parse_order_filters(request) -> dict:
#     """Vrací hodnoty z GET parametrů pro filtrování objednávek."""
#     return {
#         "status": request.GET.get("status", "").strip(),
#         "od": request.GET.get("od", "").strip(),
#         "start_date": request.GET.get("start_date"),
#         "end_date": request.GET.get("end_date"),
#     }

#
# def filter_orders(filters: dict) -> QuerySet:
#     """Vrátí queryset objednávek podle GET ale pres filters"""

#     status = filters.get("status", "").strip()
#     od_value = filters.get("od", "").strip()
#     start_date = filters.get("start_date")
#     end_date = filters.get("end_date")
#     # --- dotaz na vsechno a postupne se pridavaji dalsi filtry
#     orders = Order.objects.all()
#     # --- status filtr
#     # --- vsechny krome hidden
#     if status == "all":
#         orders = orders.exclude(status="Hidden")
#     elif status == "closed":
#         # --- Uzavrene
#         orders = orders.filter(status__in=["Billed", "Canceled"])
#     elif status:
#         # --- jednotlive
#         orders = orders.filter(status=status)
#     else:
#         # --- Otevrene - default filtr
#         orders = orders.exclude(status__in=["Hidden", "Billed", "Canceled"])
#     # --- casovy filtr
#     if start_date:
#         orders = orders.filter(evidence_termin__gte=start_date)

#     if end_date:
#         orders = orders.filter(evidence_termin__lte=end_date)
#     # --- obchodni dum filtr
#     if od_value:
#         orders = orders.filter(order_number__startswith=od_value)

#     return orders
# endregion


def format_date(date_obj):
    return date_obj.strftime("%Y-%m-%d") if date_obj else ""


def client_cons_log_porovnani(client) -> None:
    if settings.DEBUG:
        cons.log(
            f"zacatek {client.name}-{client.zip_code}ma incomplete: {client.incomplete}"
        )


def client_cons_log_aktualizovan(client) -> None:
    if settings.DEBUG:
        cons.log(f"{client.name}-{client.zip_code}:byl aktualizovan.")


def client_cons_log_update_selhal(client) -> None:
    if settings.DEBUG:
        cons.log(f"{client.name}-{client.zip_code}:Update selhal, nic se neulozilo.")


def client_cons_log_client_nenalezen(client) -> None:
    if settings.DEBUG:
        cons.log(f"Client model:{client}: nenalezen")


def client_cons_log_zakazka_nenalezena(order_number) -> None:
    if settings.DEBUG:
        cons.log(f"Zakazka: {order_number} nenalezena.")


def client_created(name: str, zip_code: str, data) -> tuple[Client, bool]:
    with transaction.atomic():
        client, created = Client.objects.get_or_create(
            name=name,
            zip_code=zip_code,
            defaults={
                "street": data.get("street", ""),
                "city": data.get("city", ""),
                "phone": data.get("phone", ""),
                "email": data.get("email", ""),
            },
        )
        # Pokud už existuje, ale má staré/neúplné údaje → aktualizuj
        if not created:
            updated = False
            for field in ["street", "city", "phone", "email"]:
                value = data.get(field, "")
                if value and getattr(client, field) != value:
                    setattr(client, field, value)
                    updated = True
            if updated:
                client.save()

    return client, created


def update_customers(customer_details: list) -> None:
    """Update modelu Client"""
    for item in customer_details:
        for order_number, data in item.items():
            try:
                order: Order = Order.objects.get(order_number=order_number)
                client: Client | None = order.client
                if client:
                    client_cons_log_porovnani(client)
                    try:
                        with transaction.atomic():
                            # client.name = data["name"].strip()
                            client.city = data.get("city", "").strip()
                            # client.zip_code = data["zip_code"].strip()
                            client.street = data.get("street", "").strip()
                            client.phone = data.get("phone", "").strip()
                            client.email = data.get("email", "").strip()
                            client.save()
                            client_cons_log_aktualizovan(client)
                            client_cons_log_porovnani(client)

                    except Exception:
                        client_cons_log_update_selhal(client)

                else:
                    client_cons_log_client_nenalezen(client)

            except Order.DoesNotExist:
                client_cons_log_zakazka_nenalezena(order_number)


def get_qrcode_value(image_path) -> None | str:
    """Get QR code value and return it"""
    try:
        image = cv2.imread(image_path)
        if image is None:
            cons.log(f"Nelze načíst obrázek: {image_path}")
            return None

        height, width = image.shape[:2]
        cropped = image[0 : int(height * 0.5), int(width * 0.5) : width]
        gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)

        detector = cv2.QRCodeDetector()

        data, _, _ = detector.detectAndDecode(gray)
        # ---
        if not data:
            if settings.DEBUG:
                cons.log("nebyl nalezen žádný QR kód.", style="red")
            return None
        if settings.DEBUG:
            cons.log(f"QR value: {data}")
        return data

    except Exception as e:
        if settings.DEBUG:
            cons.log(f"Chyba při zpracování obrázku {image_path}: {e}", style="red")
        return None


def resize_image_max_width(img: Image.Image, max_width: int = 1024) -> Image.Image:
    """
    Pokud je šířka obrázku větší než max_width,
    zmenší obrázek na max_width a upraví výšku proporčně.
    Jinak vrátí původní obrázek.
    """
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        if settings.DEBUG:
            cons.log(
                f"Resizing image from {img.width}x{img.height} to {max_width}x{new_height}",
                style="green",
            )
        result = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        return result

    return img


def convert_image_to_webp(img_file, new_name: str, quality=90) -> None | ContentFile:
    """Convert image to WEBP format with EXIF orientation fix and max width 1024px"""

    try:
        input_size = img_file.size
        cons.log(f"Input image size: {input_size / 1024:.2f} KB")
        img: Image.Image = Image.open(img_file)

        # Oprava rotace podle EXIF dat (mobilní fotky apod.)
        img = ImageOps.exif_transpose(img)

    except FileNotFoundError:
        if settings.DEBUG:
            cons.log("Error: Image file not found")
        return None

    except Exception as e:
        if settings.DEBUG:
            cons.log(f"Error opening image: {e}")
        return None

    img = resize_image_max_width(img, max_width=1024)

    # Převod do RGB, pokud je potřeba (WEBP nemusí podporovat všechny módy)
    if img.mode in ("RGBA", "P"):
        image = img.convert("RGB")
    else:
        image = img

    buffer = BytesIO()

    try:
        # Uložíme do bufferu jako WEBP s nastavenou kvalitou
        image.save(buffer, format="WEBP", quality=quality)
    except Exception as e:
        if settings.DEBUG:
            cons.log(f"Error saving image as WEBP: {e}")
        return None

    buffer.seek(0)
    output_size = len(buffer.getvalue())
    cons.log(f"Output WEBP size: {output_size / 1024:.2f} KB")

    # Vytvoříme ContentFile pro Django s novým názvem souboru
    webp_file = ContentFile(buffer.read())
    webp_file.name = f"{new_name}.webp"

    return webp_file


def call_errors_adviced() -> tuple[bool, int]:
    """pocita chyby do navbaru u zakazky"""
    is_errors: bool = False
    all_count: int = 0

    # --- Základní queryset pro všechny ADVICED objednávky
    base_query = Order.objects.filter(
        status=Status.ADVICED, team_type=TeamType.BY_ASSEMBLY_CREW
    )

    # --- 1. Problém: E-mail nebyl odeslán
    cond_mail_not_sent = Q(mail_datum_sended__isnull=True)

    # --- 2. Problém: E-mail odeslán, ale jméno týmu nesouhlasí
    cond_team_soulad = Q(
        mail_datum_sended__isnull=False, team__name__isnull=False
    ) & ~Q(team__name=F("mail_team_sended"))

    # --- 3. Problém: Tým je neaktivní
    cond_team_inactive = Q(team__active=False)

    # --- Spojení všech tří podmínek přes OR
    full_condition = cond_mail_not_sent | cond_team_soulad | cond_team_inactive

    # --- Filtrování objednávek podle chybných stavů
    error_orders = base_query.filter(full_condition)

    count = error_orders.count()
    if count > 0:
        is_errors = True

    all_count += count

    return is_errors, all_count


def check_order_error_adviced(order_id: int) -> bool:
    """konkretni order kontrola stavu"""
    # --- Vybereme pouze objednávku se statusem ADVICED a BY_ASSEMBLY_CREW a daným ID
    base_query = Order.objects.filter(
        pk=order_id, status=Status.ADVICED, team_type=TeamType.BY_ASSEMBLY_CREW
    )

    # --- První problém: nebyl odeslán e-mail (mail_datum_sended je None)
    cond_mail_not_sent = Q(mail_datum_sended__isnull=True)

    # --- Druhý problém: e-mail byl odeslán, ale jméno týmu se liší
    cond_team_soulad = Q(
        mail_datum_sended__isnull=False,
        team__name__isnull=False,  # jistota, že name existuje
    ) & ~Q(team__name=F("mail_team_sended"))

    # --- Třetí problém: tým není aktivní
    cond_team_inactive = Q(team__active=False)

    # --- Kombinace všech tří problémů pomocí OR
    full_condition = cond_mail_not_sent | cond_team_soulad | cond_team_inactive

    # --- Aplikujeme podmínky na základní query
    error_exists: bool = base_query.filter(full_condition).exists()

    return error_exists


def check_order_adviced_email_sended_to_right_team(order_id: int) -> bool:
    """konkretni order kontrola stavu"""
    # --- Vybereme pouze objednávku se statusem ADVICED a daným ID
    base_query = Order.objects.filter(
        pk=order_id, status=Status.ADVICED, team_type=TeamType.BY_ASSEMBLY_CREW
    )

    # --- prvni problém: e-mail byl odeslán, ale jméno týmu se liší
    cond_team_soulad = Q(
        mail_datum_sended__isnull=False,
        team__name__isnull=False,  # jistota, že name existuje
    ) & ~Q(team__name=F("mail_team_sended"))

    # --- Druhy problém: tým není aktivní
    cond_team_inactive = Q(team__active=False)

    # --- Kombinace všech dvou problémů pomocí OR
    full_condition = cond_team_soulad | cond_team_inactive

    # --- Aplikujeme podmínky na základní query
    error_exists: bool = base_query.filter(full_condition).exists()

    return error_exists


def is_team_names_different(order_id: int) -> bool:
    """
    Vrací True, pokud má zakázka se statusem 'ADVICED' a daným ID odeslaný e-mail
    a zároveň se název aktuálního týmu liší od názvu týmu, kterému byl e-mail odeslán.

    Používá se ke kontrole, zda nedošlo ke změně týmu po odeslání e-mailu.

    Args:
        order_id (int): ID zakázky.

    Returns:
        bool: True pokud názvy týmů nesedí, jinak False.
    """
    base_query = Order.objects.filter(
        pk=order_id, status=Status.ADVICED, team_type=TeamType.BY_ASSEMBLY_CREW
    )
    is_different = (
        base_query.filter(
            mail_datum_sended__isnull=False,
            team__name__isnull=False,
        )
        .exclude(team__name=F("mail_team_sended"))
        .exists()
    )
    return is_different


def team_soulad(order):
    """
    Vrací True, pokud název týmu na PDF (uložený v OrderPDFStorage) souhlasí s aktuálním názvem týmu v zakázce.

    Používá se ke kontrole, zda nebyl změněn tým po vygenerování PDF.

    Args:
        order (Order): Instance zakázky.

    Returns:
        bool: True pokud názvy týmů souhlasí, jinak False.
    """
    soulad: bool = False
    try:
        pdfko_tym = OrderPDFStorage.objects.get(order=order.pk)
        soulad = pdfko_tym.team == order.team.name if order.team else False
    except OrderPDFStorage.DoesNotExist:
        if settings.DEBUG:
            cons.log("Záznam v OrderPDFStorage zatím neexistuje.")

    return soulad
