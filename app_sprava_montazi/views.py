"""app_sprava_montazi View"""

from typing import Any
from datetime import datetime
from openpyxl import Workbook
from rich.console import Console

# --- Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.management import call_command
from django.db import transaction
from django.forms import BaseModelForm, inlineformset_factory
from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import CreateView, DetailView, FormView, ListView
from django.views.generic import View, UpdateView, TemplateView

# API rest ---
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

# --- formulare
from .forms import ArticleForm, CallLogFormSet, ClientForm, DistribHub
from .forms import UploadForm, TeamForm, OrderForm

# --- serializer
from .serializer import CustomerDetailSerializer, OrderCustomerUpdateSerializer

# --- modely z DB
from .models import (
    Article,
    CallLog,
    Client,
    Order,
    OrderPDFStorage,
    Status,
    Team,
    TeamType,
)
from .models import HistoricalArticle  # vim o tom je to abstract classa

# pomocne funkce ---
from .utils import filter_orders, format_date, parse_order_filters, update_customers

# 00P classes ---
from .OOP_protokols import DefaultPdfGenerator, pdf_generator_classes
from .OOP_emails import CustomEmail
# --- alias types


cons: Console = Console()
# ---
APP_URL = "app_sprava_montazi"
OD_CHOICES = [
    ("701", "OD Stodůlky"),
    ("703", "OD Černý Most"),
    ("705", "OD Liberec"),
    ("706", "OD Ústí nad Labem"),
    ("707", "OD Č. Budějovice"),
    ("708", "OD Hradec Králové"),
    ("709", "OD Plzeň"),
]
OD_DICT = dict(OD_CHOICES)
# ---


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

        distrib_hubs = DistribHub.objects.filter().exists()
        if not distrib_hubs:
            cons.log("Vytvarim Distrib_huby.", style="blue bold")
            call_command("distrib_hub")

        try:
            call_command("import_data", upload.file.path)
            messages.success(self.request, "Import dokončen.")
            return super().form_valid(form)
        # ---
        except KeyError as e:
            if settings.DEBUG:
                cons.log(f"Chyba: {str(e)}", style="red")
            messages.error(self.request, "Špatný soubor CSV")
            return redirect("createpage")
        # ---
        except DistribHub.DoesNotExist as e:
            if settings.DEBUG:
                cons.log(f"Chyba DistribHub neexistuje. Chyba: {str(e)}", style="red")
            messages.error(self.request, f"Chybné místo určení. Chyba: {str(e)}")
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

        context.update(
            {
                "order": order,
                "articles": articles,
                # --- vycistit btn update/create
                "form_type": "update",
                # --- navigace
                "active": "orders_all",
            }
        )

        return context

    def form_valid(self, form) -> HttpResponse:
        messages.success(
            self.request, f"Zákazník: <strong>{self.object}</strong> aktualizován."
        )
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse("order_detail", kwargs={"pk": self.kwargs["order_pk"]})


class ClientUpdateSecondaryView(LoginRequiredMixin, UpdateView):
    model = Client
    template_name = f"{APP_URL}/orders/client_update_secondary.html"
    form_class = ClientForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # --- vycistit btn update/create
        context["form_type"] = "update"
        # --- navigace
        context["active"] = "orders_all"

        return context

    def form_valid(self, form) -> HttpResponse:
        messages.success(
            self.request, f"Zákazník: <strong>{self.object}</strong> aktualizován."
        )
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse("client_orders", kwargs={"slug": self.object.slug})


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
                start_status = order.status
                with transaction.atomic():
                    order = order_form.save(commit=False)
                    order.save()
                    article_formset.instance = order
                    article_formset.save()
                    end_status = order.status

                if start_status == Status.NEW and end_status == Status.ADVICED:
                    messages.success(
                        request,
                        f"Objednávka změnila status na {Status.ADVICED.label}",
                    )
                else:
                    messages.success(
                        request,
                        f"Objednávka <strong>{order.order_number}</strong> upravena.",
                    )
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

    def dispatch(self, request, *args, **kwargs):
        self.filters = parse_order_filters(request)  # pylint: disable=W0201
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # --- utils.py
        return filter_orders(self.filters)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)

        get_start = (
            datetime.strptime(self.filters["start_date"], "%Y-%m-%d")
            if self.filters["start_date"]
            else None
        )

        get_end = (
            datetime.strptime(self.filters["end_date"], "%Y-%m-%d")
            if self.filters["end_date"]
            else None
        )

        context.update(
            {
                "statuses": Status,
                "raw_status": self.filters["status"],
                "get_status": Status(self.filters["status"]).label
                if self.filters["status"]
                else "",
                "od_choices": OD_CHOICES,
                "raw_od": self.filters["od"],
                "od_value": OD_DICT.get(self.filters["od"], ""),
                "get_start": get_start,
                "get_end": get_end,
                "request": self.request,
                # --- navigace
                "active": "orders_all",
            }
        )

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
        messages.success(
            self.request, f"Tým: <strong>{self.object}</strong> byl úspěšně vytvořen."
        )
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
        next_url = self.request.POST.get("next") or self.request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={self.request.get_host()}
        ):
            return next_url
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


class ClientsOrdersView(LoginRequiredMixin, View):
    template_name = f"{APP_URL}/orders/client_orders.html"

    def get(self, request, slug):
        client = get_object_or_404(Client, slug=slug)
        orders = Order.objects.filter(client=client)
        call_logs = CallLog.objects.filter(client=client)

        formset = CallLogFormSet(queryset=CallLog.objects.none())

        context = {
            "client": client,
            "call_logs": call_logs,
            "orders": orders,
            "formset": formset,
            # -- navigace
            "active": "orders_all",
        }
        return render(request, self.template_name, context)

    def post(self, request, slug):
        client = get_object_or_404(Client, slug=slug)
        orders = Order.objects.filter(client=client)
        call_logs = CallLog.objects.filter(client=client)

        formset = CallLogFormSet(request.POST, instance=client)

        context = {
            "client": client,
            "orders": orders,
            "formset": formset,
            "call_logs": call_logs,
            # -- navigace
            "active": "orders_all",
        }

        if formset.is_valid():
            for form in formset.forms:
                if form.has_changed():
                    instance = form.save(commit=False)
                    instance.client = client
                    instance.user = request.user
                    instance.save()

            messages.success(request, "Hovor zpracován a uložen.")
            return redirect("client_orders", slug=slug)

        messages.error(request, "Hovor nebyl uložen do databáze!")
        return render(request, self.template_name, context)


class OrderHistoryView(LoginRequiredMixin, ListView):
    template_name = f"{APP_URL}/orders/order_detail_history.html"

    def dispatch(self, request, *args, **kwargs):
        self.order_instance = get_object_or_404(Order, pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.order_instance.history.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order"] = self.order_instance

        order_history = list(self.order_instance.history.all())

        try:
            article_history = list(
                HistoricalArticle.objects.filter(order=self.order_instance)
            )
        except Exception as e:
            cons.log(
                f"Chyba při načítání historie HistoricalArticle pro zakázku {self.order_instance.pk}: {e}"
            )
            article_history = []

        all_history = order_history + article_history
        all_history.sort(key=lambda x: x.history_date, reverse=True)

        processed_history_data = []

        for entry in all_history:
            entry_info = {
                "id": entry.history_id,
                "date": entry.history_date,
                "type": entry.history_type,
                "user": entry.history_user,
                "status": Status(entry.status).label
                if hasattr(entry, "status")
                and entry.status is not None
                and entry.status != ""
                else None,
                "team_type": TeamType(entry.team_type).label
                if hasattr(entry, "team_type")
                and entry.team_type is not None
                and entry.team_type != ""
                else None,
                "model": "Article" if isinstance(entry, HistoricalArticle) else "Order",
                "changes": [],
            }

            if isinstance(entry, HistoricalArticle):
                entry_info["name"] = str(getattr(entry, "name", "(neznámý)"))

            if entry.history_type == "~":
                prev_record = entry.prev_record
                if prev_record:
                    delta = entry.diff_against(prev_record)

                    for change in delta.changes:
                        field_name = change.field
                        old_val = change.old
                        new_val = change.new

                        choice_fields = {
                            "team_type": TeamType,
                            "status": Status,
                        }

                        if field_name in choice_fields:
                            choices = choice_fields[field_name]
                            try:
                                old_val_label = (
                                    getattr(choices(old_val), "label", str(old_val))
                                    if old_val is not None and old_val != ""
                                    else "-"
                                )
                                new_val_label = (
                                    getattr(choices(new_val), "label", str(new_val))
                                    if new_val is not None and new_val != ""
                                    else "-"
                                )
                                old_val = old_val_label
                                new_val = new_val_label
                            except ValueError:
                                pass

                        try:
                            original_field = entry._meta.model._meta.get_field(
                                field_name
                            )
                            if (
                                original_field.is_relation
                                and original_field.related_model
                            ):
                                model_class = original_field.related_model

                                if old_val is not None and old_val != "":
                                    try:
                                        old_obj = model_class.objects.get(pk=old_val)
                                        old_val_str = str(old_obj)
                                    except model_class.DoesNotExist:
                                        old_val_str = f"ID:{old_val} (smazáno)"
                                    except Exception:
                                        old_val_str = str(old_val)
                                    old_val = old_val_str if old_val_str else "-"

                                if new_val is not None and new_val != "":
                                    try:
                                        new_obj = model_class.objects.get(pk=new_val)
                                        new_val_str = str(new_obj)
                                    except model_class.DoesNotExist:
                                        new_val_str = f"ID:{new_val} (smazáno)"
                                    except Exception:
                                        new_val_str = str(new_val)
                                    new_val = new_val_str if new_val_str else "-"

                        except Exception:
                            pass

                        entry_info["changes"].append(
                            {
                                "field": field_name,
                                "old": old_val,
                                "new": new_val,
                            }
                        )

            processed_history_data.append(entry_info)

        context["history_data"] = processed_history_data
        # --- navigace ---
        context["active"] = "orders_all"
        return context


class ExportOrdersExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # --- utils.py
        filters = parse_order_filters(request)
        orders = filter_orders(filters)

        wb = Workbook()
        ws = wb.active
        ws.title = "Objednávky"

        headers = [
            "Číslo zakázky",
            "Místo určení",
            "Mandant",
            "Stav",
            "Zákazník",
            "PSC",
            "Termín evidence",
            "Termín doručení",
            "Termín montáže",
            "Realizace kým",
            "Montážní tým",
            "Poznámky",
        ]
        ws.append(headers)

        for order in orders:
            team = str(order.team) if order.team else ""
            team_type = order.get_team_type_display()
            status = order.get_status_display()
            evidence_termin = format_date(order.evidence_termin)  # utils.py
            delivery_termin = format_date(order.delivery_termin)  # utils.py
            montage_termin = format_date(order.montage_termin)  # utils.py

            ws.append(
                [
                    str(order.order_number).upper(),
                    str(order.distrib_hub),
                    str(order.mandant),
                    str(status),
                    str(order.client),
                    str(order.client.zip_code),
                    evidence_termin,
                    delivery_termin,
                    montage_termin,
                    team_type,
                    team,
                    order.notes,
                ]
            )
        # ---
        suffix: str = (
            f"{filters['status']}_{filters['od']}_"
            f"{filters['start_date']}_{filters['end_date']}"
        )
        # ---
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = (
            f"attachment; filename=objednavky-{suffix}.xlsx"
        )
        wb.save(response)
        return response


class PdfView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        mandant = self.kwargs.get("mandant", "default")
        # ---
        generator_class = pdf_generator_classes.get(mandant, DefaultPdfGenerator)
        generator_instance = generator_class()
        # ---
        pdf = generator_instance.generate_pdf_protocol(model=None)
        # ---
        filename = f"Protokol_{mandant}.pdf"
        response = HttpResponse(content=pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{filename}"'

        return response


class OrderProtocolView(LoginRequiredMixin, DetailView):
    model = Order
    context_object_name = "order"
    template_name = template_name = f"{APP_URL}/orders/montazni_protokol.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        order = context["object"]
        pdf_exists = OrderPDFStorage.objects.filter(order=order.pk).exists()
        context.update(
            {
                "pdf_exists": pdf_exists,
                "team": order.team,
                "active": "orders_all",
            }
        )
        return context


class OrderPdfView(LoginRequiredMixin, DetailView):
    model = Order

    def render_to_response(self, context, **response_kwargs):
        order = context["object"]
        # ---
        generator_class = pdf_generator_classes.get(order.mandant, DefaultPdfGenerator)
        generator_instance = generator_class()
        # ---
        pdf = generator_instance.generate_pdf_protocol(model=order)
        # ---
        filename = f"objednavka_{order.order_number.upper()}.pdf"
        response = HttpResponse(content=pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        # ---
        return response


class GeneratePDFView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        order = get_object_or_404(Order, pk=pk)

        generator_class = pdf_generator_classes.get(order.mandant, DefaultPdfGenerator)
        generator_instance = generator_class()
        pdf_io = generator_instance.generate_pdf_protocol(model=order)
        created = generator_instance.save_pdf_protocol_to_db(model=order, pdf=pdf_io)
        # ---
        if created:
            messages.success(
                request,
                (
                    f"PDF: <strong>{str(order).upper()}</strong> "
                    f"byl úspěšně vygenerován a uložen."
                ),
            )
        else:
            messages.success(
                request,
                (
                    f"PDF: <strong>{str(order).upper()}</strong> "
                    f"byl úspěšně vygenerováno,uložen a nahrazen."
                ),
            )

        return redirect("protocol", pk=pk)

    def post(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        order = get_object_or_404(Order, pk=pk)
        zona: int = int(request.POST.get("zona") or 0)
        km: int = int(request.POST.get("zona_km") or 0)
        data: dict[str, int] = {"zona": zona, "km": km}

        default_pdf_protocol = DefaultPdfGenerator()
        default_pdf_protocol.data = data
        pdf_io = default_pdf_protocol.generate_pdf_protocol(model=order)
        created = default_pdf_protocol.save_pdf_protocol_to_db(model=order, pdf=pdf_io)
        # ---
        if created:
            messages.success(
                request,
                (
                    f"PDF: <strong>{str(order).upper()}</strong> "
                    f"byl úspěšně vygenerován a uložen."
                ),
            )
        else:
            messages.success(
                request,
                (
                    f"PDF: <strong>{str(order).upper()}</strong> "
                    f"byl úspěšně vygenerováno,uložen a nahrazen."
                ),
            )

        return redirect("protocol", pk=pk)


class CheckPDFProtocolView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs) -> FileResponse:
        pk = kwargs["pk"]
        order = get_object_or_404(Order, pk=pk)
        stored_pdf_info = get_object_or_404(OrderPDFStorage, order=order)
        pdf_file = stored_pdf_info.file

        return FileResponse(
            pdf_file.open("rb"),
            content_type="application/pdf",
            as_attachment=False,
            filename=pdf_file.name.split("/")[-1],
        )


# --- Emails ---
class SendMailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        order = get_object_or_404(Order, pk=pk)
        pdf_file = get_object_or_404(OrderPDFStorage, order=pk)
        body: str = (
            f"Zasíláme vám montážní protokol.\n\n"
            f"Datum montáže: {order.format_datetime(order.montage_termin)}\n\n"
            f"V případě dotazů nás kontaktujte.\n"
            f"S pozdravem,\n"
            f"Tým Rhenus"
        )

        email: CustomEmail = CustomEmail(
            f"Montazni protokol: {order.order_number.upper()} ",
            body,
            [order.team.email],
            [pdf_file.file.path],
        )
        email.send_email_with_pdf(order.team.email)
        messages.success(
            request,
            f"Email pro montazni tym: <strong>{order.team}</strong> na adresu <strong>{order.team.email}</strong> odeslan",
        )
        return redirect("protocol", pk=pk)


# --- API ---
class IncompleteCustomersView(APIView):
    permission_classes = [IsAuthenticated]  # jen pro přihlášené uživatele

    def get(self, request) -> Response:
        qs = Order.objects.filter(client__incomplete=True)
        seznam = [record.order_number.upper() for record in qs]
        cons.log(f"seznam nekompletnich klientu: {seznam}")
        return Response(seznam)


class CustomerUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderCustomerUpdateSerializer(data=request.data)
        if serializer.is_valid():
            updates = serializer.validated_data["updates"]

            update_customers(updates)

            return Response({"message": "Zákazníci byli aktualizováni."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
