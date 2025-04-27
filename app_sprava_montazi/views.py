"""app_sprava_montazi View"""

from typing import Any
from rich.console import Console
from django.db.models.query import QuerySet
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, View
from .models import Order, DistribHub, Status, Team
from .forms import TeamForm

cons: Console = Console()


class IndexView(LoginRequiredMixin, TemplateView):
    """Index View"""

    template_name: str = "base.html"


class HomePageView(LoginRequiredMixin, TemplateView):
    """Homepage View"""

    template_name: str = "app_sprava_montazi/homepage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["active"] = "homepage"
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard View"""

    template_name: str = "app_sprava_montazi/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["active"] = "dashboard"
        return context


class OrdersView(LoginRequiredMixin, ListView):
    """Vypis seznamu modelu Order"""

    model = Order
    template_name = "app_sprava_montazi/orders_all.html"
    context_object_name = "orders"

    def get_queryset(self) -> QuerySet[Any]:
        orders = Order.objects.all()
        status: str = self.request.GET.get("status", "").strip()
        if status:
            orders = orders.filter(status=status)
        return orders

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["statuses"] = Status
        context["active"] = "orders_all"

        return context


class TeamsView(LoginRequiredMixin, ListView):
    """Vypis seznamu modelu Order"""

    model = Team
    template_name = "app_sprava_montazi/teams_all.html"
    context_object_name = "teams"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["active"] = "teams"

        return context


class TeamCreateView(LoginRequiredMixin, CreateView):
    """Vypis seznamu modelu Order"""

    model = Team
    form_class = TeamForm
    template_name = "app_sprava_montazi/partials/team_form.html"
    success_url = reverse_lazy("teams")
