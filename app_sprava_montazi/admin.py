from django.contrib import admin

from .models import Order, Team


class OrderAdmin(admin.ModelAdmin):
    search_fields = [
        "order_number",
        "mandant",
        "customer_name",
    ]
    list_filter = ["status"]
    list_display = ["order_number", "mandant", "customer_name", "team_type", "team"]


class TeamAdmin(admin.ModelAdmin):
    search_fields = ["company", "city"]
    list_display = (
        "company",
        "city",
        "region",
        "active",
        "price_per_hour",
        "price_per_km",
    )


admin.site.register(Order, OrderAdmin)
admin.site.register(Team, TeamAdmin)
