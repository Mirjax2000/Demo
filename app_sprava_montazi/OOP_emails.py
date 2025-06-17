"""Emails"""

import os
from pathlib import Path
from dataclasses import dataclass
import dotenv
from rich.console import Console
from pypdf import PdfReader, PdfWriter

# ---
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404

# ---
from .models import Order, OrderPDFStorage, Team

# ---
cons: Console = Console()
dotenv.load_dotenv(override=True, verbose=True)


@dataclass(frozen=True)
class Config:
    from_email = os.getenv("EMAIL_HOST_USER")


class CustomEmail:
    """hlavni emailova classa"""

    def __init__(self, pk, back_url) -> None:
        self.order = get_object_or_404(Order, pk=pk)
        self.back_url = back_url
        self.cfg = Config()

    # ---

    def email_subject(self) -> str:
        """Email subject"""
        order: Order = self.order
        subject: str = f"Montazni protokol: {order.order_number.upper()}"
        return subject

    def email_body(self) -> str:
        """Email body"""
        order: Order = self.order
        body: str = (
            f"Zasíláme vám montážní protokol.(viz. příloha)\n\n"
            f"Zákazník: {order.client.name}\n"
            f"Datum montáže: {order.format_datetime(order.montage_termin)}\n\n"
            "Po dokončení zakázky odešlete fotokopii montažního protokolu na tento link"
            f"\n{self.back_url}\n\n"
            f"V případě dotazů nás kontaktujte.\n\n"
            f"S pozdravem,\n"
            f"Tým Rhenus"
        )
        return body

    def email_to(self) -> list[str]:
        """Email to"""
        order: Order = self.order
        adresat: list[str] = [order.team.email]
        return adresat

    def get_pdf_paths(self) -> list:
        """pdf as a attachment"""
        order: Order = self.order
        pdf_file = get_object_or_404(OrderPDFStorage, order=order)
        pdf_file_path: list = [pdf_file.file.path]
        return pdf_file_path

    def send_email_with_encrypted_pdf(self) -> None:
        """
        Posle zasifrovany pdfko
        """
        cfg, order = self.cfg, self.order
        password: str = order.team.email
        email = EmailMessage(
            subject=self.email_subject(),
            body=self.email_body(),
            from_email=cfg.from_email,
            to=self.email_to(),
        )

        for file_path in self.get_pdf_paths():
            encrypted_file_path = Utility.encrypt_pdf(file_path, password)

            with open(encrypted_file_path, "rb") as f:
                email.attach(
                    filename=os.path.basename(encrypted_file_path),
                    content=f.read(),
                    mimetype="application/pdf",
                )
            os.remove(encrypted_file_path)

        try:
            email.send()
            cons.log(f"Email byl odeslan na: {self.email_to()}", style="blue")
        except Exception as e:
            cons.log(f"Chyba při odesílání: {str(e)}", style="red")
            raise


class Utility:
    """Pomocne funkce pro odesilani emailu"""

    @staticmethod
    def encrypt_pdf(input_pdf_path: str, password: str) -> str:
        """
        Encryptuje PDFko a vrátí cestu k zašifrovanému souboru
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
