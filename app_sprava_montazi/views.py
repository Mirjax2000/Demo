"""app_sprava_montazi View"""

from time import sleep
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.generic import TemplateView, View
from .models import Order, DistribHub
from rich.console import Console

cons: Console = Console()


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "base.html"


class HomePageView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        template_name = "app_sprava_montazi/partials/homepage.html"
        sleep(1)
        return render(self.request, template_name)


class DashboardView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        template_name = "app_sprava_montazi/partials/dashboard.html"
        sleep(2)
        return render(self.request, template_name)


class OrdersAllView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        orders = Order.objects.all().order_by("-created")
        paginator = Paginator(orders, 15)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context = {"page_obj": page_obj}
        return render(request, "app_sprava_montazi/partials/orders_all.html", context)
