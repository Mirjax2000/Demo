"""protokols to pdf"""

from io import BytesIO
from pathlib import Path
from django.conf import settings
from rich.console import Console
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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

    def __init__(self):
        Utility.font_register()
        self.config: dict = {
            "font_size_small": 6,
            "font_size_normal": 8,
            "font_size_bigger": 10,
            "font_size_biggest": 12,
            "font_margin": 5,
            "print_margin_x": 40,
            "top_offset_y": 40,
        }
        self.config["width"], self.config["height"] = A4

    def generate_order_sconto(self, order):
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        # ---
        p.setFont("Roboto-Semibold", self.font_size_normal)
        p.drawString(print_margin, height - top_offset, "RHENUS Home Delivery s.r.o.")
        top_offset += self.font_size_normal + self.font_margin
        # ---
        p.setFont("Roboto-Regular", self.font_size_normal)
        p.drawString(
            print_margin, height - top_offset, "Plzeňská 256, 252 19 Chrášťany "
        )
        top_offset += self.font_size_normal + self.font_margin
        # ---
        p.drawString(print_margin, height - top_offset, "IČO: 27629325")
        top_offset += self.font_size_normal + self.font_margin
        # ---
        p.drawString(print_margin, height - top_offset, "DIČ: CZ27629325")
        top_offset += self.font_size_normal + self.font_margin
        # ---
        p.drawString(
            print_margin,
            height - top_offset,
            "Společnost je zapsaná v OR pod spisovou značkou C 120048 vedená u Městského soudu v Praze",
        )
        top_offset += self.font_size_normal + (self.font_margin * 2)
        # ---
        p.setFont("Roboto-Semibold", self.font_size_bigger)
        p.drawString(
            print_margin,
            height - top_offset,
            "Předávací protokol provedených prací",
        )
        top_offset += self.font_size_bigger + (self.font_margin * 3)
        # ---
        p.setFont("Roboto-Semibold", self.font_size_normal)
        p.drawString(
            53,
            height - top_offset,
            "Kontaktní údaje zákazníka",
        )
        p.rect(50, height - top_offset - 3, 200, 20)
        top_offset += self.font_size_normal + self.font_margin + 7
        # ---
        p.setFont("Roboto-Regular", self.font_size_normal)
        p.drawString(53, height - top_offset, "Jméno:")
        p.rect(50, height - top_offset - 3, 200, 20)
        top_offset += self.font_size_normal + self.font_margin + 7
        # ---
        p.drawString(53, height - top_offset, "Ulice a čp/čo:")
        p.rect(50, height - top_offset - 3, 200, 20)
        top_offset += self.font_size_normal + self.font_margin + 7
        # ---
        p.drawString(53, height - top_offset, "PSČ:")
        p.rect(50, height - top_offset - 3, 200, 20)
        top_offset += self.font_size_normal + self.font_margin + 7
        # ---
        p.drawString(53, height - top_offset, "Město:")
        p.rect(50, height - top_offset - 3, 200, 20)
        top_offset += self.font_size_normal + self.font_margin + 7
        # ---
        p.drawString(53, height - top_offset, "Telefon:")
        p.rect(50, height - top_offset - 3, 200, 20)
        top_offset += self.font_size_normal + self.font_margin + 7
        # ---
        p.drawString(53, height - top_offset, "E-mail:")
        p.rect(50, height - top_offset - 3, 200, 20)
        top_offset += self.font_size_normal + self.font_margin + 7

        p.showPage()
        p.save()

        pdf = buffer.getvalue()
        buffer.close()
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


class Utility:
    """Utilitky pro PDF generator"""

    @staticmethod
    def font_register():
        for name, path in FONTS.items():
            pdfmetrics.registerFont(TTFont(name, str(path)))


if __name__ == "__main__":
    ...
