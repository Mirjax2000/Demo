"""app_sprava_montazi View"""

from typing import Any
from rich.console import Console
from django.db import transaction
from django.conf import settings
from django.core.management import call_command
from django.db.models.query import QuerySet
from django.core.management import CommandError
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.forms import BaseModelForm, inlineformset_factory
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
    FormView,
)
from .models import Order, Status, Team, Article, Client
from .forms import TeamForm, ArticleForm, OrderForm, ClientForm, UploadForm, DistribHub

cons: Console = Console()
APP_URL = "app_sprava_montazi"


class IndexView(LoginRequiredMixin, TemplateView):
    """Index View"""

    template_name = "base.html"


class HomePageView(LoginRequiredMixin, TemplateView):
    """Homepage View"""

    template_name = f"{APP_URL}/homepage/homepage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # --- navigace
        context["active"] = "homepage"
        return context


class CreatePageView(LoginRequiredMixin, FormView):
    """Createpage View using FormView"""

    template_name = f"{APP_URL}/create/create.html"
    form_class = UploadForm
    success_url = reverse_lazy("createpage")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # --- navigace
        context["active"] = "create"
        return context

    def form_valid(self, form) -> HttpResponse:
        """Voláno, když je formulář validní."""
        upload = form.save()
        try:
            call_command("import_data", upload.file.path)
            messages.success(self.request, "Import dokončen.")
            return super().form_valid(form)
        # ---
        except KeyError:
            if settings.DEBUG:
                cons.log("Chyba: spatny CSV soubor", style="red")
            messages.error(self.request, "Špatný typ souboru CSV")
            return redirect("createpage")
        # ---
        except DistribHub.DoesNotExist:
            if settings.DEBUG:
                cons.log("Chyba DistribHub neexistuje", style="red")
            messages.error(self.request, "Neexistujicí místo určení!")
            return redirect("createpage")
        # ---
        except ValueError as e:
            if settings.DEBUG:
                cons.log(f"Chyba hodnoty {str(e)}", style="red")
            messages.error(self.request, f"Chyba hodnoty v souboru CSV! {str(e)}")
            return redirect("createpage")
        # ---
        except Exception as e:
            if settings.DEBUG:
                cons.log(f"Chyba {str(e)}", style="red")
            messages.error(self.request, "Neznamá chyba!")
            return redirect("createpage")


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard View"""

    template_name = f"{APP_URL}/dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # --- navigace
        context["active"] = "dashboard"
        return context


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    """Uprav zakaznika"""

    model = Client
    form_class = ClientForm
    template_name = f"{APP_URL}/orders/order_update_client-form.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        order_pk = self.kwargs["order_pk"]
        order = Order.objects.get(pk=order_pk)
        articles = Article.objects.filter(order=order_pk)

        context["order"] = order
        context["articles"] = articles
        # --- vycistit btn update/create
        context["form_type"] = "update"
        # --- navigace
        context["active"] = "orders_all"

        return context

    def form_valid(self, form) -> HttpResponse:
        messages.success(self.request, f"Zákazník: {self.object} aktualizován.")
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse("order_detail", kwargs={"pk": self.kwargs["order_pk"]})


class OrderCreateView(LoginRequiredMixin, View):
    """Vytvor novou zakazku"""

    template = f"{APP_URL}/orders/order_form.html"

    articleInlineFormSet = inlineformset_factory(
        Order,
        Article,
        form=ArticleForm,
        extra=1,
        can_delete=True,
    )

    def get_forms(self, data=None):
        return (
            OrderForm(data),
            ClientForm(data),
            self.articleInlineFormSet(data, prefix="article_set"),
        )

    def get(self, request, *args, **kwargs) -> HttpResponse:
        order_form, client_form, article_formset = self.get_forms()

        context = {
            "order_form": order_form,
            "client_form": client_form,
            "article_formset": article_formset,
            # --- vycistit btn update/create
            "form_type": "create",
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
            # --- vycistit btn update/create
            "form_type": "create",
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


class OrderUpdateView(LoginRequiredMixin, View):
    """Uprav objednavku"""

    template = f"{APP_URL}/orders/order_update_order-form.html"

    def get_object(self):
        return get_object_or_404(Order, pk=self.kwargs["pk"])

    articleInlineFormSet = inlineformset_factory(
        Order,
        Article,
        form=ArticleForm,
        extra=0,
        can_delete=True,
    )

    def get_forms(self, instance, data=None):
        return (
            OrderForm(data, instance=instance),
            self.articleInlineFormSet(data, instance=instance, prefix="article_set"),
        )

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        order_form, article_formset = self.get_forms(order)

        context = {
            "order": order,
            "order_form": order_form,
            "article_formset": article_formset,
            # --- vycistit btn update/create
            "form_type": "update",
            # --- navigace
            "active": "orders_all",
        }
        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        order = self.get_object()
        order_form, article_formset = self.get_forms(order, request.POST)

        context = {
            "order": order,
            "order_form": order_form,
            "article_formset": article_formset,
            # --- vycistit btn update/create
            "form_type": "update",
            # --- navigace
            "active": "orders_all",
        }

        if order_form.is_valid() and article_formset.is_valid():
            try:
                with transaction.atomic():
                    order = order_form.save(commit=False)
                    order.save()
                    article_formset.instance = order
                    article_formset.save()
                messages.success(request, "Objednávka upravena.")
                return redirect(reverse("order_detail", kwargs={"pk": order.id}))

            except Exception as e:
                if settings.DEBUG:
                    cons.log(f"chyba při aktualizaci: {str(e)}")

        messages.error(request, "Nastala chyba při ukládání změn.")
        return render(request, self.template, context)


class OrdersView(LoginRequiredMixin, ListView):
    """Vypis seznamu modelu Order"""

    model = Order
    template_name = f"{APP_URL}/orders/orders_all.html"
    context_object_name = "orders"

    def get_queryset(self) -> QuerySet[Any]:
        orders = Order.objects.exclude(status="Hidden")
        status: str = self.request.GET.get("status", "").strip()
        if status:
            orders = Order.objects.filter(status=status)
        return orders

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["statuses"] = Status
        # --- navigace
        context["active"] = "orders_all"

        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = f"{APP_URL}/orders/order_detail.html"
    context_object_name = "order"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        order_pk = self.kwargs["pk"]
        articles = Article.objects.filter(order=order_pk)

        context["articles"] = articles
        # --- navigace
        context["active"] = "orders_all"

        return context


class TeamsView(LoginRequiredMixin, ListView):
    """Vypis seznamu modelu Order"""

    model = Team
    template_name = f"{APP_URL}/teams/teams_all.html"
    context_object_name = "teams"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        # --- navigace
        context["active"] = "teams"
        return context


class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    form_class = TeamForm
    template_name = f"{APP_URL}/teams/team_form.html"
    success_url = reverse_lazy("teams")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # --- vycistit btn create/update
        context["form_type"] = "create"
        # --- navigace
        context["active"] = "teams"
        return context

    def form_valid(self, form) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(self.request, f"Tým: {self.object} byl úspěšně vytvořen.")
        return response


class TeamUpdateView(LoginRequiredMixin, UpdateView):
    model = Team
    form_class = TeamForm
    template_name = f"{APP_URL}/teams/team_form.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # --- vycistit btn create/update
        context["form_type"] = "update"
        # --- navigace
        context["active"] = "teams"
        return context

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        messages.success(self.request, f"Team: {self.object} byl aktualizovan.")
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse("team_detail", kwargs={"slug": self.object.slug})


class TeamDetailView(LoginRequiredMixin, DetailView):
    model = Team
    template_name = f"{APP_URL}/teams/team_detail.html"
    context_object_name = "team"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # --- navigace
        context["active"] = "teams"
        return context
