"""app_sprava_montazi View"""

from rich.console import Console

# --- Django
from django.conf import settings
from django.contrib.auth import get_user_model

# API rest ---
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

# --- utils
from app_sprava_montazi.utils import update_customers

# --- modely z DB
from app_sprava_montazi.models import Order

# --- serializer
from .serializer import OrderCustomerUpdateSerializer

# --- 00P classes


cons: Console = Console()
User = get_user_model()


# Create your views here.
# --- API ---
class ApiStatusView(APIView):
    permission_classes = [IsAuthenticated]  # jen pro přihlášené uživatele

    def get(self, request) -> Response:
        message: dict = {"api_status": "UP"}
        return Response(message)


class IncompleteCustomersView(APIView):
    permission_classes = [IsAuthenticated]  # jen pro přihlášené uživatele

    def get(self, request) -> Response:
        qs = Order.objects.filter(client__incomplete=True).exclude(status="Hidden")
        seznam = [record.order_number.upper() for record in qs]
        if settings.DEBUG:
            cons.log(f"pocet nekompletnych klientu je: {len(seznam)}")
            cons.log(f"seznam nekompletnich klientu: {seznam}")
        return Response(seznam)


class CustomerUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderCustomerUpdateSerializer(data=request.data)
        if serializer.is_valid():
            updates = serializer.validated_data["updates"]  # type: ignore

            update_customers(updates)

            return Response({"message": "Zákazníci byli aktualizováni."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
