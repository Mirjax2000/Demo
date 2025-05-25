"""protokols to pdf"""

from io import BytesIO
from pathlib import Path
from django.conf import settings
from rich.console import Console
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from .models import Order

cons: Console = Console()

FONT_DIR: Path = settings.BASE_DIR / "files"
FONTS: dict[str, Path] = {
    "FiraCode": FONT_DIR / "FiraCode-Regular.ttf",
    "Roboto-Regular": FONT_DIR / "Roboto-Regular.ttf",
    "Roboto-Light": FONT_DIR / "Roboto-Light.ttf",
    "Roboto-Semibold": FONT_DIR / "Roboto-Semibold.ttf",
    "JetBrainsMono": FONT_DIR / "JetBrainsMono.ttf",
}


class PdfGenerator:
    """PDF generator"""

    def __init__(self, model) -> None:
        Utility.font_register()
        self.model = model
        # --- config ---
        self.config: dict[str, int | float] = {
            "font_size_small": 6,
            "font_size_normal": 8,
            "font_size_bigger": 10,
            "font_size_biggest": 12,
            "margin": 5,
            "offset_x": 40,
            "offset_y": 40,
        }
        self.config["width"], self.config["height"] = A4
        # --- atributes ---
        self.buffer = BytesIO()
        self.canvas: Canvas = Canvas(self.buffer, pagesize=A4)
        self.section: Section = Section(self.config, self.canvas)

    def generate_order_sconto(self):
        self.section.header()  # --- header ---
        self.section.body_sconto()  # --- body ---
        self.section.footer()  # --- footer ---
        # ---
        self.canvas.showPage()
        self.canvas.save()
        # ---
        pdf = self.buffer.getvalue()
        self.buffer.close()
        return pdf

    def generate_order_general(self, order):
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        p.setFont("FiraCode", 16)
        p.drawString(50, height - 50, f"Objednávka č. {order.order_number}")

        p.setFont("Roboto-Light", 16)
        p.drawString(50, height - 100, f"Zákazník: {order.client.name}")
        p.drawString(50, height - 120, f"Tým: {order.team.name}")
        p.drawString(
            50, height - 140, f"Vytvořeno: {order.delivery_termin.strftime('%d.%m.%Y')}"
        )

        p.showPage()
        p.save()

        pdf = buffer.getvalue()
        buffer.close()
        return pdf


class Section:
    """Section"""

    def __init__(self, config: dict, canvas: Canvas) -> None:
        self.config = config
        self.canvas = canvas

    def header(self) -> None:
        """header section"""
        self.canvas.setFont("Roboto-Semibold", self.config["font_size_normal"])
        self.canvas.drawString(
            print_margin, height - top_offset, "RHENUS Home Delivery s.r.o."
        )
        # ---
        self.canvas.setFont("Roboto-Regular", self.config["font_size_normal"])
        self.canvas.drawString(
            print_margin, height - top_offset, "Plzeňská 256, 252 19 Chrášťany "
        )
        # ---
        self.canvas.drawString(print_margin, height - top_offset, "IČO: 27629325")
        # ---
        self.canvas.drawString(print_margin, height - top_offset, "DIČ: CZ27629325")
        # ---
        self.canvas.drawString(
            print_margin,
            height - top_offset,
            "Společnost je zapsaná v OR pod spisovou značkou C 120048 vedená u Městského soudu v Praze",
        )

    def footer(self) -> None:
        """Footer section"""
        pass

    def body_sconto(self) -> None:
        """Sconto section"""
        self.canvas.setFont("Roboto-Semibold", self.font_size_bigger)
        self.canvas.drawString(
            print_margin,
            height - top_offset,
            "Předávací protokol provedených prací",
        )
        # ---
        self.canvas.setFont("Roboto-Semibold", self.font_size_normal)
        self.canvas.drawString(
            53,
            height - top_offset,
            "Kontaktní údaje zákazníka",
        )
        p.rect(50, height - top_offset - 3, 200, 20)
        # ---
        p.setFont("Roboto-Regular", self.font_size_normal)
        p.drawString(53, height - top_offset, "Jméno:")
        p.rect(50, height - top_offset - 3, 200, 20)
        # ---
        p.drawString(53, height - top_offset, "Ulice a čp/čo:")
        p.rect(50, height - top_offset - 3, 200, 20)
        # ---
        p.drawString(53, height - top_offset, "PSČ:")
        p.rect(50, height - top_offset - 3, 200, 20)
        # ---
        p.drawString(53, height - top_offset, "Město:")
        p.rect(50, height - top_offset - 3, 200, 20)
        # ---
        p.drawString(53, height - top_offset, "Telefon:")
        p.rect(50, height - top_offset - 3, 200, 20)
        # ---
        p.drawString(53, height - top_offset, "E-mail:")
        p.rect(50, height - top_offset - 3, 200, 20)

    def body_general(self) -> None:
        """general section"""
        pass


class Utility:
    """Utilitky pro PDF generator"""

    @staticmethod
    def font_register() -> None:
        """Registrujeme fonty do pameti pro reportlab"""
        for name, path in FONTS.items():
            pdfmetrics.registerFont(TTFont(name, str(path)))


if __name__ == "__main__":
    ...
