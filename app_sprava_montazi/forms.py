from django import forms
from django.forms import widgets
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
