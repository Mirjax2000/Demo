"""app_sprava_montazi View"""

from rich.console import Console
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView, View
from .models import Order, DistribHub, Status
from django.db.models import Q

cons: Console = Console()


class IndexView(LoginRequiredMixin, TemplateView):
    """Index View"""

    template_name: str = "base.html"


class HomePageView(LoginRequiredMixin, View):
    """Homepage View"""

    def get(self, *args, **kwargs) -> HttpResponse:
        template_name: str = "app_sprava_montazi/partials/homepage.html"
        return render(self.request, template_name)


class DashboardView(LoginRequiredMixin, View):
    """Dashboard View"""

    def get(self, *args, **kwargs) -> HttpResponse:
        template_name: str = "app_sprava_montazi/partials/dashboard.html"
        return render(self.request, template_name)


class OrdersAllView(LoginRequiredMixin, View):
    """Vypis seznamu modelu Order"""

    def get(self, request, *args, **kwargs) -> HttpResponse:
        orders = Order.objects.all().order_by("-created")
        #
        paginator: Paginator = Paginator(orders, 15)
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)
        #
        context: dict = {
            "page_obj": page_obj,
            "statuses": Status,
        }
        #
        return render(request, "app_sprava_montazi/partials/orders_all.html", context)


class OrdersSearchView(LoginRequiredMixin, View):
    """Vypis seznamu modelu Order"""

    def post(self, request, *args, **kwargs) -> HttpResponse:
        status: str = request.POST.get("status", "").strip()
        query: str = request.POST.get("query", "").strip().lower()
        orders = Order.objects.all()
        if query:
            orders = orders.filter(
                Q(order_number__icontains=query)
                | Q(client__name__icontains=query)
                | Q(distrib_hub__slug__icontains=query)
                | Q(mandant__icontains=query)
            )
        if status:
            orders = orders.filter(status=status)
        #
        orders = orders.order_by("-created")
        #
        paginator: Paginator = Paginator(orders, 15)
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)
        #
        context: dict = {
            "page_obj": page_obj,
            "statuses": Status,
        }
        #
        return render(request, "app_sprava_montazi/partials/orders_all.html", context)


