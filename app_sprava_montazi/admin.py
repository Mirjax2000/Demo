from django.contrib import admin

from .models import (
    Order,
    Team,
    DistribHub,
    Upload,
    Client,
    Article,
    CallLog,
    OrderPDFStorage,
)
from simple_history.admin import SimpleHistoryAdmin


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


class CallLogAdmin(admin.ModelAdmin):
    list_display = ("client", "called_at", "was_successful")
    fields = ("client", "called_at", "was_successful", "note")
    readonly_fields = ("called_at",)
    list_filter = ["was_successful"]
    list_per_page = 15


class OrderHistoryAdmin(SimpleHistoryAdmin, OrderAdmin):
    pass


class DistribHubHistoryAdmin(SimpleHistoryAdmin, DistribHubAdmin):
    pass


class ClientHistoryAdmin(SimpleHistoryAdmin, ClientAdmin):
    pass


class TeamHistoryAdmin(SimpleHistoryAdmin, TeamAdmin):
    pass


class ArticleHistoryAdmin(SimpleHistoryAdmin, ArticleAdmin):
    pass


class CallLogHistoryAdmin(SimpleHistoryAdmin, CallLogAdmin):
    pass


admin.site.register(DistribHub, DistribHubHistoryAdmin)
admin.site.register(Client, ClientHistoryAdmin)
admin.site.register(Order, OrderHistoryAdmin)
admin.site.register(Team, TeamHistoryAdmin)
admin.site.register(Article, ArticleHistoryAdmin)
admin.site.register(Upload, SimpleHistoryAdmin)  # Pro model bez vlastní Admin třídy
admin.site.register(CallLog, CallLogHistoryAdmin)
admin.site.register(OrderPDFStorage)
