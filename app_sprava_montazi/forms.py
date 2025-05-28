"""Forms"""

from rich.console import Console
from django import forms
from django.utils.text import slugify
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
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
)

cons: Console = Console()


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "order_number",
            "distrib_hub",
            "mandant",
            "status",
            "evidence_termin",
            "delivery_termin",
            "montage_termin",
            "team_type",
            "team",
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
                    "placeholder": "Poznámky",
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["evidence_termin"].input_formats = [
            "%Y-%m-%d",
            "%d.%m.%Y",
            "%d/%m/%Y",
        ]

        self.fields["delivery_termin"].input_formats = [
            "%Y-%m-%d",
            "%d.%m.%Y",
            "%d/%m/%Y",
        ]

        self.fields["montage_termin"].input_formats = [
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d %H:%M",
            "%d.%m.%Y %H:%M",
            "%d/%m/%Y %H:%M",
        ]

    def clean_team_type(self):
        team_type = self.cleaned_data.get("team_type")
        if not team_type:
            return TeamType.BY_ASSEMBLY_CREW
        return team_type

    def clean_status(self):
        status = self.cleaned_data.get("status")
        if not status:
            return Status.NEW
        return status


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["name", "price", "quantity", "note"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "L-form__input", "placeholder": "artikl..."}
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "L-form__input",
                    "placeholder": "cena...",
                    "step": "1",  # krokování po 10
                    "min": "0",
                }
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

        widgets = {
            "name": forms.TextInput(
                attrs={"class": "L-form__input", "placeholder": "celé jméno..."}
            ),
            "street": forms.TextInput(
                attrs={"class": "L-form__input", "placeholder": "ulice..."}
            ),
            "city": forms.TextInput(
                attrs={"class": "L-form__input", "placeholder": "město..."}
            ),
            "zip_code": forms.TextInput(
                attrs={"class": "L-form__input number", "placeholder": "PSC..."}
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "L-form__input number",
                    "placeholder": "Telefon",
                    "type": "tel",
                }
            ),
            "email": forms.EmailInput(
                attrs={"class": "L-form__input", "placeholder": "E-mail"}
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
                attrs={"class": "L-form__input", "placeholder": "Název společnosti"}
            ),
            "city": forms.TextInput(
                attrs={"class": "L-form__input", "placeholder": "Město"}
            ),
            "region": forms.TextInput(
                attrs={"class": "L-form__input", "placeholder": "Region"}
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "L-form__input number",
                    "placeholder": "Telefon",
                    "type": "tel",
                }
            ),
            "email": forms.EmailInput(
                attrs={"class": "L-form__input", "placeholder": "E-mail"}
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
                attrs={"class": "L-form__input", "rows": 4, "placeholder": "Poznámky"}
            ),
        }
        error_messages = {
            "name": {
                "required": "Jméno je povinné!",
                "max_length": "Jméno je příliš dlouhé! (max. 32 znaků)",
                "unique": "Tato spolecnost uz existuje",
            },
            "city": {
                "required": "Jméno je povinné!",
                "max_length": "Jméno je příliš dlouhé! (max. 32 znaků)",
            },
            "phone": {
                "required": "Telefon je povinný",
                "invalid": "Zadej platné telefonní číslo ve formátu 212345678.",
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
                    "id": "formFile",
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
