"""Forms"""

from typing import Any
from rich.console import Console
from django import forms
from django.utils.text import slugify
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import (
    Order,
    Article,
    DistribHub,
    Team,
    Client,
    TeamType,
    Status,
    Upload,
    CallLog,
    OrderMontazImage,
)

cons: Console = Console()


class OrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields["order_number"].disabled = True
            attrs = self.fields["order_number"].widget.attrs
            classes = attrs.get("class", "")
            attrs["class"] = " ".join(filter(None, [classes, "form_cell_disable"]))

        self.fields["team"].empty_label = "Vyberte tým..."  # type: ignore

        self.fields["evidence_termin"].input_formats = [  # type: ignore
            "%Y-%m-%d",
            "%d.%m.%Y",
            "%d/%m/%Y",
        ]

        self.fields["delivery_termin"].input_formats = [  # type: ignore
            "%Y-%m-%d",
            "%d.%m.%Y",
            "%d/%m/%Y",
        ]

        self.fields["montage_termin"].input_formats = [  # type: ignore
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d %H:%M",
            "%d.%m.%Y %H:%M",
            "%d/%m/%Y %H:%M",
        ]

    class Meta:
        model = Order
        fields = [
            "order_number",
            "distrib_hub",
            "mandant",
            "status",
            "client",
            "evidence_termin",
            "delivery_termin",
            "montage_termin",
            "team_type",
            "team",
            "vynos",
            "naklad",
            "notes",
        ]

        widgets = {
            "order_number": forms.TextInput(
                attrs={
                    "class": "L-form__input",
                    "placeholder": "Číslo zakázky...",
                }
            ),
            "distrib_hub": forms.Select(
                attrs={
                    "class": "L-form__select",
                }
            ),
            "mandant": forms.TextInput(
                attrs={
                    "class": "L-form__input",
                    "placeholder": "Mandant...",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "L-form__select",
                }
            ),
            "team_type": forms.Select(
                attrs={
                    "class": "L-form__select",
                }
            ),
            "team": forms.Select(
                attrs={
                    "class": "L-form__select",
                }
            ),
            "client": forms.HiddenInput(
                attrs={
                    "class": "d-none",
                }
            ),
            "evidence_termin": forms.DateInput(
                attrs={
                    "class": "L-form__date",
                    "type": "date",
                },
                format="%Y-%m-%d",
            ),
            "delivery_termin": forms.DateInput(
                attrs={
                    "class": "L-form__date",
                    "type": "date",
                },
                format="%Y-%m-%d",
            ),
            "montage_termin": forms.DateTimeInput(
                attrs={
                    "class": "L-form__date",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "L-form__input",
                    "rows": 4,
                    "placeholder": "Poznámky...",
                }
            ),
            "vynos": forms.NumberInput(
                attrs={
                    "class": "L-form__input",
                    "step": "1",
                    "placeholder": "Výnos...",
                }
            ),
            "naklad": forms.NumberInput(
                attrs={
                    "class": "L-form__input",
                    "step": "1",
                    "placeholder": "Náklad...",
                }
            ),
        }
        error_messages = {
            "order_number": {
                "required": "číslo objednávky je povinné!",
                "unique": "objednávka uz existuje!",
            },
            "mandant": {
                "required": "Mandant je povinný!",
            },
            "distrib_hub": {
                "required": "místo určení je povinné!",
            },
        }

    def clean_order_number(self):
        order_number = self.cleaned_data.get("order_number", "").upper()

        qs = Order.objects.filter(order_number__iexact=order_number)

        # Pokud jde o aktualizaci, vyloučím sám sebe
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("Objednávka už existuje!")

        return order_number

    def clean(self) -> dict[str, Any]:
        cleaned_data: dict[str, Any] = super().clean()
        # kontrola stavu - zaterminovano
        if cleaned_data.get("status") != Status.ADVICED:
            return cleaned_data

        self.validate_adviced(data=cleaned_data)

        return cleaned_data

    def validate_adviced(self, data) -> None:
        """Validace při stavu 'Zatermínováno'"""
        team_type: TeamType = data.get("team_type")
        team: Team = data.get("team")
        client: Client = data.get("client")
        montage_termin = data.get("montage_termin")
        delivery_termin = data.get("delivery_termin")
        naklad = data.get("naklad")
        vynos = data.get("vynos")

        is_montage: bool = team_type == TeamType.BY_ASSEMBLY_CREW
        is_delivery: bool = team_type == TeamType.BY_DELIVERY_CREW
        is_customer: bool = team_type == TeamType.BY_CUSTOMER

        if is_montage:
            self.if_is_montage(
                client, team, montage_termin, delivery_termin, naklad, vynos
            )
        elif is_delivery:
            self.if_is_delivery(
                client, team, montage_termin, delivery_termin, naklad, vynos
            )
        elif is_customer:
            self.add_error(
                "team_type",
                "Pro stav 'Zatermínováno' nesmí být Zákazníkem. Přepni pole podle typu.",
            )

    def if_is_montage(
        self, client: Client, team: Team, montage_termin, delivery_termin, naklad, vynos
    ) -> None:
        if not client:
            self.add_error(
                "client", "Pro stav 'Zatermínováno' je třeba vyplnit zákazníka."
            )
        if client.incomplete:
            self.add_error(
                "client",
                "Zákazník má neúplné údaje, nelze uložit jako 'Zatermínováno'.",
            )
        if not team:
            self.add_error(
                "team", "Pro stav 'Zatermínováno' musí být vybrán montážní tým."
            )

        if not montage_termin:
            self.add_error("montage_termin", "Zadej termín montáže.")

        if not delivery_termin:
            self.add_error("delivery_termin", "Zadej termín doručení.")
        if naklad is None:
            self.add_error("naklad", "Chybí náklad")
        if vynos is None:
            self.add_error("vynos", "Chybí výnos")

    def if_is_delivery(
        self, client: Client, team: Team, montage_termin, delivery_termin, naklad, vynos
    ) -> None:
        if not client:
            self.add_error(
                "client", "Pro stav 'Zatermínováno' je třeba vyplnit zákazníka."
            )
        if team:
            self.add_error(
                "team", "Pro stav 'Zatermínováno' nemá být vybrán montážní tým."
            )
        if montage_termin:
            self.add_error(
                "montage_termin",
                "Pro stav 'Zatermínováno' nemá být vybrán termín montáže.",
            )
        if not delivery_termin:
            self.add_error(
                "delivery_termin",
                "Pro stav 'Zatermínováno' musí být vybrán termín doručení.",
            )
        if naklad is None:
            self.add_error("naklad", "Chybí náklad")
        if vynos is None:
            self.add_error("vynos", "Chybí výnos")


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["name", "quantity", "note"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "L-form__input", "placeholder": "artikl..."}
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "L-form__input",
                    "placeholder": "množství...",
                }
            ),
            "note": forms.Textarea(
                attrs={
                    "class": "L-form__input",
                    "rows": 2,
                    "placeholder": "poznámky...",
                }
            ),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")

        # Validace, že množství je mezi 0 a 999
        if quantity is None:
            raise forms.ValidationError("Množství je povinné.")
        if quantity > 999:
            raise forms.ValidationError("Množství nemůže být větší než 999.")
        if quantity < 0:
            raise forms.ValidationError("Množství nemůže být záporné.")

        return quantity


class ClientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["name"].disabled = True
            attrs_name = self.fields["name"].widget.attrs
            classes_name = attrs_name.get("class", "")
            attrs_name["class"] = " ".join(
                filter(None, [classes_name, "form_cell_disable"])
            )

            self.fields["zip_code"].disabled = True
            attrs_zip = self.fields["zip_code"].widget.attrs
            classes_zip = attrs_zip.get("class", "")
            attrs_zip["class"] = " ".join(
                filter(None, [classes_zip, "form_cell_disable"])
            )

    class Meta:
        model = Client
        fields = [
            "name",
            "street",
            "city",
            "zip_code",
            "phone",
            "email",
        ]

        l_form_input: str = "L-form__input"
        widgets = {
            "name": forms.TextInput(
                attrs={"class": l_form_input, "placeholder": "celé jméno..."}
            ),
            "street": forms.TextInput(
                attrs={"class": l_form_input, "placeholder": "ulice..."}
            ),
            "city": forms.TextInput(
                attrs={"class": l_form_input, "placeholder": "město..."}
            ),
            "zip_code": forms.TextInput(
                attrs={"class": f"{l_form_input} number", "placeholder": "PSC..."}
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": f"{l_form_input} number",
                    "placeholder": "Telefon...",
                    "type": "tel",
                }
            ),
            "email": forms.EmailInput(
                attrs={"class": l_form_input, "placeholder": "E-mail..."}
            ),
        }
        error_messages = {
            "name": {
                "required": "Jméno je povinné!",
            },
            "street": {
                "max_length": "Jméno je příliš dlouhé! (max. 32 znaků)",
            },
            "city": {
                "max_length": "Jméno je příliš dlouhé! (max. 32 znaků)",
            },
            "phone": {
                "required": "Telefon je povinný",
                "invalid": "Zadej platné telefonní číslo ve formátu 602345678.",
            },
            "zip_code": {
                "required": "PSČ je povinné!",
            },
        }

    def clean_zip_code(self) -> str:
        zip_code: str | None = self.cleaned_data.get("zip_code")

        if not zip_code or len(zip_code) != 5:
            raise forms.ValidationError("PSČ musí mít přesně 5 číslic.")
        return zip_code


class DistribHubForm(forms.ModelForm):
    class Meta:
        model = DistribHub
        fields: list = ["code", "city"]
        widgets = {
            "code": forms.TextInput(
                attrs={"class": "L-form__input", "placeholder": "kod..."}
            ),
            "city": forms.TextInput(
                attrs={"class": "L-form__input", "placeholder": "city..."}
            ),
        }

        error_messages = {
            "code": {
                "required": "Kod je povinný!",
                "max_length": "Jméno je příliš dlouhé! (max. 3 znaky)",
                "unique": "Tento kod uz existuje!",
            },
            "city": {
                "required": "Jméno je povinné!",
                "max_length": "Jméno je příliš dlouhé! (max. 32 znaků)",
            },
        }


class TeamForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields["name"].disabled = True
            attrs = self.fields["name"].widget.attrs
            classes = attrs.get("class", "")
            attrs["class"] = " ".join(filter(None, [classes, "form_cell_disable"]))

    class Meta:
        model = Team
        fields = [
            "name",
            "city",
            "region",
            "phone",
            "email",
            "active",
            "price_per_hour",
            "price_per_km",
            "notes",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={"class": "L-form__input", "placeholder": "Název společnosti..."}
            ),
            "city": forms.TextInput(
                attrs={"class": "L-form__input", "placeholder": "Město..."}
            ),
            "region": forms.TextInput(
                attrs={"class": "L-form__input", "placeholder": "Region..."}
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "L-form__input number",
                    "placeholder": "Telefon...",
                    "type": "tel",
                }
            ),
            "email": forms.EmailInput(
                attrs={"class": "L-form__input", "placeholder": "E-mail..."}
            ),
            "active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input C-checkbox",
                }
            ),
            "price_per_hour": forms.NumberInput(
                attrs={
                    "class": "L-form__input",
                    "placeholder": "Cena za hod",
                    "step": "1",
                    "min": "0",
                }
            ),
            "price_per_km": forms.NumberInput(
                attrs={
                    "class": "L-form__input",
                    "placeholder": "Cena za km",
                    "step": "1",
                    "min": "0",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "L-form__input",
                    "rows": 4,
                    "placeholder": "Poznámky...",
                }
            ),
        }

        error_messages = {
            "name": {
                "required": "Jméno je povinné!",
                "max_length": "Jméno je příliš dlouhé! (max. 32 znaků)",
                "unique": "Tato společnost uz existuje",
            },
            "city": {
                "required": "Město je povinné!",
                "max_length": "Město je příliš dlouhé! (max. 32 znaků)",
            },
            "phone": {
                "required": "Telefon je povinný",
                "invalid": "Zadej platné telefonní číslo.",
            },
        }

    def clean_name(self) -> str:
        name = str(self.cleaned_data.get("name"))
        slug = slugify(name)

        qs = Team.objects.filter(slug=slug)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError("Společnost s tímto názvem už existuje.")

        return name


class UploadForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ["file"]
        widgets = {
            "file": forms.FileInput(
                attrs={
                    "class": "form-control mt-1",
                    "id": "CsvFormFile",
                    "type": "file",
                    "accept": ".csv",
                }
            ),
        }
        error_messages = {
            "file": {
                "required": "Soubor je povinný!",
            },
        }


class CallLogForm(forms.ModelForm):
    class Meta:
        model = CallLog
        fields = ["note", "was_successful"]
        widgets = {
            "note": forms.Textarea(
                attrs={
                    "class": "L-form__input",
                    "rows": 2,
                    "placeholder": "Poznámky",
                }
            ),
            "was_successful": forms.Select(
                attrs={"class": "L-form__select", "required": True}
            ),
        }
        error_messages = {
            "was_successful": {
                "required": "Zadat výsledek hovoru!",
            },
            "note": {
                "required": "Nějaké info.",
            },
        }

    def clean_was_successful(self):
        value = self.cleaned_data.get("was_successful")
        if not value:
            raise forms.ValidationError("Zadat výsledek hovoru!")
        return value


CallLogFormSet = inlineformset_factory(
    Client, CallLog, form=CallLogForm, extra=1, can_delete=True
)


class MonthFilterForm(forms.Form):
    MONTHS = [
        ("", "Všechny měsíce"),
        ("01", "Leden"),
        ("02", "Únor"),
        ("03", "Březen"),
        ("04", "Duben"),
        ("05", "Květen"),
        ("06", "Červen"),
        ("07", "Červenec"),
        ("08", "Srpen"),
        ("09", "Září"),
        ("10", "Říjen"),
        ("11", "Listopad"),
        ("12", "Prosinec"),
    ]
    month = forms.ChoiceField(
        choices=MONTHS,
        label="Měsíc",
        required=False,
        widget=forms.Select(attrs={"class": "form-select L-table__select", "id": "month"}),
    )
    year = forms.ChoiceField(
        label="Rok",
        required=False,
        widget=forms.Select(attrs={"class": "form-select L-table__select", "id": "year"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamicky naplnit roky podle evidence_termin + zajistit aktuální rok
        years_qs = Order.objects.dates("evidence_termin", "year", order="DESC")
        current_year = timezone.localdate().year if hasattr(timezone, 'localdate') else timezone.now().year
        year_set = {d.year for d in years_qs}
        year_set.add(current_year)
        years_sorted = sorted(year_set, reverse=True)
        years = [("", "Všechny roky")] + [(str(y), str(y)) for y in years_sorted]
        self.fields["year"].choices = years
        # Pokud je formulář nevyplněný (první načtení), nastav výchozí rok na aktuální
        if not self.is_bound:
            self.fields["year"].initial = str(current_year)
            self.initial["year"] = str(current_year)
