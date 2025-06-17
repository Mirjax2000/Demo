"""utilitky"""

import cv2
from rich.console import Console

# --- django
from django.db.models import QuerySet
from django.conf import settings
from django.db import transaction


# --- models
from .models import Order

# ---
cons: Console = Console()


def parse_order_filters(request) -> dict:
    """Vrací hodnoty z GET parametrů pro filtrování objednávek."""
    return {
        "status": request.GET.get("status", "").strip(),
        "od": request.GET.get("od", "").strip(),
        "start_date": request.GET.get("start_date"),
        "end_date": request.GET.get("end_date"),
    }


def filter_orders(filters: dict) -> QuerySet:
    """Vrátí queryset objednávek podle GET ale pres filters"""
    orders = Order.objects.exclude(status="Hidden")

    status = filters.get("status", "").strip()
    od_value = filters.get("od", "").strip()
    start_date = filters.get("start_date")
    end_date = filters.get("end_date")

    if status:
        orders = orders.filter(status=status)

    if start_date:
        orders = orders.filter(evidence_termin__gte=start_date)

    if end_date:
        orders = orders.filter(evidence_termin__lte=end_date)

    if od_value:
        orders = orders.filter(order_number__startswith=od_value)

    return orders


def format_date(date_obj):
    return date_obj.strftime("%Y-%m-%d") if date_obj else ""


def update_customers(customer_details: list) -> None:
    """Update modelu Client"""
    for item in customer_details:
        for order_number, data in item.items():
            try:
                order = Order.objects.get(order_number=order_number.lower())
                client = order.client
                if client:
                    cons.log(
                        f"zacatek {client.slug} ma incomplete: {client.incomplete}"
                    )
                    try:
                        with transaction.atomic():
                            client.name = data["name"]
                            client.city = data.get("city", "")
                            client.zip_code = data["zip_code"]
                            client.street = data.get("street", "")
                            client.phone = data.get("phone", "")
                            client.email = data.get("email", "")
                            client.save()
                            if settings.DEBUG:
                                cons.log(f"{client.slug}: byl aktualizovan.")
                                cons.log(
                                    f"konec: {client.slug} ma incomplete: {client.incomplete}"
                                )

                    except Exception:
                        if settings.DEBUG:
                            cons.log(f"{client.slug}: Update selhal, nic se neulozilo.")

                else:
                    if settings.DEBUG:
                        cons.log(f"{client}: nenalezen")

            except Order.DoesNotExist:
                if settings.DEBUG:
                    cons.log(f"Order {order_number} not found")


def get_qrcode_value(image_path):
    try:
        image = cv2.imread(image_path)
        if image is None:
            cons.log(f"Nelze načíst obrázek: {image_path}")
            return None

        # Ořízneme horní pravý roh (např. 50 % výšky, 50 % šířky od pravého okraje)
        height, width = image.shape[:2]
        # cropped = image[0 : int(height * 0.5), int(width * 0.5) : width]

        # Vytvoříme QR code detektor
        detector = cv2.QRCodeDetector()

        # Detekujeme a dekódujeme QR kód
        data, points, _ = detector.detectAndDecode(image)
        if not data:
            cons.log("nebyl nalezen žádný QR kód.", style="red")
            return None
        cons.log(f"QR value: {data}")
        return data

    except Exception as e:
        cons.log(f"Chyba při zpracování obrázku {image_path}: {e}", style="red")
        return None
