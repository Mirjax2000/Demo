"""servisni views"""

from rich.console import Console

# --- Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.http import JsonResponse


# --- modely z DB
from .models import Order


cons: Console = Console()
# ---
APP_URL = "app_sprava_montazi"

# --- Autocomplete ---


class AutocompleteOrdersView(LoginRequiredMixin, View):
    def get(self, request):
        term = request.GET.get("term", "")
        zakazky = Order.objects.filter(order_number__icontains=term).values_list(
            "order_number", flat=True
        )[:10]

        send_to_autocomplete: list[str] = []
        for zakazka in zakazky:
            send_to_autocomplete.append(zakazka.upper())
        return JsonResponse({"orders": send_to_autocomplete})


class OrderStatusView(LoginRequiredMixin, View):
    def get(self, request):
        number = request.GET.get("order_number", "")
        try:
            order = Order.objects.get(order_number=number.lower())
            status = order.get_status_display()  # type:ignore
            return JsonResponse({"status": status}, status=200)
        except Order.DoesNotExist:
            return JsonResponse({"status": "Neznámé číslo zakázky"}, status=404)
