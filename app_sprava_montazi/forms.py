"""Forms"""

from django import forms
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from .models import Order, Article, DistribHub, Team, Client


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "order_number",
            "distrib_hub",
            "mandant",
            "status",
            "delivery_termin",
            "evidence_termin",
            "montage_termin",
            "team_type",
            "team",
            "notes",
        ]
        widgets = {
            "order_number": forms.TextInput(
                attrs={"class": "L-form__input", "placeholder": "Číslo zakázky..."}
            ),
            "distrib_hub": forms.Select(
                attrs={"class": "L-form__input", "placeholder": "místo určení..."}
            ),
            "mandant": forms.TextInput(
                attrs={"class": "L-form__input", "placeholder": "Mandant..."}
            ),
            "status": forms.Select(
                attrs={"class": "L-form__input", "placeholder": "stav..."}
            ),
            "team_type": forms.Select(
                attrs={"class": "L-form__input", "placeholder": "Realizace kým..."}
            ),
            "team": forms.Select(
                attrs={"class": "L-form__input", "placeholder": "Montážní tým..."}
            ),
            "delivery_termin": forms.DateInput(
                attrs={"class": "L-form__date", "type": "date"}
            ),
            "evidence_termin": forms.DateInput(
                attrs={"class": "L-form__date", "type": "date"}
            ),
            "montage_termin": forms.DateTimeInput(
                attrs={"class": "L-form__datetime", "type": "datetime-local"}
            ),
            "notes": forms.Textarea(
                attrs={"class": "L-form__input", "rows": 4, "placeholder": "Poznámky"}
            ),
        }
        error_messages = {
            "order_number": {
                "required": "číslo objednávky je povinné",
                "unique": "objednávka uz existuje.",
            },
            "distrib_hub": {
                "required": "místo určení je povinné",
            },
        }


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
                    "rows": 4,
                    "placeholder": "poznámky...",
                }
            ),
        }


ArticleInlineFormSet = inlineformset_factory(
    Order,
    Article,
    form=ArticleForm,
    extra=5,
    can_delete=True,
)


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
            "phone": {},
            "zip_code": {
                "required": "Jméno je povinné!",
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
                "unique": "Tento kod uz existuje",
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
                    "class": "form-check-input",
                }
            ),
            "price_per_hour": forms.NumberInput(
                attrs={
                    "class": "L-form__input",
                    "placeholder": "Cena za hodinu",
                }
            ),
            "price_per_km": forms.NumberInput(
                attrs={"class": "L-form__input", "placeholder": "Cena za km"}
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
                "required": "Telefon je povinny",
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
