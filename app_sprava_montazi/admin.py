from django.contrib import admin

from .models import Order, Team, DistribHub


# class OrderAdmin(admin.ModelAdmin):
#     search_fields = ["order_number"]
#     list_filter = ["status"]
#     list_display = ["order_number", "distrib_hub", "mandant", "team_type", "team"]


# class TeamAdmin(admin.ModelAdmin):
#     search_fields = ["name", "city"]
#     list_filter = ["active"]
#     list_display = (
#         "name",
#         "city",
#         "region",
#         "active",
#         "price_per_hour",
#         "price_per_km",
#     )
class DistribHubAdmin(admin.ModelAdmin):
    search_fields = ["code", "city"]
    list_display = ("slug", "code", "city")


admin.site.register(Order)
admin.site.register(DistribHub, DistribHubAdmin)
# admin.site.register(Team)
