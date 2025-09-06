"""Serializer pro API"""

from rest_framework import serializers
from drf_spectacular.utils import extend_schema


# api status
class ApiStatusSerializer(serializers.Serializer):
    api_status = serializers.CharField()


# obsah do detailu v to co jde na update customera
class CustomerDetailSerializer(serializers.Serializer):
    name = serializers.CharField()
    zip_code = serializers.CharField()
    city = serializers.CharField(required=False, allow_blank=True)
    street = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)


# jedna objednavka co jde na update customers
class CustomerUpdateItemSerializer(serializers.Serializer):
    order_number = serializers.CharField()
    details = CustomerDetailSerializer()


# seznam co jde zpet na update customer
class OrderCustomerUpdateSerializer(serializers.Serializer):
    updates = CustomerUpdateItemSerializer(many=True)


# seznam nekompletnich zakazniku
class IncompleteCustomersSerializer(serializers.Serializer):
    order_numbers = serializers.ListField(
        child=serializers.CharField(),
    )


# jedna dopravni zakazka
class ZaterminovanaObjednavkaSerializer(serializers.Serializer):
    order_number = serializers.CharField()
    evidence_termin = serializers.DateField()


# seznam dopravnich zakazek
class ZaterminovaneObjednavkySerializer(serializers.Serializer):
    orders = ZaterminovanaObjednavkaSerializer(many=True)


# dopravni objednavky do stavu realized
class ZakazkyUpdateSerializer(serializers.Serializer):
    orders = serializers.ListField(
        child=serializers.CharField(),
    )
