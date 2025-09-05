"""Serializer pro API"""

from rest_framework import serializers
from drf_spectacular.utils import extend_schema


class CustomerDetailSerializer(serializers.Serializer):
    name = serializers.CharField()
    zip_code = serializers.CharField()
    city = serializers.CharField(required=False, allow_blank=True)
    street = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)


class CustomerUpdateItemSerializer(serializers.Serializer):
    order_number = serializers.CharField()
    details = CustomerDetailSerializer()  # <-- tady ukáže všechna pole


class OrderCustomerUpdateSerializer(serializers.Serializer):
    updates = CustomerUpdateItemSerializer(many=True)


class IncompleteCustomersSerializer(serializers.Serializer):
    order_numbers = serializers.ListField(
        child=serializers.CharField(),
        help_text="Seznam order_number všech nekompletních klientů",
    )


class ZaterminovaneObjednavkySerializer(serializers.Serializer):
    orders = serializers.ListField(
        child=serializers.CharField(),
        help_text="Seznam číslel zakázek zaterminovaných dopravou",
    )


class ApiStatusSerializer(serializers.Serializer):
    api_status = serializers.CharField()
