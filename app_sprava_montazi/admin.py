from django.contrib import admin

from .models import Order, Team


class OrderAdmin(admin.ModelAdmin):
    search_fields = ["order_number"]
    list_filter = ["status"]
    list_display = ["order_number", "distrib_hub", "mandant", "team_type", "team"]


class TeamAdmin(admin.ModelAdmin):
    search_fields = ["name", "city"]
    list_filter = ["active"]
    list_display = (
        "name",
        "city",
        "region",
        "active",
        "price_per_hour",
        "price_per_km",
    )


admin.site.register(Order, OrderAdmin)
admin.site.register(Team, TeamAdmin)
