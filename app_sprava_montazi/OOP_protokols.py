"""protokols to pdf"""

from dataclasses import dataclass
from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path
from typing import Any

from django.utils.timezone import localtime
from django.core.files.base import ContentFile
from django.conf import settings
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.barcode import code128
from reportlab.pdfgen.canvas import Canvas
from rich.console import Console
from .models import Article, Order, OrderPDFStorage

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
    border_radius: int = 3
    border_clr: Color = HexColor("#ABABAB")
    fill_clr: Color = HexColor("#EAEAEA")
    montage_sofa_price: int = 495
    montage_minimal_price: int = 454
    percentage_value: float = 12.00


@dataclass(frozen=True)
class CompanyInfo:
    name: str = "RHENUS Home Delivery s.r.o."
    address: str = "Plzeňská 256, 252 19 Chrášťany"
    ico: str = "IČO: 27629325"
    dic: str = "DIČ: CZ27629325"
    ref: str = "Zapsaná v OR: C 120048, Městský soud v Praze."


class PdfGenerator(ABC):
    """PDF generator"""

    def __init__(self) -> None:
        # --- config ---
        self.cfg: PdfConfig = PdfConfig()
        # --- pro reportlab
        Utility.font_register()
        self.buffer = BytesIO()
        self.cvs: Canvas = Canvas(self.buffer, pagesize=A4)
        # --- subclassy
        self.utils: Utility = Utility(self.cfg, self.cvs, self.buffer)
        self.section: Section = Section(self)

    @abstractmethod
    def generate_pdf_protocol(self, model, data: Any = None) -> bytes:
        pass

    def save_pdf_protocol_to_db(self, model, pdf: bytes) -> bool:
        pdf_content = ContentFile(pdf)
        filename = f"order_{model.order_number.upper()}.pdf"
        pdf_file, created = OrderPDFStorage.objects.get_or_create(order=model)

        # Smaž předchozí soubor, pokud existuje
        if pdf_file.file and pdf_file.file.name:
            pdf_file.file.delete(save=False)

        # Ulož nový PDF soubor
        pdf_file.file.save(filename, pdf_content, save=True)

        if created and settings.DEBUG:
            cons.log(f"pdf: {pdf_file} ulozeno", style="blue bold")
        elif settings.DEBUG:
            cons.log(f"soubor byl nahrazen novym {pdf_file}")

        return created


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
            utils, cvs = self.utils, self.cvs
            utils.draw_txt(
                "Kontaktní údaje zákazníka", y_offset=105, font="Roboto-Semibold"
            )
            utils.draw_txt("Jméno:", y_offset=120)
            utils.draw_txt("Ulice:", y_offset=134)
            utils.draw_txt("PSČ:", y_offset=148)
            utils.draw_txt("Město:", y_offset=162)
            utils.draw_txt("Telefon:", y_offset=176)
            utils.draw_txt("E-mail:", y_offset=190)
            # --- border
            cvs.setDash([])
            cvs.roundRect(37, 604, 173, 90, radius=4, stroke=1, fill=0)

        def team_info(self) -> None:
            utils, cvs = self.utils, self.cvs
            x_offset: float = 388
            utils.draw_txt(
                "Informace o zakázce",
                x_offset=388,
                y_offset=147,
                font="Roboto-Semibold",
            )
            utils.draw_txt("Číslo zakázky:", x_offset=x_offset, y_offset=162)
            utils.draw_txt("Datum / čas:", x_offset=x_offset, y_offset=175)
            utils.draw_txt("Montažní tým:", x_offset=x_offset, y_offset=190)
            # --- border
            cvs.roundRect(385, 604, 173, 48, radius=4, stroke=1, fill=0)

        def faktura_info(self) -> None:
            utils, cvs = self.utils, self.cvs
            x_offset: float = 220
            utils.draw_txt(
                "Fakturační údaje",
                x_offset=x_offset,
                y_offset=105,
                font="Roboto-Semibold",
            )
            utils.draw_txt("Název firmy:", x_offset=x_offset, y_offset=120)
            utils.draw_txt("Adresa:", x_offset=x_offset, y_offset=134)
            utils.draw_txt("IČO:", x_offset=x_offset, y_offset=148)
            utils.draw_txt("DIČ:", x_offset=x_offset, y_offset=162)
            utils.draw_txt("Telefon:", x_offset=x_offset, y_offset=176)
            utils.draw_txt("Email:", x_offset=x_offset, y_offset=190)
            # --- checkbox
            utils.draw_txt("Plátce DPH:", x_offset=x_offset, y_offset=211)
            utils.draw_checkbox("ano", 320, 587, 305, 211)
            utils.draw_checkbox("ne", 358, 587, 347, 211)

            # --- border
            cvs.roundRect(x_offset - 3, 604, 161, 90, radius=4, stroke=1, fill=0)

        def predavaci_protokol_sccz(self) -> None:
            """Predavaci protokol subsection"""
            utils = self.utils
            utils.draw_txt("Čas začátku montáže:", y_offset=540)
            utils.draw_dotted_line(125, 258, 185, 258)
            utils.draw_txt("Čas dokončení montáže:", x_offset=200, y_offset=540)
            utils.draw_dotted_line(295, 258, 355, 258)
            utils.draw_txt(
                "Montáž byla provedena v určeném rozsahu, dle montážního návodu a nejsou třeba další zásahy montážního týmu",
                y_offset=560,
            )
            utils.draw_checkbox("ano", 490, 239, 475, 560)
            utils.draw_checkbox("ne", 535, 239, 524, 560)
            # ---
            utils.draw_txt("Montáž nebyla provedena v určeném rozsahu", y_offset=580)
            utils.draw_checkbox("ano", 490, 218, 475, 580)
            utils.draw_checkbox("ne", 535, 218, 524, 580)
            # ---
            utils.draw_txt("Montáž s vrtáním a kotvením do zdi", y_offset=600)
            utils.draw_checkbox("ano", 490, 198, 475, 600)
            utils.draw_checkbox("ne", 535, 198, 524, 600)
            # ---
            reklamace_txt = "Reklamace nebo poznámka k montáži:"
            utils.draw_txt_field(reklamace_txt, 620, 37, 109, 521, 70)

        def predavaci_protokol_default(self) -> None:
            """Predavaci protokol subsection"""
            utils = self.utils
            utils.draw_txt("Čas začátku montáže:", y_offset=455)
            utils.draw_dotted_line(125, 343, 185, 343)
            utils.draw_txt("Čas dokončení montáže:", x_offset=200, y_offset=455)
            utils.draw_dotted_line(295, 343, 355, 343)
            # ---
            utils.draw_txt(
                "Montáž byla provedena v určeném rozsahu, dle montážního návodu a nejsou třeba další zásahy montážního týmu",
                y_offset=472,
            )
            utils.draw_checkbox("ano", 490, 316, 475, 472)
            utils.draw_checkbox("ne", 535, 316, 524, 472)
            # ---
            utils.draw_txt("Montáž nebyla provedena v určeném rozsahu", y_offset=489)
            utils.draw_checkbox("ano", 490, 299, 475, 489)
            utils.draw_checkbox("ne", 535, 299, 524, 489)
            # ---
            utils.draw_txt("Montáž s vrtáním a kotvením do zdi", y_offset=506)
            utils.draw_checkbox("ano", 490, 282, 475, 506)
            utils.draw_checkbox("ne", 535, 282, 524, 506)
            # ---
            utils.draw_txt(
                "Montáž slouží k bytové potřebě ve smyslu § 48 zákona 235/2004 Sb. ve znění PP",
                y_offset=523,
            )
            utils.draw_checkbox("ano", 490, 265, 475, 523)
            utils.draw_checkbox("ne", 535, 265, 524, 523)
            reklamace_txt = "Reklamace nebo poznámka k montáži:"
            utils.draw_txt_field(reklamace_txt, 540, 37, 200, 521, 60)

        # ---

    def __init__(self, parent: PdfGenerator) -> None:
        # --- atributy
        self.parent: PdfGenerator = parent
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
        utils, company = self.utils, self.company
        utils.draw_txt(company.name, y_offset=11, font="Roboto-Semibold")
        utils.draw_txt(company.address, y_offset=27, font="Roboto-Regular")
        utils.draw_txt(company.ico, y_offset=38)
        utils.draw_txt(company.dic, y_offset=49)
        utils.draw_txt(company.ref, y_offset=60)
        utils.place_img("rhenus_logo.png", img_width=180, img_height=42, x=375, y=760)

    def footer(self) -> None:
        """Footer section"""
        utils, cfg = self.utils, self.cfg
        l_margin: float = cfg.x_offset
        small = cfg.font_size_small
        text_1 = (
            "Zákazník svým podpisem na konci strany tohoto protokolu potvrzujete "
            "správnost všech uvedených údajů a akceptujete všeobecné obchodní podmínky."
        )
        text_2 = "Ústní vedlejší ujednání nejsou platná."

        # --- podpis montera
        utils.draw_txt("podpis montéra", 120, 762)
        utils.draw_dotted_line(x1=70, y1=51, x2=230, y2=51)
        # --- podpis zakaznika
        utils.draw_txt("podpis zákazníka", 415, 762)
        utils.draw_dotted_line(x1=365, y1=51, x2=525, y2=51)
        # --- ujednani
        utils.draw_txt(text_1, l_margin, 705, font="Roboto-Light", font_size=small)
        utils.draw_txt(text_2, l_margin, 715, font="Roboto-Light", font_size=small)

    def sccz_section(self) -> None:
        """Sconto section"""
        utils, cfg, subsection = self.utils, self.cfg, self.subsection
        bigger = cfg.font_size_bigger
        small = cfg.font_size_small
        # ---
        header: str = "Předávací protokol provedených prací"
        utils.draw_txt(header, y_offset=84, font="Roboto-Semibold", font_size=bigger)
        # ---
        subsection.customer_info()
        subsection.team_info()
        # --- poznamky k zakazce
        notes_txt: str = "Poznámky k zakázce:"
        utils.draw_txt_field(notes_txt, 213, 37, 566, 521, 20)
        # ---
        text_1 = "Zákazník prohlašuje, že má-li být zboží připevněno či zavěšeno na stěně, že se ujistil před zahájením prací o povaze a průběhu rozvodů předmětných médií, "
        text_2 = "o nosnosti stěn a případných místních specifikách. Zákazník je povinen informovat Společnost o všech těchto skutečnostech významných pro montáž"
        text_3 = "před zahájením montážních prací."
        utils.draw_txt(text_1, y_offset=247, font="Roboto-Light", font_size=small)
        utils.draw_txt(text_2, font="Roboto-Light", y_offset=256, font_size=small)
        utils.draw_txt(text_3, font="Roboto-Light", y_offset=266, font_size=small)
        # --- podpis zakaznika
        utils.draw_txt("podpis zákazníka", x_offset=415, y_offset=301)
        utils.draw_dotted_line(x1=365, y1=510, x2=525, y2=510)
        # ---
        utils.draw_txt(
            "MONTÁŽ NÁBYTKU", y_offset=300, font="Roboto-Semibold", font_size=bigger
        )
        # --- polozky k montazi
        montaz_txt: str = "Položky k montáži uhrazené dle kupní smlouvy na OD Sconto:"
        utils.draw_txt_field(montaz_txt, 330, 37, 379, 521, 90)
        # --- polozky spotrebniho materialu
        material_text: str = "Použitý nadstandardní spotřební materiál:"
        utils.draw_txt_field(material_text, 440, 37, 289, 521, 70)
        subsection.predavaci_protokol_sccz()

    def sccz_data_section(self, order) -> None:
        """Sconto pdf section with Order data"""
        utils = self.utils
        x1, x2 = 73, 442

        # --- client info
        utils.draw_txt(
            order.client.name[:30],
            x_offset=x1,
            y_offset=120,
            font="Roboto-Semibold",
        )
        utils.draw_txt(order.client.street, x_offset=x1, y_offset=134)
        utils.draw_txt(order.client.format_psc(), x_offset=x1, y_offset=148)
        utils.draw_txt(order.client.city, x_offset=x1, y_offset=162)
        utils.draw_txt(order.client.format_phone(), x_offset=x1, y_offset=176)
        utils.draw_txt(order.client.email[:31], x_offset=x1, y_offset=190)
        # --- order info
        utils.draw_txt(order.order_number.upper(), x_offset=x2, y_offset=162)
        # --- prevod casu
        local_dt = localtime(order.montage_termin)
        utils.draw_txt(
            f"{order.format_datetime(local_dt)}",
            x_offset=x2,
            y_offset=175,
            font="Roboto-Semibold",
        )
        utils.draw_txt(
            f"{order.team}", x_offset=x2, y_offset=190, font="Roboto-Semibold"
        )
        # --- notes
        utils.draw_txt(f"{order.notes[:140]}", y_offset=228, font="Roboto-Light")
        # --- articles
        articles = Article.objects.filter(order=order)
        offset: float = 346.0
        # ---
        for article in articles:
            utils.draw_txt(article.name, y_offset=offset, font="Roboto-Semibold")
            if article.price:
                utils.draw_txt(
                    f"cena: {article.price} Kč", x_offset=150, y_offset=offset
                )
            else:
                utils.draw_txt("cena: 0.00 Kč", x_offset=150, y_offset=offset)

            utils.draw_txt(f"qty: {article.quantity} ks", x_offset=240, y_offset=offset)
            utils.draw_txt(f"pzn.: {article.note[:74]}", x_offset=280, y_offset=offset)
            offset += 14

    def default_section(self) -> None:
        """general pdf section"""
        utils, subsection = self.utils, self.subsection
        bigger = self.cfg.font_size_bigger
        small = self.cfg.font_size_small
        # ---
        header: str = "Vyúčtování provedených prací:"
        utils.draw_txt(header, y_offset=84, font="Roboto-Semibold", font_size=bigger)
        # ---
        subsection.customer_info()
        subsection.faktura_info()
        subsection.team_info()
        # ---
        utils.draw_txt(
            "MONTÁŽ NÁBYTKU", y_offset=220, font="Roboto-Semibold", font_size=bigger
        )
        # --- zony ---
        utils.draw_txt("Zóna 1", x_offset=130, y_offset=250)
        utils.draw_txt("Zóna 2", x_offset=190, y_offset=250)
        utils.draw_txt("Zóna 3", x_offset=250, y_offset=250)
        utils.draw_txt("Nad Zónou 3", x_offset=310, y_offset=250)
        utils.draw_txt(
            "do 10 km", x_offset=126, y_offset=258, font="Roboto-Light", font_size=small
        )
        utils.draw_txt(
            "do 20 km", x_offset=186, y_offset=258, font="Roboto-Light", font_size=small
        )
        utils.draw_txt(
            "do 50 km", x_offset=246, y_offset=258, font="Roboto-Light", font_size=small
        )
        # --- monteri ---
        utils.draw_txt_field("Doprava montérů", 258, 37, 505, 521, 35)
        utils.draw_txt("313,- Kč", x_offset=126, y_offset=273, font="Roboto-Semibold")
        utils.draw_txt("379,- Kč", x_offset=185, y_offset=273, font="Roboto-Semibold")
        utils.draw_txt("470,- Kč", x_offset=246, y_offset=273, font="Roboto-Semibold")
        utils.draw_txt(
            "470 Kč + 20 Kč/km", x_offset=298, y_offset=273, font="Roboto-Semibold"
        )
        utils.draw_txt("km", x_offset=382, y_offset=280)
        utils.draw_dotted_line(x1=397, y1=518, x2=425, y2=518)
        utils.draw_txt("=", x_offset=435, y_offset=280)
        utils.draw_dotted_line(x1=450, y1=518, x2=520, y2=518)
        utils.draw_txt("Kč", x_offset=525, y_offset=280)
        # --- check boxy ---
        utils.draw_checkbox(text="", x=134, y=512, x_txt=0, y_txt=0)
        utils.draw_checkbox(text="", x=192, y=512, x_txt=0, y_txt=0)
        utils.draw_checkbox(text="", x=253, y=512, x_txt=0, y_txt=0)
        utils.draw_checkbox(text="", x=321, y=512, x_txt=0, y_txt=0)
        # --- nabytek ---
        utils.draw_txt_field("Montáž", 312, 37, 437, 521, 50)
        header_3: str = "Montáž: 12% z hodnoty nábytku bez DPH určeného k montáži"
        utils.draw_txt(header_3, x_offset=40, y_offset=330)
        utils.draw_txt("Hodnota zboží", x_offset=295, y_offset=330)
        utils.draw_dotted_line(x1=355, y1=469, x2=425, y2=469)
        utils.draw_txt("=", x_offset=435, y_offset=330)
        utils.draw_dotted_line(x1=450, y1=469, x2=520, y2=469)
        utils.draw_txt("Kč", x_offset=525, y_offset=330)
        # ---
        utils.draw_txt("Sesazení sedací soupravy:", x_offset=40, y_offset=353)
        utils.draw_txt("495,-Kč/ks", x_offset=135, y_offset=353, font="Roboto-Semibold")
        utils.draw_txt("množství", x_offset=360, y_offset=353)
        utils.draw_dotted_line(x1=397, y1=446, x2=425, y2=446)
        utils.draw_txt("=", x_offset=435, y_offset=353)
        utils.draw_dotted_line(450, 446, 520, 446)
        utils.draw_txt("Kč", x_offset=525, y_offset=353)
        # ---
        header_4: str = "Použitý nadstandardní spotřební materiál:"
        utils.draw_txt_field(header_4, 382, 37, 367, 521, 50)
        # --- predavaci protokol
        subsection.predavaci_protokol_default()
        # --- celkova cena
        utils.draw_txt("Minimální cena montáže:", x_offset=40, y_offset=620)
        header_2: str = "454 Kč + doprava montérů"
        utils.draw_txt(header_2, x_offset=132, y_offset=620, font="Roboto-Semibold")
        utils.draw_txt(
            "Celková cena (cena montáže + doprava): ", x_offset=295, y_offset=620
        )
        utils.draw_dotted_line(450, 178, 520, 178)
        utils.draw_txt("Kč", x_offset=525, y_offset=620)
        # ---
        utils.draw_txt("Záloha (platba na OD): ", x_offset=360, y_offset=642)
        utils.draw_dotted_line(450, 156, 520, 156)
        utils.draw_txt("Kč", x_offset=525, y_offset=642)
        # ---
        utils.draw_txt("Sazba DPH: ", x_offset=210, y_offset=664)
        utils.draw_checkbox("15%", 271, 135, 255, 664)
        utils.draw_checkbox("21%", 306, 135, 290, 664)
        utils.draw_checkbox("Přenesená daňová povinnost", 425, 135, 325, 664)
        utils.draw_dotted_line(450, 134, 520, 134)
        utils.draw_txt("Kč", x_offset=525, y_offset=664)
        # ---
        utils.draw_txt("K úhradě: ", x_offset=405, y_offset=686)
        utils.draw_dotted_line(450, 112, 520, 112)
        utils.draw_txt("Kč", x_offset=525, y_offset=686)
        # ---

    def default_data_section(self, order) -> None:
        utils = self.utils
        x1, x2 = 73, 442
        self.montage_calculation(order)

        # --- client info
        utils.draw_txt(
            order.client.name[:30], x_offset=x1, y_offset=120, font="Roboto-Semibold"
        )
        utils.draw_txt(order.client.street, x_offset=x1, y_offset=134)
        utils.draw_txt(order.client.format_psc(), x_offset=x1, y_offset=148)
        utils.draw_txt(order.client.city, x_offset=x1, y_offset=162)
        utils.draw_txt(order.client.format_phone(), x_offset=x1, y_offset=176)
        utils.draw_txt(order.client.email[:31], x_offset=x1, y_offset=190)
        # --- order info
        utils.draw_txt(order.order_number.upper(), x_offset=x2, y_offset=162)
        # --- prevod casu
        local_dt = localtime(order.montage_termin)
        time: str = order.format_datetime(local_dt)
        utils.draw_txt(text=time, x_offset=x2, y_offset=175, font="Roboto-Semibold")
        # ---
        utils.draw_txt(
            f"{order.team}", x_offset=x2, y_offset=190, font="Roboto-Semibold"
        )

    def montage_calculation(self, order) -> None:
        cfg, utils = self.cfg, self.utils
        articles = order.articles.all()
        goods_value: float = 0
        sofa_count: int = 0
        percentage_value: float = 0
        shipping_price: float = 0

        for article in articles:
            if not article.is_sofa:
                if article.price is not None:
                    goods_value += float(article.price) * article.quantity
            else:
                sofa_count += article.quantity

        price_with_sofa: float = sofa_count * cfg.montage_sofa_price
        percentage_value = goods_value / 100 * 12
        price: float = price_with_sofa + percentage_value
        total_price: float = price + shipping_price

        # --- not sofa - percentage
        utils.draw_txt(
            text=utils.x_offset_length(goods_value)[0],
            x_offset=425 - utils.x_offset_length(goods_value)[1],
            y_offset=331,
            font="Roboto-Semibold",
            font_size=cfg.font_size_bigger,
        )
        utils.draw_txt(
            text=utils.x_offset_length(percentage_value)[0],
            x_offset=520 - utils.x_offset_length(percentage_value)[1],
            y_offset=331,
            font="Roboto-Semibold",
            font_size=cfg.font_size_bigger,
        )
        # --- sofa
        utils.draw_txt(
            text=str(sofa_count),
            x_offset=410,
            y_offset=354,
            font="Roboto-Semibold",
            font_size=cfg.font_size_bigger,
        )
        utils.draw_txt(
            text=utils.x_offset_length(price_with_sofa)[0],
            x_offset=520 - utils.x_offset_length(price_with_sofa)[1],
            y_offset=354,
            font="Roboto-Semibold",
            font_size=cfg.font_size_bigger,
        )
        # --- total price
        utils.draw_txt(
            text=utils.x_offset_length(total_price)[0],
            x_offset=520 - utils.x_offset_length(total_price)[1],
            y_offset=622,
            font="Roboto-Semibold",
            font_size=cfg.font_size_bigger,
        )


class Utility:
    """Utilitky pro PDF generator"""

    def __init__(self, cfg, cvs, buffer):
        self.cfg = cfg
        self.cvs = cvs
        self.buffer = buffer

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

    def draw_txt(
        self,
        text: str,
        x_offset=None,
        y_offset: float = 0,
        font="Roboto-Regular",
        font_size=None,
    ) -> None:
        """Vykresluje text"""
        cfg = self.cfg
        if font_size is None:
            font_size = cfg.font_size_normal
        if x_offset is None:
            x_offset = cfg.x_offset

        self.cvs.setFont(font, font_size)
        self.cvs.drawString(x_offset, cfg.height - cfg.y_offset - y_offset, text)

    def draw_dotted_line(
        self, x1: float, y1: float, x2: float, y2: float, width: int = 1
    ) -> None:
        cvs: Canvas = self.cvs
        cvs.setLineWidth(width)
        cvs.setDash(1, 2)
        cvs.line(x1, y1, x2, y2)
        cvs.setDash()

    def draw_checkbox(
        self, text: str, x: float, y: float, x_txt: float, y_txt: float
    ) -> None:
        cvs, cfg = self.cvs, self.cfg
        cvs.setStrokeColor(HexColor("#707070"))
        cvs.setFillColor(cfg.fill_clr)
        cvs.roundRect(x, y, 12, 12, radius=2, stroke=1, fill=1)
        # --- reset na default
        cvs.setStrokeColor(cfg.border_clr)
        cvs.setFillColor(HexColor("#000000"))
        self.draw_txt(text, x_txt, y_txt, font_size=cfg.font_size_small)

    def draw_txt_field(
        self, text: str, y_txt: int, x_rect: int, y_rect: int, width: int, height: int
    ) -> None:
        cvs, cfg = self.cvs, self.cfg
        self.draw_txt(text, y_offset=y_txt)
        # --- border
        cvs.setDash([])
        cvs.roundRect(
            x_rect, y_rect, width, height, radius=cfg.border_radius, stroke=1, fill=0
        )

    def place_img(
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

    def watermark(self, text):
        cvs, cfg = self.cvs, self.cfg
        cvs.saveState()
        cvs.translate(cfg.width / 2, cfg.height / 2)
        cvs.rotate(55)

        cvs.setFont("Roboto-Regular", 61)
        cvs.setFillColorRGB(0.95, 0.95, 0.95)
        cvs.drawCentredString(10, 0, text)

        cvs.restoreState()

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

    def finalize_pdf(self) -> bytes:
        cvs, buffer = self.cvs, self.buffer
        cvs.showPage()
        cvs.save()
        pdf_data = buffer.getvalue()
        buffer.close()
        return pdf_data

    def x_offset_length(self, number: float) -> tuple[str, float]:
        text: str = f"{number:.2f}"
        width: float = pdfmetrics.stringWidth(
            text,
            "Roboto-Semibold",
            self.cfg.font_size_bigger,
        )
        return (text, width)


class SCCZPdfGenerator(PdfGenerator):
    """PDF generator for SCCZ type."""

    def generate_pdf_protocol(self, model: Any = None, data: Any = None) -> bytes:
        section, utils = self.section, self.utils
        # ---
        utils.watermark(CompanyInfo.name)  # --- vodoznak ---
        section.header()  # --- header ---
        section.sccz_section()  # --- body sconto ---
        section.footer()  # --- footer ---
        # ---
        if model is not None:
            order_number = model.order_number
            utils.generate_barcode(order_number.upper(), 370, 670)
            section.sccz_data_section(model)  # --- data layer ---
            cons.log(f"SCCZ pdf: {order_number} sestaven", style="blue")
        else:
            cons.log("SCCZ pdf: obecny Template sestaven", style="blue")
        # ---
        return utils.finalize_pdf()


class DefaultPdfGenerator(PdfGenerator):
    """PDF generator for Default."""

    def generate_pdf_protocol(self, model: Any = None, data: Any = None) -> bytes:
        section, utils = self.section, self.utils
        # ---
        utils.watermark(CompanyInfo.name)  # --- vodoznak ---
        section.header()  # --- header ---
        section.default_section()  # --- body general ---
        section.footer()  # --- footer ---
        # ---
        if model is not None:
            order_number = model.order_number
            shiping: list = data
            utils.generate_barcode(order_number.upper(), 370, 670)
            section.default_data_section(model)  # --- data layer ---
            cons.log(f"General pdf: {order_number} sestaven", style="blue")
            cons.log(f"zona: {shiping[0]} pocet km: {shiping[1]}")
        else:
            cons.log("Default pdf: Obecny Template sestaven", style="blue")
        # ---
        return utils.finalize_pdf()


pdf_generator_classes = {
    "default": DefaultPdfGenerator,
    "SCCZ": SCCZPdfGenerator,
}

if __name__ == "__main__":
    ...
