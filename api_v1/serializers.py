"""
API v1 Serializers — kompletní serializátory pro oddělený FE/BE.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from app_sprava_montazi.models import (
    Article,
    AppSetting,
    CallLog,
    Client,
    DistribHub,
    FinanceCostItem,
    FinanceRevenueItem,
    Order,
    OrderBackProtocol,
    OrderMontazImage,
    OrderPDFStorage,
    Team,
    Upload,
)

User = get_user_model()


# ──────────────────────────────────────────
# Auth
# ──────────────────────────────────────────
class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "is_staff", "role"]
        read_only_fields = ["id", "is_staff", "role"]

    def get_role(self, obj) -> str:
        from api_v1.permissions import get_user_role
        return get_user_role(obj)


class UserAdminSerializer(serializers.ModelSerializer):
    """Serializer pro admin správu uživatelů — umožňuje změnu role a aktivace."""

    role = serializers.SerializerMethodField(read_only=True)
    group = serializers.ChoiceField(
        choices=["Admin", "Manager", "Operator", "ReadOnly"],
        write_only=True,
        required=False,
    )

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "is_active", "is_staff", "date_joined", "last_login",
            "role", "group",
        ]
        read_only_fields = ["id", "username", "date_joined", "last_login", "role"]

    def get_role(self, obj) -> str:
        from api_v1.permissions import get_user_role
        return get_user_role(obj)

    def update(self, instance, validated_data):
        from django.contrib.auth.models import Group
        group_name = validated_data.pop("group", None)
        instance = super().update(instance, validated_data)
        if group_name:
            # Odeber ze všech RBAC skupin a přidej do nové
            rbac_groups = Group.objects.filter(name__in=["Admin", "Manager", "Operator", "ReadOnly"])
            instance.groups.remove(*rbac_groups)
            new_group, _ = Group.objects.get_or_create(name=group_name)
            instance.groups.add(new_group)
        return instance


class UserAdminCreateSerializer(serializers.ModelSerializer):
    """Serializer pro vytvoření nového uživatele adminem."""

    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    group = serializers.ChoiceField(
        choices=["Admin", "Manager", "Operator", "ReadOnly"],
        write_only=True,
    )
    role = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "is_active", "password", "password2", "group",
            "role", "date_joined", "last_login",
        ]
        read_only_fields = ["id", "date_joined", "last_login", "role"]

    def get_role(self, obj) -> str:
        from api_v1.permissions import get_user_role
        return get_user_role(obj)

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password2": "Hesla se neshodují."})
        if User.objects.filter(username=data["username"]).exists():
            raise serializers.ValidationError({"username": "Uživatel s tímto jménem již existuje."})
        return data

    def create(self, validated_data):
        from django.contrib.auth.models import Group

        validated_data.pop("password2")
        group_name = validated_data.pop("group")
        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data,
        )
        new_group, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(new_group)
        return user


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2"]

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password2": "Hesla se neshodují."})
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        user.is_staff = False
        user.is_superuser = False
        user.save()
        return user


# ──────────────────────────────────────────
# DistribHub
# ──────────────────────────────────────────
class DistribHubSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()

    class Meta:
        model = DistribHub
        fields = ["id", "code", "city", "slug", "label"]
        read_only_fields = ["id", "slug"]

    def get_label(self, obj) -> str:
        return str(obj)


# ──────────────────────────────────────────
# Team
# ──────────────────────────────────────────
class TeamListSerializer(serializers.ModelSerializer):
    """Zjednodušený serializátor pro seznam/výběr."""

    class Meta:
        model = Team
        fields = [
            "id",
            "name",
            "city",
            "region",
            "phone",
            "email",
            "active",
            "slug",
        ]
        read_only_fields = ["id", "slug"]


class TeamDetailSerializer(serializers.ModelSerializer):
    """Plný serializátor s cenami a poznámkami."""

    class Meta:
        model = Team
        fields = [
            "id",
            "name",
            "city",
            "region",
            "phone",
            "email",
            "active",
            "price_per_hour",
            "price_per_km",
            "notes",
            "slug",
        ]
        read_only_fields = ["id", "slug"]

    def validate_name(self, value: str) -> str:
        """Kontrola unikátnosti slug generovaného z name."""
        from django.utils.text import slugify

        new_slug = slugify(value)
        qs = Team.objects.filter(slug=new_slug)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                f"Tým s názvem generujícím slug '{new_slug}' již existuje."
            )
        return value


# ──────────────────────────────────────────
# Client
# ──────────────────────────────────────────
class ClientListSerializer(serializers.ModelSerializer):
    formatted_phone = serializers.SerializerMethodField()
    formatted_psc = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            "id",
            "name",
            "street",
            "city",
            "zip_code",
            "phone",
            "email",
            "incomplete",
            "slug",
            "formatted_phone",
            "formatted_psc",
            "consent_given",
            "consent_date",
            "data_retention_until",
            "is_anonymized",
        ]
        read_only_fields = ["id", "slug", "incomplete", "is_anonymized"]

    @staticmethod
    def _mask_phone(value: str) -> str:
        """Show last 4 chars, mask the rest: '***456789' → '******789'."""
        if not value or len(value) <= 4:
            return value or ""
        return "*" * (len(value) - 4) + value[-4:]

    @staticmethod
    def _mask_email(value: str) -> str:
        """Mask email: 'jan.novak@email.cz' → 'j***k@email.cz'."""
        if not value or "@" not in value:
            return value or ""
        local, domain = value.rsplit("@", 1)
        if len(local) <= 2:
            masked_local = local[0] + "***" if local else "***"
        else:
            masked_local = local[0] + "***" + local[-1]
        return f"{masked_local}@{domain}"

    def get_phone(self, obj) -> str:
        return self._mask_phone(obj.phone)

    def get_email(self, obj) -> str:
        return self._mask_email(obj.email)

    def get_formatted_phone(self, obj) -> str:
        return self._mask_phone(obj.format_phone())

    def get_formatted_psc(self, obj) -> str:
        return obj.format_psc()

    def validate_zip_code(self, value: str) -> str:
        """PSČ musí být přesně 5 číslic."""
        value = value.strip()
        if not value.isdigit() or len(value) != 5:
            raise serializers.ValidationError("PSČ musí být přesně 5 číslic.")
        return value


# ──────────────────────────────────────────
# CallLog  (must be defined before ClientDetailSerializer)
# ──────────────────────────────────────────
class CallLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)
    client_name = serializers.CharField(source="client.name", read_only=True)

    class Meta:
        model = CallLog
        fields = [
            "id",
            "client",
            "client_name",
            "user",
            "user_name",
            "called_at",
            "note",
            "was_successful",
        ]
        read_only_fields = ["id", "called_at"]


class ClientDetailSerializer(ClientListSerializer):
    """Client s vazbou na zakázky — reálné phone/email (pro dispečery)."""

    # Override SerializerMethodField → normální CharField → zapisovatelné + nemaskované
    phone = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    formatted_phone = serializers.SerializerMethodField()

    order_count = serializers.SerializerMethodField()
    call_logs = CallLogSerializer(many=True, read_only=True, source="calls")

    class Meta(ClientListSerializer.Meta):
        fields = ClientListSerializer.Meta.fields + ["order_count", "call_logs"]

    def get_formatted_phone(self, obj) -> str:
        """Detail zobrazuje reálný formátovaný telefon (bez maskování)."""
        return obj.format_phone()

    def get_order_count(self, obj) -> int:
        return obj.order_set.count()


# ──────────────────────────────────────────
# Article (inline k Order)
# ──────────────────────────────────────────
class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["id", "name", "quantity", "note"]
        read_only_fields = ["id"]


# ──────────────────────────────────────────
# Finance items
# ──────────────────────────────────────────
class FinanceRevenueItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinanceRevenueItem
        fields = ["id", "order", "description", "amount", "created", "updated"]
        read_only_fields = ["id", "created", "updated"]


class FinanceCostItemSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source="team.name", read_only=True, default=None)

    class Meta:
        model = FinanceCostItem
        fields = [
            "id",
            "order",
            "team",
            "team_name",
            "description",
            "amount",
            "carrier_confirmed",
            "created",
            "updated",
        ]
        read_only_fields = ["id", "created", "updated"]


# ──────────────────────────────────────────
# Order PDF / Images / BackProtocol
# ──────────────────────────────────────────
class OrderPDFStorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderPDFStorage
        fields = ["id", "team", "file", "created"]
        read_only_fields = ["id", "created"]


class OrderMontazImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderMontazImage
        fields = ["id", "position", "created", "alt_text", "image"]
        read_only_fields = ["id", "created"]


class OrderBackProtocolSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderBackProtocol
        fields = ["id", "file", "alt_text", "created"]
        read_only_fields = ["id", "created"]


# ──────────────────────────────────────────
# Order
# ──────────────────────────────────────────
class OrderListSerializer(serializers.ModelSerializer):
    """Serializátor pro seznam zakázek (tabulka)."""

    client_name = serializers.CharField(source="client.name", read_only=True, default=None)
    client_incomplete = serializers.BooleanField(
        source="client.incomplete", read_only=True, default=None
    )
    team_name = serializers.CharField(source="team.name", read_only=True, default=None)
    distrib_hub_label = serializers.SerializerMethodField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    team_type_display = serializers.CharField(source="get_team_type_display", read_only=True)
    has_pdf = serializers.SerializerMethodField()
    has_back_protocol = serializers.SerializerMethodField()
    montage_images_count = serializers.SerializerMethodField()
    profit = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "mandant",
            "status",
            "status_display",
            "team_type",
            "team_type_display",
            # FK info
            "distrib_hub",
            "distrib_hub_label",
            "client",
            "client_name",
            "client_incomplete",
            "team",
            "team_name",
            # termíny
            "evidence_termin",
            "delivery_termin",
            "montage_termin",
            # finance
            "naklad",
            "vynos",
            "profit",
            # příznaky
            "has_pdf",
            "has_back_protocol",
            "montage_images_count",
            # meta
            "notes",
            "mail_datum_sended",
            "mail_team_sended",
        ]

    def get_distrib_hub_label(self, obj) -> str:
        return str(obj.distrib_hub) if obj.distrib_hub else ""

    def get_has_pdf(self, obj) -> bool:
        return hasattr(obj, "pdf") and obj.pdf is not None

    def get_has_back_protocol(self, obj) -> bool:
        return hasattr(obj, "back_protocol") and obj.back_protocol is not None

    def get_montage_images_count(self, obj) -> int:
        return obj.montage_images.count()

    def get_profit(self, obj) -> str:
        return str(obj.profit())


class OrderDetailSerializer(OrderListSerializer):
    """Plný detailní serializátor s vnořenými daty."""

    articles = ArticleSerializer(many=True, read_only=True)
    client_detail = ClientListSerializer(source="client", read_only=True)
    team_detail = TeamListSerializer(source="team", read_only=True)
    distrib_hub_detail = DistribHubSerializer(source="distrib_hub", read_only=True)
    pdf = OrderPDFStorageSerializer(read_only=True)
    back_protocol = OrderBackProtocolSerializer(read_only=True)
    montage_images = OrderMontazImageSerializer(many=True, read_only=True)
    revenue_items = FinanceRevenueItemSerializer(many=True, read_only=True)
    cost_items = FinanceCostItemSerializer(many=True, read_only=True)

    class Meta(OrderListSerializer.Meta):
        fields = OrderListSerializer.Meta.fields + [
            "articles",
            "client_detail",
            "team_detail",
            "distrib_hub_detail",
            "pdf",
            "back_protocol",
            "montage_images",
            "revenue_items",
            "cost_items",
        ]


class OrderWriteSerializer(serializers.ModelSerializer):
    """Serializátor pro vytvoření/úpravu zakázky."""

    articles = ArticleSerializer(many=True, required=False)
    client_data = serializers.DictField(required=False, write_only=True)

    class Meta:
        model = Order
        fields = [
            "order_number",
            "mandant",
            "status",
            "team_type",
            "distrib_hub",
            "client",
            "team",
            "evidence_termin",
            "delivery_termin",
            "montage_termin",
            "naklad",
            "vynos",
            "notes",
            "articles",
            "client_data",
        ]
        extra_kwargs = {
            "client": {"required": False, "allow_null": True},
        }

    def validate_order_number(self, value):
        value = value.upper()
        qs = Order.objects.filter(order_number__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Objednávka už existuje!")
        return value

    def validate(self, data):
        """Server-side Adviced validation matching Django OrderForm.validate_adviced()."""
        # For partial update, merge with existing instance values
        status_val = data.get("status", getattr(self.instance, "status", None))
        team_type = data.get("team_type", getattr(self.instance, "team_type", None))

        if status_val == "Adviced":
            if team_type == "By_customer":
                raise serializers.ValidationError(
                    {"status": "Zákazník realizuje sám — nelze zatermínovat."}
                )

            client_val = data.get("client", getattr(self.instance, "client", None))
            delivery = data.get(
                "delivery_termin",
                getattr(self.instance, "delivery_termin", None),
            )
            vynos = data.get("vynos", getattr(self.instance, "vynos", None))
            naklad = data.get("naklad", getattr(self.instance, "naklad", None))

            errs: dict[str, str] = {}

            if not client_val and not data.get("client_data"):
                errs["client"] = "Vyžadován zákazník."
            elif client_val and getattr(client_val, "incomplete", False):
                errs["client"] = "Zákazník má neúplné údaje, nelze zatermínovat."
            if not delivery:
                errs["delivery_termin"] = "Vyžadován termín doručení."
            if not vynos or float(vynos) <= 0:
                errs["vynos"] = "Vyžadován výnos > 0."
            if not naklad or float(naklad) <= 0:
                errs["naklad"] = "Vyžadován náklad > 0."

            if team_type == "By_assembly_crew":
                team_val = data.get("team", getattr(self.instance, "team", None))
                montage = data.get(
                    "montage_termin",
                    getattr(self.instance, "montage_termin", None),
                )
                if not team_val:
                    errs["team"] = "Vyžadován tým."
                if not montage:
                    errs["montage_termin"] = "Vyžadován termín montáže."

            if team_type == "By_delivery_crew":
                # Delivery orders must NOT have team or montage_termin
                team_val = data.get("team", getattr(self.instance, "team", None))
                montage = data.get(
                    "montage_termin",
                    getattr(self.instance, "montage_termin", None),
                )
                if team_val:
                    errs["team"] = "Dopravní zakázka nesmí mít přiřazený tým."
                if montage:
                    errs["montage_termin"] = "Dopravní zakázka nesmí mít termín montáže."

            if errs:
                raise serializers.ValidationError(errs)

        return data

    def _resolve_client(self, validated_data):
        """Handle client_data → get_or_create, matching Django's client_created()."""
        client_data = validated_data.pop("client_data", None)
        if client_data and not validated_data.get("client"):
            name = client_data.get("name", "").strip()
            zip_code = client_data.get("zip_code", "").strip()
            if name and zip_code:
                from django.db import transaction
                with transaction.atomic():
                    client, created = Client.objects.get_or_create(
                        name=name,
                        zip_code=zip_code,
                        defaults={
                            "street": client_data.get("street", ""),
                            "city": client_data.get("city", ""),
                            "phone": client_data.get("phone", ""),
                            "email": client_data.get("email", ""),
                        },
                    )
                    if not created:
                        updated = False
                        for field in ["street", "city", "phone", "email"]:
                            value = client_data.get(field, "")
                            if value and getattr(client, field) != value:
                                setattr(client, field, value)
                                updated = True
                        if updated:
                            client.save()
                validated_data["client"] = client
        return validated_data

    def create(self, validated_data):
        validated_data = self._resolve_client(validated_data)
        articles_data = validated_data.pop("articles", [])
        order = Order.objects.create(**validated_data)
        for article_data in articles_data:
            Article.objects.create(order=order, **article_data)
        return order

    def update(self, instance, validated_data):
        validated_data.pop("client_data", None)  # client_data ignored on update
        articles_data = validated_data.pop("articles", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if articles_data is not None:
            # Per-article CRUD: update existing, create new, delete missing
            existing_ids = set()
            for article_data in articles_data:
                art_id = article_data.get("id")
                if art_id:
                    existing_ids.add(art_id)
                    Article.objects.filter(pk=art_id, order=instance).update(**{
                        k: v for k, v in article_data.items() if k != "id"
                    })
                else:
                    Article.objects.create(order=instance, **article_data)
            # Delete articles not in payload
            instance.articles.exclude(pk__in=existing_ids).delete()

        return instance


# ──────────────────────────────────────────
# Upload (CSV import)
# ──────────────────────────────────────────
class UploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Upload
        fields = ["id", "file", "created"]
        read_only_fields = ["id", "created"]


# ──────────────────────────────────────────
# Dashboard (read-only aggregáty)
# ──────────────────────────────────────────
class DashboardSerializer(serializers.Serializer):
    open_orders = serializers.DictField()
    closed_orders = serializers.DictField()
    adviced_type_orders = serializers.DictField()
    count_all = serializers.IntegerField()
    hidden = serializers.IntegerField()
    no_montage_term_count = serializers.IntegerField()
    no_montage_total_count = serializers.IntegerField()
    has_no_montage_term = serializers.BooleanField()
    is_invalid = serializers.BooleanField()
    invalid_count = serializers.IntegerField()
    finance_summary = serializers.DictField()
    new_issues_count = serializers.IntegerField()
    customer_r_count = serializers.IntegerField()
    new_issues_orders = OrderListSerializer(many=True, read_only=True)
    customer_r_orders = OrderListSerializer(many=True, read_only=True)
    mandant_options = serializers.ListField(child=serializers.CharField())
    year_options = serializers.ListField(child=serializers.IntegerField())


# ──────────────────────────────────────────
# AppSetting
# ──────────────────────────────────────────
class AppSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppSetting
        fields = ["id", "name", "data"]
        read_only_fields = ["id"]
