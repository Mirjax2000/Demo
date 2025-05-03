"""Form testy"""

from django.test import TestCase
from .forms import ClientForm, DistribHubForm
from .models import DistribHub


class ClientFormTest(TestCase):
    def test_valid_data(self):
        """
        Testuje, zda formulář ClientForm je platný při zadání správných dat.
        """
        form = ClientForm(
            data={
                "name": "Jan Novák",
                "street": "Hlavní",
                "city": "Praha",
                "zip_code": "10000",
                "phone": "212345678",
                "email": "jan@example.com",
            }
        )
        print(form.errors)
        self.assertTrue(form.is_valid())

    def test_missing_required_field_name(self):
        """
        Testuje, zda formulář ClientForm je neplatny při zadání nesprávných dat.
        """
        form = ClientForm(
            data={
                "name": "",
                "street": "Hlavní",
                "city": "Praha",
                "zip_code": "10000",
                "phone": "212345678",
                "email": "jan@example.com",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertEqual(form.errors["name"][0], "Jméno je povinné!")

    def test_invalid_email_format(self):
        """
        Testuje, zda formulář ClientForm správně detekuje neplatný formát e-mailové adresy.
        """
        form = ClientForm(
            data={
                "name": "Jan Novák",
                "street": "Hlavní",
                "city": "Praha",
                "zip_code": "10000",
                "phone": "212345678",
                "email": "špatnýemail",  # neplatný e-mail
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_zip_code_required(self):
        """
        Testuje, že pole 'zip_code' je ve formuláři ClientForm povinné.
        """
        form = ClientForm(
            data={
                "name": "Jan Novák",
                "street": "Hlavní",
                "city": "Praha",
                "zip_code": "",  # chybí PSČ
                "phone": "212345678",
                "email": "jan@example.com",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("zip_code", form.errors)
        self.assertEqual(form.errors["zip_code"][0], "Jméno je povinné!")


class DistribHubFormTest(TestCase):
    def test_valid_form(self):
        """
        Testuje, zda je formulář DistribHubForm platný při zadání správných dat.
        """
        form = DistribHubForm(
            data={
                "code": "A01",
                "city": "Brno",
            }
        )
        self.assertTrue(form.is_valid())

    def test_missing_code(self):
        """
        Testuje, zda formulář DistribHubForm správně vyžaduje pole 'code'.
        """
        form = DistribHubForm(
            data={
                "code": "",
                "city": "Brno",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("code", form.errors)
        self.assertEqual(form.errors["code"][0], "Kod je povinný!")

    def test_code_too_long(self):
        """
        Testuje, zda formulář DistribHubForm správně detekuje příliš dlouhý kód.
        """
        form = DistribHubForm(
            data={
                "code": "ABCDE",  # moc dlouhé
                "city": "Brno",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("code", form.errors)

    def test_duplicate_code(self):
        """
        Testuje, zda formulář DistribHubForm správně detekuje duplicitní kód distribučního hubu.
        """
        DistribHub.objects.create(code="A01", city="Praha")
        form = DistribHubForm(
            data={
                "code": "A01",  # duplicitní
                "city": "Brno",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("code", form.errors)
        self.assertEqual(form.errors["code"][0], "Tento kod uz existuje!")

    def test_missing_city(self):
        """
        Testuje, zda formulář DistribHubForm správně detekuje chybějící hodnotu pole 'city'.
        """
        form = DistribHubForm(
            data={
                "code": "B01",
                "city": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("city", form.errors)
        self.assertEqual(form.errors["city"][0], "Jméno je povinné!")
