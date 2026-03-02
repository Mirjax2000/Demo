"""django admin"""

from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

# --- models
from .models import Order, Team, DistribHub, Upload, Client, Article, CallLog
from .models import OrderPDFStorage, OrderBackProtocol, OrderBackProtocolToken
from .models import AppSetting, OrderMontazImage, DataRetentionPolicy


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
    list_display = ("name", "street", "city", "zip_code", "incomplete", "is_anonymized", "consent_given")
    list_filter = ["incomplete", "is_anonymized", "consent_given"]
    list_per_page = 15
    readonly_fields = ("is_anonymized",)


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
        "quantity",
    )
    list_per_page = 15


class CallLogAdmin(admin.ModelAdmin):
    list_display = ("client", "called_at", "was_successful")
    fields = ("client", "called_at", "was_successful", "note")
    readonly_fields = ("called_at",)
    list_filter = ["was_successful"]
    list_per_page = 15


class OrderBackProtocolTokenAdmin(admin.ModelAdmin):
    list_display = ("order", "token", "created")
    readonly_fields = ("token", "created")
    search_fields = ("order__order_number", "token")
    ordering = ("-created",)


class OrderMontazImageAdmin(admin.ModelAdmin):
    list_display = ("order", "position", "created", "alt_text", "image")
    search_fields = ("order__order_number",)
    readonly_fields = ("created",)
    ordering = ("-created",)


class OrderBackProtocolAdmin(admin.ModelAdmin):
    list_display = ("order", "alt_text")
    search_fields = ("order__order_number",)
    readonly_fields = ("created",)
    ordering = ("-created",)


class OrderHistoryAdmin(SimpleHistoryAdmin, OrderAdmin):
    pass


class OrderMontazImageHistoryAdmin(SimpleHistoryAdmin, OrderMontazImageAdmin):
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


class AppSettingHistoryAdmin(SimpleHistoryAdmin):
    pass


admin.site.register(AppSetting, AppSettingHistoryAdmin)
admin.site.register(DistribHub, DistribHubHistoryAdmin)
admin.site.register(OrderMontazImage, OrderMontazImageHistoryAdmin)
admin.site.register(Client, ClientHistoryAdmin)
admin.site.register(Order, OrderHistoryAdmin)
admin.site.register(Team, TeamHistoryAdmin)
admin.site.register(Article, ArticleHistoryAdmin)
admin.site.register(Upload, SimpleHistoryAdmin)
admin.site.register(CallLog, CallLogHistoryAdmin)
admin.site.register(OrderPDFStorage)
admin.site.register(OrderBackProtocol, OrderBackProtocolAdmin)
admin.site.register(OrderBackProtocolToken, OrderBackProtocolTokenAdmin)


@admin.register(DataRetentionPolicy)
class DataRetentionPolicyAdmin(admin.ModelAdmin):
    list_display = ("name", "retention_days", "is_active", "auto_anonymize", "updated")
    list_filter = ["is_active", "auto_anonymize"]
    readonly_fields = ("created", "updated")
