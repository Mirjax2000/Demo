"""app_sprava_montazi View"""

from typing import Any
from rich.console import Console
from django.db.models.query import QuerySet
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)
from .models import Order, DistribHub, Status, Team, Article
from .forms import TeamForm, ArticleInlineFormSet, OrderForm, ClientForm
from django.forms import formset_factory

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
    model = Team
    form_class = TeamForm
    template_name = "app_sprava_montazi/team_form.html"
    success_url = reverse_lazy("teams")

    def form_valid(self, form):
        messages.success(self.request, "Tým byl úspěšně vytvořen.")
        return super().form_valid(form)


class TeamUpdateView(LoginRequiredMixin, UpdateView):
    model = Team
    form_class = TeamForm
    template_name = "app_sprava_montazi/team_form.html"
    success_url = reverse_lazy("teams")


def order_create(request):
    if request.method == "POST":
        order_form = OrderForm(request.POST)
        client_form = ClientForm(request.POST)
        article_formset = ArticleInlineFormSet(request.POST)

        if client_form.is_valid():
            client = client_form.save()
            if order_form.is_valid():
                order = order_form.save(commit=False)
                order.client = client  # Přiřadíme uloženého klienta k objednávce
                order.save()  # Nyní uložíme objednávku
                article_formset = ArticleInlineFormSet(request.POST, instance=order)
                if article_formset.is_valid():
                    article_formset.save()
                    return redirect("order_detail", order_id=order.id)
                else:
                    # Pokud se artikly nevalidují, musíme smazat uloženého klienta a objednávku
                    client.delete()
                    if order.id:
                        order.delete()
                    # Znovu zobrazíme formulář s chybami
                    return render(
                        request,
                        "order_create.html",
                        {
                            "order_form": order_form,
                            "article_formset": article_formset,
                            "client_form": client_form,
                        },
                    )
            else:
                # Pokud se objednávka nevaliduje, musíme smazat uloženého klienta
                client.delete()
                # Znovu zobrazíme formulář s chybami
                return render(
                    request,
                    "order_create.html",
                    {
                        "order_form": order_form,
                        "article_formset": article_formset,
                        "client_form": client_form,
                    },
                )
        else:
            article_formset = (
                ArticleInlineFormSet()
            )  # Prázdný formset pro zobrazení chyb
            # Znovu zobrazíme formulář s chybami klienta
            return render(
                request,
                "order_create.html",
                {
                    "order_form": order_form,
                    "article_formset": article_formset,
                    "client_form": client_form,
                },
            )
    else:
        order_form = OrderForm()
        article_formset = ArticleInlineFormSet()
        client_form = ClientForm()

    context = {
        "order_form": order_form,
        "article_formset": article_formset,
        "client_form": client_form,
    }
    return render(request, "app_sprava_montazi/order_form.html", context)


def order_update(request, pk):
    order = Order.objects.get(pk=pk)
    if request.method == "POST":
        order_form = OrderForm(request.POST, instance=order)
        article_formset = ArticleInlineFormSet(request.POST, instance=order)

        if order_form.is_valid() and article_formset.is_valid():
            order = order_form.save()
            article_formset.instance = order
            article_formset.save()
            return redirect("order_detail", pk=order.id)
    else:
        order_form = OrderForm(instance=order)
        article_formset = ArticleInlineFormSet(instance=order)

    context = {
        "order_form": order_form,
        "article_formset": article_formset,
    }
    return render(request, "app_sprava_montazi/order_form.html", context)


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "app_sprava_montazi/order_detail.html"
    context_object_name = "order"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        articles = Article.objects.filter(order=self.object)

        context["active"] = "orders"
        context["articles"] = articles

        return context
