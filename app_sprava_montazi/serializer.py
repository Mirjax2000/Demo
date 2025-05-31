from rest_framework import serializers


class CustomerDetailSerializer(serializers.Serializer):
    name = serializers.CharField()
    zip_code = serializers.CharField()
    city = serializers.CharField(required=False, allow_blank=True)
    street = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)


class OrderCustomerUpdateSerializer(serializers.Serializer):
    updates = serializers.ListField(
        child=serializers.DictField(child=serializers.JSONField())
    )
