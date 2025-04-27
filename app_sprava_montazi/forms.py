"""Forms"""

from django import forms
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from .models import Order, Article, DistribHub, Team


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields: list = [
            "status",
            "client",
            "montage_termin",
            "team_type",
            "team",
            "notes",
        ]


class ClientForm(forms.ModelForm):
    class Meta:
        model = Order
        fields: list = []


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields: list = []


class DistribHubForm(forms.ModelForm):
    class Meta:
        model = DistribHub
        fields: list = []


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
            "phone": forms.NumberInput(
                attrs={"class": "L-form__input", "placeholder": "Telefon"}
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
                attrs={"class": "L-form__input", "placeholder": "Cena za hodinu"}
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
        if Team.objects.filter(slug=slug).exists():
            raise ValidationError("Společnost s tímto názvem už existuje.")
        return name
