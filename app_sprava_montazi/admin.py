from django.contrib import admin

from .models import Order, Team, DistribHub, Upload, Client, Article


class OrderAdmin(admin.ModelAdmin):
    search_fields = [
        "order_number",
    ]
    list_filter = ["status"]
    list_display = [
        "order_number",
        "distrib_hub",
        "mandant",
        "client",
        "team_type",
        "team",
    ]
    list_per_page = 15


class DistribHubAdmin(admin.ModelAdmin):
    search_fields = ["code", "city"]
    list_display = ("slug", "code", "city")
    list_per_page = 15


class ClientAdmin(admin.ModelAdmin):
    search_fields = ["name", "email"]
    list_display = ("name", "street", "city", "zip_code", "incomplete")
    list_filter = ["incomplete"]

    list_per_page = 15


class TeamAdmin(admin.ModelAdmin):
    search_fields = ["name", "city"]
    list_display = ("name", "city", "active", "price_per_hour", "price_per_km")
    list_filter = ["active"]
    list_per_page = 15


class ArticleAdmin(admin.ModelAdmin):
    search_fields = ["name", "order"]
    list_display = (
        "order",
        "name",
        "price",
        "quantity",
    )
    list_per_page = 15


admin.site.register(DistribHub, DistribHubAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Upload)
