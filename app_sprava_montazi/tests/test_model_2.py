"""Model testy"""

from datetime import date, timedelta, datetime
import tempfile

# --- django
from django.forms import ValidationError
from django.contrib.auth import get_user_model

from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.db import IntegrityError
from django.utils.text import slugify
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

# --- modely
from ..models import AppSetting, Order, OrderMontazImage, Status, DistribHub, Client
from ..models import TeamType

User = get_user_model()


class SettingsModelTest(TestCase):
    def setUp(self):
        self.data = {"price": 10, "minPrice": 5, "maxPrice": 15}
        self.name: str = "appSettings"
        self.app_settings = AppSetting.objects.create(
            name=self.name,
            data=self.data,
        )

    def test_model_field_types(self) -> None:
        """Ověří, že pole jsou typu Charfiled a Jsonfield."""
        name = AppSetting._meta.get_field("name")
        data = AppSetting._meta.get_field("data")
        self.assertIsInstance(name, models.CharField)
        self.assertIsInstance(data, models.JSONField)

    def test_appsettings_creation(self):
        app_settings = self.app_settings
        self.assertTrue(isinstance(app_settings, AppSetting))
        self.assertEqual(app_settings.name, self.name)
        self.assertEqual(app_settings.data, self.data)

        # Ověření jednotlivých klíčů a hodnot
        self.assertEqual(app_settings.data["price"], 10)
        self.assertEqual(app_settings.data["minPrice"], 5)
        self.assertEqual(app_settings.data["maxPrice"], 15)

    def test_empty_data_allowed(self):
        setting = AppSetting.objects.create(name="emptyData", data={})
        self.assertEqual(setting.data, {})

    def test_unique_name_constraint(self):
        # vytvoříme první záznam
        AppSetting.objects.create(name="setting1", data={"key": "value"})

        # při vytvoření druhého se stejným jménem by měla přijít chyba
        with self.assertRaises(IntegrityError):
            AppSetting.objects.create(name="setting1", data={"key2": "value2"})

    def test_update_setting(self):
        # Změníme data a uložíme
        self.app_settings.data = {"new_key": "new_value"}
        self.app_settings.save()

        updated = AppSetting.objects.get(pk=self.app_settings.pk)
        self.assertEqual(updated.data, {"new_key": "new_value"})

    def test_delete_setting(self):
        # Smažeme záznam
        self.app_settings.delete()

        # Otestujeme, že už neexistuje v DB
        exists = AppSetting.objects.filter(pk=self.app_settings.pk).exists()
        self.assertFalse(exists)


@override_settings(MEDIA_ROOT=tempfile.gettempdir())  # testovací složka
class OrderMontazImageTest(TestCase):
    def setUp(self):
        self.hub = DistribHub.objects.create(code="111", city="Praha")
        self.customer = Client.objects.create(name="Pedro Pascal", zip_code="12345")
        self.order = Order.objects.create(
            order_number="ORDER-TEST-ADVICED",
            distrib_hub=self.hub,
            mandant="SCCZ",
            client=self.customer,
            status=Status.ADVICED,
            delivery_termin=timezone.now().date(),
            evidence_termin=timezone.now().date(),
            team_type=TeamType.BY_DELIVERY_CREW,
            notes="zaterminovano s dopravou",
        )

    def test_image_upload_path(self):
        # připravíme testovací soubor
        test_image = SimpleUploadedFile(
            "test.jpg", b"file_content", content_type="image/jpeg"
        )

        # vytvoříme instanci modelu
        image_instance = OrderMontazImage.objects.create(
            order=self.order,
            image=test_image,
            position=1,
        )

        # kontrola, že se soubor ukládá do správné složky
        expected_prefix = f"montage_images/{self.order.order_number.upper()}/test"
        self.assertTrue(
            image_instance.image.name.startswith(expected_prefix),
            f"Soubor by měl začínat '{expected_prefix}', ale je '{image_instance.image.name}'",
        )

        # volitelně: kontrola, že soubor existuje fyzicky (v testovací temp složce)
        self.assertTrue(image_instance.image.storage.exists(image_instance.image.name))
