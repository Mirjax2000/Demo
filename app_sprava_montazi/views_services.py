"""servisni views"""

import secrets
from rich.console import Console

# --- Django
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse


# --- modely z DB
from .models import Order, OrderBackProtocolToken

# --- OOP classes
from .OOP_emails import CustomEmail

cons: Console = Console()
# ---
APP_URL = "app_sprava_montazi"


# --- Emails ---
class SendMailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        order: Order = get_object_or_404(Order, pk=pk)
        # ---
        token_obj, _ = OrderBackProtocolToken.objects.get_or_create(order=order)
        if not token_obj.token:
            token_obj.token = secrets.token_urlsafe(16)
            token_obj.save()

        back_url = request.build_absolute_uri(
            reverse("back_protocol", kwargs={"pk": pk}) + f"?token={token_obj.token}"
        )
        # ---
        email: CustomEmail = CustomEmail(pk=pk, back_url=back_url, user=request.user)
        try:
            email.send_email_with_encrypted_pdf()
            order.mail_datum_sended = timezone.now()
            order.save()
            messages.success(
                request,
                (
                    f"Email pro montazni tym: <strong>{order.team}</strong> "
                    f"na adresu <strong>{order.team.email}</strong> byl odeslan."  # type:ignore
                ),
            )
        except Exception as e:  # pylint: disable=broad-exception-caught
            messages.error(
                request,
                (
                    f"Email pro montazni tym: <strong>{order.team}</strong> "
                    f"na adresu <strong>{order.team.email}</strong> "  # type: ignore
                    f"nebyl odeslan, Chyba {str(e)}"
                ),
            )

        return redirect("protocol", pk=pk)


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
