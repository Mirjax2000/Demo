"""protokols to pdf"""

from io import BytesIO
from pathlib import Path
from dataclasses import dataclass
from rich.console import Console
from django.conf import settings
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ---
cons: Console = Console()


# ---
@dataclass
class PdfConfig:
    font_size_small: float = 7.7
    font_size_normal: float = 8
    font_size_bigger: float = 11.5
    x_offset: float = 40
    y_offset: float = 40
    width: float = A4[0]
    height: float = A4[1]
    files: Path = settings.BASE_DIR / "files"


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

    def generate_pdf_sconto(self) -> bytes:
        self.section.header()  # --- header ---
        self.section.sconto()  # --- body sconto ---
        self.section.footer()  # --- footer ---
        # ---
        self.cvs.showPage()
        self.cvs.save()
        # ---
        pdf = self.buffer.getvalue()
        self.buffer.close()
        return pdf

    def generate_pdf_general(self) -> bytes:
        self.section.header()  # --- header ---
        # self.section.general()  # --- body general ---
        self.section.footer()  # --- footer ---
        # ---
        self.cvs.showPage()
        self.cvs.save()
        # ---
        pdf = self.buffer.getvalue()
        self.buffer.close()
        return pdf


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

    def draw_text(
        self,
        text: str,
        y_offset: float,
        x_offset=None,
        font="Roboto-Regular",
        font_size=None,
    ) -> None:
        """Vykresluje text"""
        if font_size is None:
            font_size = self.cfg.font_size_normal
        if x_offset is None:
            x_offset = self.cfg.x_offset
        self.cvs.setFont(font, font_size)
        self.cvs.drawString(x_offset, self.from_top_offset(y_offset), text)

    def header(self) -> None:
        """header section"""
        self.draw_text(
            "RHENUS Home Delivery s.r.o.", y_offset=11, font="Roboto-Semibold"
        )
        self.draw_text(
            "Plzeňská 256, 252 19 Chrášťany", y_offset=15, font="Roboto-Regular"
        )
        self.draw_text("IČO: 27629325", y_offset=11)
        self.draw_text("DIČ: CZ27629325", y_offset=11)
        self.draw_text(
            "Společnost je zapsaná v OR pod spisovou značkou C 120048 vedená u Městského soudu v Praze",
            y_offset=11,
        )
        image_width: float = 180
        image_height: float = 42
        self.cvs.drawImage(
            image=self.cfg.files / "rhenus_logo.png",
            x=self.cfg.width - 180 - self.cfg.x_offset,
            y=self.cfg.height - self.cfg.y_offset - image_height,
            width=image_width,
            height=image_height,
        )

    def footer(self) -> None:
        """Footer section"""
        # --- podpis montera
        text_width: float = 60
        self.cvs.setFont("Roboto-Regular", self.cfg.font_size_normal)
        # ---
        self.cvs.drawString(self.cfg.x_offset + 50, self.cfg.x_offset, "podpis montéra")
        # --- podpis zakaznika
        right_margin: float = self.cfg.width - text_width - 50 - self.cfg.x_offset
        self.cvs.drawString(right_margin, self.cfg.y_offset, "podpis zákazníka")
        # --- lines ---

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
        self.cvs.setFont("Roboto-Regular", self.cfg.font_size_normal)
        self.cvs.drawString(self.cfg.x_offset, self.from_bottom_offset(42), text_2)
        self.cvs.drawString(self.cfg.x_offset, self.from_bottom_offset(11), text_1)

    def sconto(self) -> None:
        """Sconto section"""
        self.draw_text(
            "Předávací protokol provedených prací",
            y_offset=22,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.draw_text(
            "Kontaktní údaje zákazníka",
            y_offset=22,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_normal,
        )
        self.draw_text("Jméno:", y_offset=15)
        self.draw_text("Ulice a čp/čo:", y_offset=15)
        self.draw_text("PSČ:", y_offset=15)
        self.draw_text("Město:", y_offset=15)
        self.draw_text("Telefon:", y_offset=15)
        self.draw_text("E-mail:", y_offset=15)
        # ---
        self.cvs.setStrokeColor(HexColor("#ABABAB"))
        self.cvs.roundRect(
            37, self.from_top_offset(5), 200, 105, radius=4, stroke=1, fill=0
        )
        # ---
        text_1 = "Zákazník prohlašuje, že má-li být zboží připevněno či zavěšeno na stěně, že se ujistil před zahájením prací o povaze a průběhu rozvodů předmětných médií, "
        text_2 = "o nosnosti stěn a případných místních specifikách. Zákazník je povinen informovat Společnost o všech těchto skutečnostech významných pro montáž"
        text_3 = "před zahájením montážních prací."
        self.draw_text(text_1, y_offset=15, font_size=self.cfg.font_size_small)
        self.draw_text(text_2, y_offset=11, font_size=self.cfg.font_size_small)
        self.draw_text(text_3, y_offset=11, font_size=self.cfg.font_size_small)

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
