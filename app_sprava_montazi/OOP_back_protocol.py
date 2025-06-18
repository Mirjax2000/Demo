"""oop for recieved protocols"""

import os
from dataclasses import dataclass
from rich.console import Console

# --- django
from django.conf import settings
from django.http import HttpResponse, HttpRequest
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.contrib import messages
from django.shortcuts import redirect

# --- models
from .models import Order, OrderBackProtocol, OrderBackProtocolToken, Status
from .utils import get_qrcode_value, convert_image_to_webp

cons: Console = Console()


@dataclass(frozen=True)
class Config:
    img_formats: tuple[str, ...] = (".jpg", ".jpeg", ".png", ".webp", ".bmp")


class ProtocolUploader:
    """OOP pro vsechno z navratu protokolu od montazniho tymu"""

    def __init__(self, order: Order, image, request: HttpRequest):
        self.order = order
        self.image = image
        self.request = request
        self.conf: Config = Config()
        self.protocol_obj: OrderBackProtocol | None = None
        self.error_message: str | None = None

    def set_error(self, message: str) -> None:
        """nastavi error zpravu"""
        self.error_message = message

    def redirect_with_error(self) -> HttpResponse:
        """Handles error by redirecting with the stored message."""
        if self.error_message:
            messages.error(self.request, self.error_message)
        else:
            messages.error(
                self.request, "Nastala neočekávaná chyba."
            )  # Fallback message
        return redirect(self.request.META.get("HTTP_REFERER", "/"))

    def validate_image(self) -> bool:
        """Validates if an image is provided and has an allowed format."""
        if not self.image:
            self.set_error("Soubor nevybrán")
            return False

        ext = os.path.splitext(self.image.name)[1]
        if ext.lower() not in self.conf.img_formats:
            self.set_error(
                f"Špatný soubor s koncovkou: <strong>{ext}</strong>, nejedná se o obrázek"
            )
            return False
        return True

    def process_and_save_protocol(self) -> bool:
        """Processes the image, renames it, and saves the protocol."""
        new_filename = (
            f"{self.order.order_number.upper()}{os.path.splitext(self.image.name)[1]}"
        )

        renamed_file = ContentFile(self.image.read())
        renamed_file.name = new_filename

        obj, created = OrderBackProtocol.objects.get_or_create(order=self.order)
        self.protocol_obj = obj  # Store for later use

        if not created and obj.file and obj.file.name:
            obj.file.delete(save=False)

        try:
            obj.file.save(new_filename, renamed_file, save=True)
            if created and settings.DEBUG:
                cons.log(
                    f"{str(obj.order).upper()}{os.path.splitext(self.image.name)[1]} uložen",
                    style="blue bold",
                )
            elif settings.DEBUG:
                cons.log(
                    f"soubor byl nahrazen novým: {obj.order}{os.path.splitext(self.image.name)[1]}",
                    style="blue",
                )
            return True
        except Exception as e:
            cons.log(f"Error saving protocol file: {e}", style="red")
            self.set_error("Chyba při ukládání protokolu.")
            return False

    def validate_barcode(self) -> bool:
        """Validates the QR code value against the order number."""
        if not self.protocol_obj or not self.protocol_obj.file:
            self.set_error(
                "Protokolový soubor není k dispozici pro ověření čárového kódu."
            )
            return False

        barcode_value: None | str = get_qrcode_value(
            image_path=self.protocol_obj.file.path
        )
        barcode_number: str = str(barcode_value).strip().upper()
        order_number: str = self.order.order_number.strip().upper()

        if not barcode_value:
            # Delete the file if barcode extraction fails
            if self.protocol_obj.file:
                self.protocol_obj.file.delete(save=False)
            self.set_error(
                "<strong>Chyba:</strong> Špatný <strong>QR code</strong>, zkuste znovu s lepším obrázkem."
            )
            return False

        if barcode_number != order_number:
            # Delete the file if barcode does not match
            if self.protocol_obj.file:
                self.protocol_obj.file.delete(save=False)
            self.set_error(
                f"<strong>Chyba:</strong> Nejedná se o protokol <strong>{order_number}</strong>"
            )
            return False
        return True

    def update_order_status(self) -> None:
        """Prepnuti statusu a zapis do history zaznamy se "system" userem"""
        self.order.status = Status.REALIZED
        user = get_user_model()
        try:
            system_user = user.objects.get(username=settings.SYSTEM_USERNAME)
            self.order._history_user = system_user

        except user.DoesNotExist:
            self.order._history_user = None
        self.order.save()

        if settings.DEBUG:
            cons.log(f"zmenu provedl: {self.order._history_user}")
            cons.log(
                f"Order: {self.order.order_number} byl zmenen na {self.order.status}"
            )

    def delete_token(self) -> None:
        """mazeme tokken"""
        token = OrderBackProtocolToken.objects.filter(order=self.order)
        token.delete()

    def convert_and_save_webp(self) -> None:
        """convertujeme soubor na webp"""
        if not self.protocol_obj or not self.protocol_obj.file:
            cons.log("Chybi soubor konverzi na WEBP.", style="red")
            return

        webp_file = convert_image_to_webp(
            self.protocol_obj.file, self.order.order_number.upper()
        )

        if webp_file:
            self.protocol_obj.file.delete(save=False)
            self.protocol_obj.file.save(webp_file.name, webp_file, save=True)
            if settings.DEBUG:
                cons.log(
                    f"Original image nahrazen WEBP: {webp_file.name}", style="green"
                )
        else:
            if settings.DEBUG:
                cons.log("WEBP konverze selhala", style="red")

    @staticmethod
    def html_success() -> str:
        """Returns the HTML for a success page."""
        return """
                <!DOCTYPE html>
                <html lang="cs">
                <head>
                    <meta charset="UTF-8">
                    <title>Success</title>
                </head>
                <body style="text-align:center; font-family:sans-serif;">
                    <h1 style="font-size:3rem;">Vše proběhlo v pořádku</h1>
                    <h2 style="font-size:2rem;">Děkujeme</h2>
                    <hr>
                </body>
                </html>
                """
