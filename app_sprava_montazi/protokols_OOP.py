"""protokols to pdf"""

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from django.utils.timezone import localtime
from django.conf import settings
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.barcode import code128
from reportlab.pdfgen.canvas import Canvas
from rich.console import Console

# ---
cons: Console = Console()


# ---
@dataclass(frozen=True)
class PdfConfig:
    font_size_small: float = 7.6
    font_size_normal: float = 8
    font_size_bigger: float = 12
    x_offset: float = 40
    y_offset: float = 40
    width: float = A4[0]
    height: float = A4[1]
    files: Path = settings.BASE_DIR / "files"
    border_clr: Color = HexColor("#ABABAB")
    fill_clr: Color = HexColor("#E8E8E8")


@dataclass(frozen=True)
class CompanyInfo:
    name: str = "RHENUS Home Delivery s.r.o."
    address: str = "Plzeňská 256, 252 19 Chrášťany"
    ico: str = "IČO: 27629325"
    dic: str = "DIČ: CZ27629325"
    ref: str = "Zapsaná v OR: C 120048, Městský soud v Praze."


class PdfGenerator:
    """PDF generator"""

    def __init__(self, model, data_layer: bool = True) -> None:
        # --- config ---
        self.cfg: PdfConfig = PdfConfig()
        # --- atributes ---
        self.model = model
        self.data_layer = data_layer
        # --- pro reportlab
        Utility.font_register()
        self.buffer = BytesIO()
        self.cvs: Canvas = Canvas(self.buffer, pagesize=A4)
        # --- subclassy
        self.utils: Utility = Utility(self.cfg, self.cvs)
        self.section: Section = Section(self)

    def generate_pdf_sconto(self) -> bytes:
        self.utils.vodoznak(CompanyInfo.name)  # --- vodoznak ---
        self.section.header()  # --- header ---
        self.section.sconto()  # --- body sconto ---
        self.section.footer()  # --- footer ---
        # ---
        if self.data_layer:
            self.utils.generate_barcode(self.model.order_number.upper(), 365, 685)
            self.section.sconto_data(self.model)  # --- data layer ---
        # ---
        self.cvs.showPage()
        self.cvs.save()
        # ---
        pdf = self.buffer.getvalue()
        self.buffer.close()
        cons.log(f"pdf: {self.model.order_number} sestaven")
        return pdf

    def generate_pdf_general(self) -> bytes:
        self.section.header()  # --- header ---
        self.section.general()  # --- body general ---
        self.section.footer()  # --- footer ---
        self.utils.vodoznak(CompanyInfo.name)  # --- vodoznak ---
        # ---
        self.cvs.showPage()
        self.cvs.save()
        # ---
        pdf = self.buffer.getvalue()
        self.buffer.close()
        cons.log(f"pdf: {self.model.order_number} sestaven")
        return pdf


class Section:
    """Sections"""

    class SubSection:
        """Subsections"""

        def __init__(self, parent: "Section") -> None:
            # --- atributes
            self.parent = parent
            # --- config
            self.cfg = parent.cfg
            # --- reportlab
            self.cvs = parent.cvs
            # --- Subclassy
            self.utils = self.parent.utils

        def customer_info(self) -> None:
            self.utils.draw_text(
                "Kontaktní údaje zákazníka", y_offset=105, font="Roboto-Semibold"
            )
            self.utils.draw_text("Jméno:", y_offset=120)
            self.utils.draw_text("Ulice:", y_offset=134)
            self.utils.draw_text("PSČ:", y_offset=148)
            self.utils.draw_text("Město:", y_offset=162)
            self.utils.draw_text("Telefon:", y_offset=176)
            self.utils.draw_text("E-mail:", y_offset=190)
            # --- border
            self.cvs.setDash([])
            self.cvs.roundRect(37, 604, 183, 90, radius=4, stroke=1, fill=0)

        def team_info(self) -> None:
            self.utils.draw_text(
                "Informace o zakázce",
                x_offset=378,
                y_offset=147,
                font="Roboto-Semibold",
            )
            self.utils.draw_text("Číslo zakázky:", x_offset=378, y_offset=162)
            self.utils.draw_text("Datum / čas:", x_offset=378, y_offset=175)
            self.utils.draw_text("Montažní tým:", x_offset=378, y_offset=190)
            # --- border
            self.cvs.roundRect(375, 604, 183, 48, radius=4, stroke=1, fill=0)

        def polozky_k_montazi(self) -> None:
            self.utils.draw_text(
                "Položky k montáži uhrazené dle kupní smlouvy na OD Sconto:",
                y_offset=310,
            )
            # --- border
            self.cvs.setDash([])
            self.cvs.roundRect(37, 389, 521, 100, radius=4, stroke=1, fill=0)

        def polozky_materialu(self) -> None:
            self.utils.draw_text(
                "Použitý nadstandardní spotřební materiál:", y_offset=430
            )
            # --- border
            self.cvs.setDash([])
            self.cvs.roundRect(37, 299, 521, 70, radius=4, stroke=1, fill=0)

        def predavaci_protokol(self) -> None:
            """Predavaci protokol subsection"""
            self.utils.draw_text(f"Čas začátku montáže: {'.' * 30}", y_offset=530)
            self.utils.draw_text(
                f"Čas dokončení montáže: {'.' * 30}", x_offset=200, y_offset=530
            )
            self.utils.draw_text(
                "Montáž byla provedena v určeném rozsahu, dle montážního návodu a nejsou třeba další zásahy montážního týmu",
                y_offset=550,
            )
            self.utils.draw_checkbox("ano", 500, 249, 485, 550)
            self.utils.draw_checkbox("ne", 545, 249, 534, 550)
            # ---
            self.utils.draw_text(
                "Montáž nebyla provedena v určeném rozsahu", y_offset=570
            )
            self.utils.draw_checkbox("ano", 500, 228, 485, 570)
            self.utils.draw_checkbox("ne", 545, 228, 534, 570)
            # ---
            self.utils.draw_text("Montáž s vrtáním a kotvením do zdi", y_offset=590)
            self.utils.draw_checkbox("ano", 500, 208, 485, 590)
            self.utils.draw_checkbox("ne", 545, 208, 534, 590)
            # ---
            self.utils.draw_text("Reklamace nebo poznámka k montáži:", y_offset=610)
            # --- border
            self.cvs.setDash([])
            self.cvs.roundRect(37, 119, 521, 70, radius=4, stroke=1, fill=0)

        # ---

    def __init__(self, parent: PdfGenerator) -> None:
        # --- atributy
        self.parent: PdfGenerator = parent
        self.model = self.parent.model
        # --- config
        self.cfg: PdfConfig = self.parent.cfg
        # --- reportlab
        self.cvs: Canvas = self.parent.cvs
        self.cvs.setStrokeColor(self.cfg.border_clr)
        # --- Subclassy
        self.utils: Utility = parent.utils
        self.company: CompanyInfo = CompanyInfo()
        self.subsection: Section.SubSection = self.SubSection(self)

    def header(self) -> None:
        """header section - mezery jsou zde po 11 pixelech"""
        self.utils.draw_text(self.company.name, y_offset=11, font="Roboto-Semibold")
        self.utils.draw_text(self.company.address, y_offset=27, font="Roboto-Regular")
        self.utils.draw_text(self.company.ico, y_offset=38)
        self.utils.draw_text(self.company.dic, y_offset=49)
        self.utils.draw_text(self.company.ref, y_offset=60)
        self.utils.place_image(
            "rhenus_logo.png", img_width=180, img_height=42, x=375, y=760
        )

    def footer(self) -> None:
        """Footer section"""
        l_margin: float = self.cfg.x_offset
        small_font = self.cfg.font_size_small

        text_1 = (
            "Zákazník svým podpisem na konci strany tohoto protokolu potvrzujete "
            "správnost všech uvedených údajů a akceptujete všeobecné obchodní podmínky."
        )
        text_2 = "Ústní vedlejší ujednání nejsou platná."

        # --- podpis montera
        self.utils.draw_text("podpis montéra", 120, 762)
        self.utils.draw_dotted_line(x1=70, y1=51, x2=230, y2=51)
        # --- podpis zakaznika
        self.utils.draw_text("podpis zákazníka", 415, 762)
        self.utils.draw_dotted_line(x1=365, y1=51, x2=525, y2=51)
        # --- ujednani
        self.utils.draw_text(
            text_1, l_margin, 700, font="Roboto-Light", font_size=small_font
        )
        self.utils.draw_text(
            text_2, l_margin, 710, font="Roboto-Light", font_size=small_font
        )

    def sconto(self) -> None:
        """Sconto section"""
        bigger_font = self.cfg.font_size_bigger
        small_font = self.cfg.font_size_small
        self.utils.draw_text(
            "Předávací protokol provedených prací",
            y_offset=84,
            font="Roboto-Semibold",
            font_size=bigger_font,
        )
        # ---
        self.subsection.customer_info()
        self.subsection.team_info()
        # ---
        text_1 = "Zákazník prohlašuje, že má-li být zboží připevněno či zavěšeno na stěně, že se ujistil před zahájením prací o povaze a průběhu rozvodů předmětných médií, "
        text_2 = "o nosnosti stěn a případných místních specifikách. Zákazník je povinen informovat Společnost o všech těchto skutečnostech významných pro montáž"
        text_3 = "před zahájením montážních prací."
        self.utils.draw_text(
            text_1, y_offset=220, font="Roboto-Light", font_size=small_font
        )
        self.utils.draw_text(
            text_2, font="Roboto-Light", y_offset=231, font_size=small_font
        )
        self.utils.draw_text(
            text_3, font="Roboto-Light", y_offset=242, font_size=small_font
        )
        # --- podpis zakaznika
        self.utils.draw_text("podpis zákazníka", x_offset=415, y_offset=281)
        self.utils.draw_dotted_line(x1=365, y1=530, x2=525, y2=530)
        # ---
        self.utils.draw_text(
            "MONTÁŽ NÁBYTKU",
            y_offset=285,
            font="Roboto-Semibold",
            font_size=bigger_font,
        )
        # ---
        self.subsection.polozky_k_montazi()
        self.subsection.polozky_materialu()
        self.subsection.predavaci_protokol()

    def sconto_data(self, order) -> None:
        """Sconto pdf section with Order data"""
        x1: float = 75
        x2: float = 435

        self.utils.draw_text(
            order.client.name,
            x_offset=x1,
            y_offset=120,
            font="Roboto-Semibold",
        )
        self.utils.draw_text(order.client.street, x_offset=x1, y_offset=134)
        self.utils.draw_text(order.client.format_psc(), x_offset=x1, y_offset=148)
        self.utils.draw_text(order.client.city, x_offset=x1, y_offset=162)
        self.utils.draw_text(order.client.format_phone(), x_offset=x1, y_offset=176)
        self.utils.draw_text(order.client.email, x_offset=x1, y_offset=190)
        # ---
        self.utils.draw_text(order.order_number.upper(), x_offset=x2, y_offset=162)
        # --- prevod casu
        local_dt = localtime(order.montage_termin)
        self.utils.draw_text(
            f"{order.format_datetime(local_dt)}", x_offset=x2, y_offset=175
        )
        self.utils.draw_text(f"{order.team}", x_offset=x2, y_offset=190)

    def general(self) -> None:
        """general pdf section"""
        pass


class Utility:
    """Utilitky pro PDF generator"""

    def __init__(self, cfg, cvs):
        self.cfg = cfg
        self.cvs = cvs

    FONT_DIR: Path = settings.BASE_DIR / "files"
    FONTS: dict[str, Path] = {
        "Roboto-Regular": FONT_DIR / "Roboto-Regular.ttf",
        "Roboto-Light": FONT_DIR / "Roboto-Light.ttf",
        "Roboto-Semibold": FONT_DIR / "Roboto-Semibold.ttf",
    }

    @staticmethod
    def font_register() -> None:
        """Registrujeme fonty do pameti pro reportlab"""
        for name, path in Utility.FONTS.items():
            pdfmetrics.registerFont(TTFont(name, str(path)))

    def draw_text(
        self,
        text: str,
        x_offset=None,
        y_offset: float = 0,
        font="Roboto-Regular",
        font_size=None,
    ) -> None:
        """Vykresluje text"""
        if font_size is None:
            font_size = self.cfg.font_size_normal
        if x_offset is None:
            x_offset = self.cfg.x_offset

        self.cvs.setFont(font, font_size)
        self.cvs.drawString(
            x_offset, self.cfg.height - self.cfg.y_offset - y_offset, text
        )

    def draw_dotted_line(
        self, x1: float, y1: float, x2: float, y2: float, width: int = 1
    ) -> None:
        self.cvs.setLineWidth(width)
        self.cvs.setDash(1, 2)
        self.cvs.line(x1, y1, x2, y2)

    def draw_checkbox(
        self, text: str, x: float, y: float, x_txt: float, y_txt: float
    ) -> None:
        self.cvs.setStrokeColor(HexColor("#707070"))
        self.cvs.setFillColor(self.cfg.fill_clr)
        self.cvs.roundRect(x, y, 12, 12, radius=2, stroke=1, fill=1)
        # --- reset na default
        self.cvs.setStrokeColor(self.cfg.border_clr)
        self.cvs.setFillColor(HexColor("#000000"))
        self.draw_text(text, x_txt, y_txt, font_size=self.cfg.font_size_small)

    def place_image(
        self, img_name: str, img_width: float, img_height: float, x: float, y: float
    ) -> None:
        """Place image"""
        self.cvs.drawImage(
            image=self.cfg.files / img_name,
            width=img_width,
            height=img_height,
            x=x,
            y=y,
        )

    def vodoznak(self, text):
        self.cvs.saveState()
        self.cvs.translate(self.cfg.width / 2, self.cfg.height / 2)
        self.cvs.rotate(45)

        self.cvs.setFont("Roboto-Regular", 55)
        self.cvs.setFillColorRGB(0.97, 0.97, 0.97)
        self.cvs.drawCentredString(25, 25, text)

        self.cvs.restoreState()

    def generate_barcode(self, data_string: str, x: float, y: float) -> BytesIO:
        buffer = BytesIO()
        barcode: code128.Code128 = code128.Code128(
            data_string,
            barHeight=25,
            barWidth=1,
            humanReadable=False,
        )
        barcode.drawOn(self.cvs, x, y)
        buffer.seek(0)
        return buffer


if __name__ == "__main__":
    ...
