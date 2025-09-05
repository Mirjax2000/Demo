"""app_sprava_montazi View"""

from rich.console import Console

# --- Django
from django.conf import settings
from django.contrib.auth import get_user_model

# API rest ---
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.authtoken.models import Token

# --- utils
from app_sprava_montazi.utils import update_customers

# --- modely z DB
from app_sprava_montazi.models import Order, Status, TeamType

# --- serializer
from .serializer import OrderCustomerUpdateSerializer, ApiStatusSerializer
from .serializer import IncompleteCustomersSerializer
from .serializer import ZaterminovaneObjednavkySerializer

# --- 00P classes


cons: Console = Console()
User = get_user_model()


# Create your views here.
# --- API ---
class ApiStatusView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Status API",
        description="Vrací aktuální stav API, typicky 'UP'",
        responses={
            200: OpenApiResponse(
                response=ApiStatusSerializer,
                description="Aktuální stav API",
                examples=[
                    OpenApiExample(
                        "Příklad úspěšné odpovědi",
                        value={"api_status": "UP"},
                    )
                ],
            ),
            401: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Nebyly zadány přihlašovací údaje.",
                examples=[
                    OpenApiExample(
                        "NoCredentials",
                        value={"detail": "Nebyly zadány přihlašovací údaje."},
                    )
                ],
            ),
        },
    )
    def get(self, request) -> Response:
        return Response({"api_status": "UP"})


class IncompleteCustomersView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Seznam nekompletních zákazníků",
        description="Vrací seznam `order_number` všech klientů, kteří mají `incomplete=True` a nejsou `Hidden`",
        responses={
            200: OpenApiResponse(
                response=IncompleteCustomersSerializer,
                description="Seznam nekompletních zákazníků",
                examples=[
                    OpenApiExample(
                        "Příklad úspěšné odpovědi",
                        value={
                            "order_numbers": [
                                "709815789100523888-R",
                                "709815789100523889-R",
                                "709815789100523890-R",
                            ]
                        },
                    )
                ],
            ),
            401: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Nebyly zadány přihlašovací údaje.",
                examples=[
                    OpenApiExample(
                        "NoCredentials",
                        value={"detail": "Nebyly zadány přihlašovací údaje."},
                    )
                ],
            ),
        },
    )
    def get(self, request) -> Response:
        qs = Order.objects.filter(client__incomplete=True).exclude(status="Hidden")
        seznam = [record.order_number.upper() for record in qs]

        if settings.DEBUG:
            cons.log(f"Počet nekompletních klientů je: {len(seznam)}")
            cons.log(f"Seznam nekompletních klientů: {seznam}")

        return Response({"order_numbers": seznam})


class ZaterminovanoDopravouView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Seznam zaterminovaných objednávek dopravou",
        description="Vrací seznam `order_number` všech objednávek, které mají status `ADVICED` a `team_type` `BY_DELIVERY_CREW`.",
        responses={
            200: OpenApiResponse(
                response=ZaterminovaneObjednavkySerializer,
                description="Seznam dopravních objednávek",
                examples=[
                    OpenApiExample(
                        "Příklad úspěšné odpovědi",
                        value={
                            "order_numbers": [
                                "709815789100523888-R",
                                "709815789100523889-R",
                                "709815789100523890-R",
                            ]
                        },
                    )
                ],
            ),
            401: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Nebyly zadány přihlašovací údaje.",
                examples=[
                    OpenApiExample(
                        "NoCredentials",
                        value={"detail": "Nebyly zadány přihlašovací údaje."},
                    )
                ],
            ),
        },
    )
    def get(self, request) -> Response:
        qs = Order.objects.filter(
            status=Status.ADVICED, team_type=TeamType.BY_DELIVERY_CREW
        )
        seznam = [record.order_number.upper() for record in qs]

        if settings.DEBUG:
            cons.log(f"Počet zaterminovaných zakázek: {len(seznam)}")
            cons.log(f"Seznam zaterminovaných zakázek: {seznam}")

        return Response({"order_numbers": seznam})


class CustomerUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Aktualizace zákazníků",
        description="Přijímá seznam aktualizací zákazníků a aplikuje je.",
        request=OrderCustomerUpdateSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Zpráva o úspěšné aktualizaci",
                examples=[
                    OpenApiExample(
                        "Úspěšná aktualizace",
                        value={"message": "Zákazníci byli aktualizováni."},
                    )
                ],
            ),
            401: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Nebyly zadány přihlašovací údaje.",
                examples=[
                    OpenApiExample(
                        "NoCredentials",
                        value={"detail": "Nebyly zadány přihlašovací údaje."},
                    )
                ],
            ),
        },
    )
    def post(self, request):
        serializer = OrderCustomerUpdateSerializer(data=request.data)
        if serializer.is_valid():
            updates = serializer.validated_data["updates"]  # type: ignore
            update_customers(updates)
            return Response({"message": "Zákazníci byli aktualizováni."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
