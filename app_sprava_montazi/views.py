"""app_sprava_montazi View"""

from typing import Any
from rich.console import Console
from django.db import transaction
from django.conf import settings
from django.db.models.query import QuerySet
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.template.loader import render_to_string
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)
from .models import Order, DistribHub, Status, Team, Article, Client
from .forms import TeamForm, ArticleInlineFormSet, OrderForm, ClientForm
from django.forms import BaseModelForm, formset_factory

cons: Console = Console()


class IndexView(LoginRequiredMixin, TemplateView):
    """Index View"""

    template_name: str = "base.html"


class HomePageView(LoginRequiredMixin, TemplateView):
    """Homepage View"""

    template_name: str = "app_sprava_montazi/homepage/homepage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["active"] = "homepage"
        return context


class CreatePageView(LoginRequiredMixin, TemplateView):
    """Createpage View"""

    template_name: str = "app_sprava_montazi/create/create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["active"] = "create"
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard View"""

    template_name: str = "app_sprava_montazi/dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["active"] = "dashboard"
        return context


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "app_sprava_montazi/orders/order_detail_client-form.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        order_pk = self.kwargs["order_pk"]
        order = Order.objects.get(pk=order_pk)
        articles = Article.objects.filter(order=order_pk)

        context["order"] = order
        context["articles"] = articles
        context["active"] = "orders"

        return context

    def form_valid(self, form) -> HttpResponse:
        messages.success(self.request, f"Zákazník: {self.object} aktualizován.")
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse("order_detail", kwargs={"pk": self.kwargs["order_pk"]})


class OrdersView(LoginRequiredMixin, ListView):
    """Vypis seznamu modelu Order"""

    model = Order
    template_name = "app_sprava_montazi/orders/orders_all.html"
    context_object_name = "orders"

    def get_queryset(self) -> QuerySet[Any]:
        orders = Order.objects.exclude(status="hidden")
        status: str = self.request.GET.get("status", "").strip()
        if status:
            orders = orders.filter(status=status)
        return orders

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["statuses"] = Status
        # --- navigace
        context["active"] = "orders_all"

        return context


class OrderCreateView(LoginRequiredMixin, View):
    template = "app_sprava_montazi/orders/order_form.html"

    def get_forms(self, data=None):
        return (
            OrderForm(data),
            ClientForm(data),
            ArticleInlineFormSet(data),
        )

    def get(self, request, *args, **kwargs) -> HttpResponse:
        order_form, client_form, article_formset = self.get_forms()

        context = {
            "order_form": order_form,
            "client_form": client_form,
            "article_formset": article_formset,
            # --- navigace
            "active": "orders_all",
        }
        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        order_form, client_form, article_formset = self.get_forms(request.POST)
        context = {
            "order_form": order_form,
            "client_form": client_form,
            "article_formset": article_formset,
            # --- navigace
            "active": "orders_all",
        }

        if (
            client_form.is_valid()
            and order_form.is_valid()
            and article_formset.is_valid()
        ):
            try:
                with transaction.atomic():
                    client = client_form.save()
                    order = order_form.save(commit=False)
                    order.client = client
                    order.save()
                    article_formset.instance = order
                    article_formset.save()
                messages.success(request, "Objednávka vytvořena.")
                return redirect(reverse("order_detail", kwargs={"pk": order.id}))

            except Exception as e:
                if settings.DEBUG:
                    cons.log(f"chyba: {str(e)}")

        messages.error(request, "Nastala chyba při ukládání objednávky.")
        return render(request, self.template, context)


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "app_sprava_montazi/orders/order_detail.html"
    context_object_name = "order"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        order_pk = self.kwargs["pk"]
        articles = Article.objects.filter(order=order_pk)

        context["articles"] = articles
        # --- navigace
        context["active"] = "orders"

        return context


class TeamsView(LoginRequiredMixin, ListView):
    """Vypis seznamu modelu Order"""

    model = Team
    template_name = "app_sprava_montazi/teams/teams_all.html"
    context_object_name = "teams"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        # --- navigace
        context["active"] = "teams"
        return context


class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    form_class = TeamForm
    template_name = "app_sprava_montazi/teams/team_form.html"
    success_url = reverse_lazy("teams")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # --- navigace
        context["active"] = "teams"
        return context

    def form_valid(self, form) -> HttpResponse:
        response = super().form_valid(form)
        cons.log(response)
        messages.success(self.request, f"Tým: {self.object} byl úspěšně vytvořen.")
        return response


class TeamUpdateView(LoginRequiredMixin, UpdateView):
    model = Team
    form_class = TeamForm
    template_name = "app_sprava_montazi/teams/team_form.html"
    success_url = reverse_lazy("teams")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # --- navigace
        context["active"] = "teams"
        return context

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        messages.success(self.request, f"Team: {self.object} byl aktualizovan.")
        return super().form_valid(form)


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
                    return redirect("order_detail", pk=order.id)
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
