"""Emails"""

import os
from pathlib import Path
from dataclasses import dataclass
import dotenv
from rich.console import Console
from pypdf import PdfReader, PdfWriter

# Django imports
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_object_or_404

from .models import Order, OrderPDFStorage

cons: Console = Console()
dotenv.load_dotenv(override=True, verbose=True)


@dataclass(frozen=True)
class Config:
    from_email = os.getenv("EMAIL_HOST_USER")


class CustomEmail:
    """Hlavní emailová třída"""

    def __init__(self, pk, back_url, user) -> None:
        self.order = get_object_or_404(Order, pk=pk)
        self.back_url = back_url
        self.cfg = Config()
        self.user = user

    def email_subject(self) -> str:
        """Předmět emailu"""
        order: Order = self.order
        return f"Montážní protokol: {order.order_number.upper()}"

    def dispecert_email_address(self, user) -> str:
        return user.email

    def email_body(self) -> str:
        """HTML tělo emailu"""
        order: Order = self.order
        html_body = f"""
<body>
    <p style="margin-bottom:10px;margin-top:20px">
        Dobrý den,<br>Zasíláme vám montážní protokol. (viz. příloha)
    </p>
    <p style="margin-bottom:10px">
        Zákazník: <strong>{order.client.name}</strong><br>
        Datum montáže: <strong>{order.format_datetime(order.montage_termin)}</strong>
    </p>
    <p>Po dokončení zakázky odešlete fotokopii montážního protokolu na tento link:</p>
    <br>
    <a href="{self.back_url}"
       style="color:#ffffff; background-color:#1a73e8; padding:10px 20px;
              border-radius:5px; margin-left:45px;
              display:inline-block; text-decoration:none;
              font-size:1.5rem;">
       předat protokol
    </a>
    <br><br>
    <p>V případě dotazů nás kontaktujte.</p>
    <p>dispečer: {self.dispecert_email_address(self.user)}</p>
    <br>
    <br>
    <p>S pozdravem,<br>Tým Rhenus</p>
</body>
"""
        return html_body

    def email_body_plain(self) -> str:
        """HTML tělo emailu"""
        order: Order = self.order
        body_text = (
            "Zasíláme vám montážní protokol. (viz. příloha)\n\n"
            f"Zákazník: {order.client.name}\n"
            f"Datum montáže: {order.format_datetime(order.montage_termin)}\n\n"
            "Po dokončení zakázky odešlete fotokopii montážního protokolu na tento link:\n"
            f"{self.back_url}\n\n"
            "V případě dotazů nás kontaktujte.\n\n"
            "S pozdravem,\n"
            "Tým Rhenus"
        )
        return body_text

    def email_to(self) -> list[str]:
        """Adresáti emailu"""
        order: Order = self.order
        return [order.team.email]

    def get_pdf_paths(self) -> list[str]:
        """Cesty k PDF přílohám"""
        order: Order = self.order
        pdf_file = get_object_or_404(OrderPDFStorage, order=order)
        return [pdf_file.file.path]

    def send_email_with_encrypted_pdf(self) -> None:
        """Odeslání emailu s zašifrovaným PDF jako přílohou"""
        password = self.order.team.email
        email = EmailMultiAlternatives(
            subject=self.email_subject(),
            body=self.email_body_plain(),  # fallback plain text
            from_email=self.cfg.from_email,
            to=self.email_to(),
        )

        # Přidání HTML verze emailu
        email.attach_alternative(self.email_body(), "text/html")

        # Přidání zašifrovaných PDF příloh
        for file_path in self.get_pdf_paths():
            encrypted_path = Utility.encrypt_pdf(file_path, password)
            with open(encrypted_path, "rb") as f:
                email.attach(
                    filename=os.path.basename(encrypted_path),
                    content=f.read(),
                    mimetype="application/pdf",
                )
            os.remove(encrypted_path)

        try:
            email.send()
            cons.log(f"Email byl odeslán na: {self.email_to()}", style="blue")
        except Exception as e:
            cons.log(f"Chyba při odesílání: {e}", style="red")
            raise


class Utility:
    """Pomocné funkce pro odesílání emailů"""

    @staticmethod
    def encrypt_pdf(input_pdf_path: str, password: str) -> str:
        """
        Zašifruje PDF a vrátí cestu k zašifrovanému souboru
        """
        input_path = Path(input_pdf_path)
        reader = PdfReader(input_path)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        writer.encrypt(password)

        encrypted_path = input_path.with_name(
            f"{input_path.stem}_encrypted{input_path.suffix}"
        )

        with open(encrypted_path, "wb") as f:
            writer.write(f)

        return str(encrypted_path)


if __name__ == "__main__":
    ...
