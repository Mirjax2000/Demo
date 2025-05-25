"""protokols to pdf"""

from io import BytesIO
from pathlib import Path
from django.conf import settings
from dataclasses import dataclass
from rich.console import Console
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

cons: Console = Console()


@dataclass
class PdfConfig:
    font_size_small: float = 7.7
    font_size_normal: float = 8
    font_size_bigger: float = 10
    font_size_biggest: float = 12
    x_offset: float = 40
    y_offset: float = 40
    width: float = A4[0]
    height: float = A4[1]


class PdfGenerator:
    """PDF generator"""

    def __init__(self, model) -> None:
        Utility.font_register()
        # --- config ---
        self.cfg: PdfConfig = PdfConfig()
        # --- atributes ---
        self.model = model
        self.buffer = BytesIO()
        self.cvs: Canvas = Canvas(self.buffer, pagesize=A4)
        self.section: Section = Section(self)

    def generate_pdf_sconto(self):
        self.section.header()  # --- header ---
        # self.section.sconto()  # --- body sconto ---
        self.section.footer()  # --- footer ---
        # ---
        self.cvs.showPage()
        self.cvs.save()
        # ---
        pdf = self.buffer.getvalue()
        self.buffer.close()
        return pdf

    def generate_pdf_general(self, order): ...


class Section:
    """Sections"""

    def __init__(self, parent: PdfGenerator) -> None:
        self.parent: PdfGenerator = parent
        self.cfg: PdfConfig = self.parent.cfg
        self.cvs: Canvas = self.parent.cvs
        self.model = self.parent.model
        self.top_offset: float = 0
        self.bottom_offset: float = 0

    def from_top_offset(self, margin: float = 0) -> float:
        """odpocitavani od shora pro osu Y"""
        self.top_offset += margin
        height: float = self.cfg.height
        y_offset: float = self.cfg.y_offset
        return height - y_offset - self.top_offset

    def from_bottom_offset(self, margin: int = 0) -> float:
        """odpocitavani od spoda pro osu Y"""
        self.bottom_offset += margin
        y_offset: float = self.cfg.y_offset
        return y_offset + self.bottom_offset

    def header(self) -> None:
        """header section"""
        self.cvs.setFont("Roboto-Semibold", self.cfg.font_size_normal)
        self.cvs.drawString(
            self.cfg.y_offset,
            self.from_top_offset(0),
            "RHENUS Home Delivery s.r.o.",
        )
        # ---
        self.cvs.setFont("Roboto-Regular", self.cfg.font_size_normal)
        self.cvs.drawString(
            self.cfg.x_offset,
            self.from_top_offset(15),
            "Plzeňská 256, 252 19 Chrášťany ",
        )
        # ---
        self.cvs.drawString(
            self.cfg.x_offset,
            self.from_top_offset(11),
            "IČO: 27629325",
        )
        # ---
        self.cvs.drawString(
            self.cfg.x_offset,
            self.from_top_offset(11),
            "DIČ: CZ27629325",
        )
        # ---
        self.cvs.drawString(
            self.cfg.x_offset,
            self.from_top_offset(11),
            "Společnost je zapsaná v OR pod spisovou značkou C 120048 vedená u Městského soudu v Praze",
        )

    def footer(self) -> None:
        """Footer section"""
        # --- podpis montera
        text_width: float = 60
        # ---
        self.cvs.drawString(self.cfg.x_offset + 50, self.cfg.x_offset, "podpis montéra")
        # --- podpis zakaznika
        right_margin: float = self.cfg.width - text_width - 50 - self.cfg.x_offset
        self.cvs.drawString(right_margin, self.cfg.y_offset, "podpis zákazníka")
        # --- lines ---

        cons.log(self.bottom_offset)
        self.cvs.setLineWidth(1)
        self.cvs.setDash(1, 2)
        self.cvs.line(
            self.cfg.x_offset,
            self.from_bottom_offset(11),
            self.cfg.x_offset + text_width + 100,
            self.from_bottom_offset(0),
        )
        self.cvs.setLineWidth(1)
        self.cvs.setDash(1, 2)
        self.cvs.line(
            right_margin - 50,
            self.from_bottom_offset(0),
            self.cfg.width - self.cfg.x_offset,
            self.from_bottom_offset(0),
        )
        # --- ujednani
        text_1 = "Zákazník svým podpisem na konci strany tohoto protokolu potvrzujete správnost všech uvedených údajů a akceptujete všeobecné obchodní podmínky."
        text_2 = "Ústní vedlejší ujednání nejsou platná."
        self.cvs.setFont("Roboto-Regular", self.cfg.font_size_small)
        self.cvs.drawString(self.cfg.x_offset, self.from_bottom_offset(42), text_2)
        self.cvs.drawString(self.cfg.x_offset, self.from_bottom_offset(11), text_1)

    def sconto(self) -> None:
        """Sconto section"""
        self.cvs.setFont("Roboto-Semibold", self.cfg.font_size_bigger)
        self.cvs.drawString(
            self.cfg.x_offset,
            self.cfg.height - self.cfg.x_offset,
            "Předávací protokol provedených prací",
        )
        # ---
        self.cvs.setFont("Roboto-Semibold", self.cfg.font_size_normal)
        self.cvs.drawString(
            53,
            self.cfg.height - self.cfg.x_offset,
            "Kontaktní údaje zákazníka",
        )
        self.cvs.rect(50, self.cfg.height - self.cfg.x_offset - 3, 200, 20)
        # ---
        self.cvs.setFont("Roboto-Regular", self.cfg.font_size_normal)
        self.cvs.drawString(53, self.cfg.height - self.cfg.x_offset, "Jméno:")
        self.cvs.rect(50, self.cfg.height - self.cfg.x_offset - 3, 200, 20)
        # ---
        self.cvs.drawString(53, self.cfg.height - self.cfg.x_offset, "Ulice a čp/čo:")
        self.cvs.rect(50, self.cfg.height - self.cfg.x_offset - 3, 200, 20)
        # ---
        self.cvs.drawString(53, self.cfg.height - self.cfg.x_offset, "PSČ:")
        self.cvs.rect(50, self.cfg.height - self.cfg.x_offset - 3, 200, 20)
        # ---
        self.cvs.drawString(53, self.cfg.height - self.cfg.x_offset, "Město:")
        self.cvs.rect(50, self.cfg.height - self.cfg.x_offset - 3, 200, 20)
        # ---
        self.cvs.drawString(53, self.cfg.height - self.cfg.x_offset, "Telefon:")
        self.cvs.rect(50, self.cfg.height - self.cfg.x_offset - 3, 200, 20)
        # ---
        self.cvs.drawString(53, self.cfg.height - self.cfg.x_offset, "E-mail:")
        self.cvs.rect(50, self.cfg.height - self.cfg.x_offset - 3, 200, 20)

    def general(self) -> None:
        """general pdf section"""
        pass


class Utility:
    """Utilitky pro PDF generator"""

    FONT_DIR: Path = settings.BASE_DIR / "files"
    FONTS: dict[str, Path] = {
        "FiraCode": FONT_DIR / "FiraCode-Regular.ttf",
        "Roboto-Regular": FONT_DIR / "Roboto-Regular.ttf",
        "Roboto-Light": FONT_DIR / "Roboto-Light.ttf",
        "Roboto-Semibold": FONT_DIR / "Roboto-Semibold.ttf",
        "JetBrainsMono": FONT_DIR / "JetBrainsMono.ttf",
    }

    @staticmethod
    def font_register() -> None:
        """Registrujeme fonty do pameti pro reportlab"""
        for name, path in Utility.FONTS.items():
            pdfmetrics.registerFont(TTFont(name, str(path)))


if __name__ == "__main__":
    ...
