"""Model testy"""

from django.test import TestCase
from django.db import IntegrityError
from .models import DistribHub, Order, Team, TeamType


class DistribHubModelTest(TestCase):
    def setUp(self):
        self.hub = DistribHub.objects.create(code="111", city="Praha")

    def test_slug_is_generated_correctly(self):
        """
        Testuje správné generování slug hodnoty pro Hub objekt.
        """
        self.assertEqual(self.hub.slug, "111-praha")

    def test_slug_and_code_are_unique(self):
        """
        Test na kontrolu unikátnosti kódu distribučního hubu.
        """
        with self.assertRaises(IntegrityError):
            DistribHub.objects.create(code="111", city="Praha")
            DistribHub.objects.create(code="111", city="Praha-1")

    def test_slug_with_special_characters(self):
        """Test správného vytvoření slug hodnoty obsahující diakritiku."""
        special = DistribHub.objects.create(code="222", city="České Budějovice")
        self.assertEqual(special.slug, "222-ceske-budejovice")


class OrderModelTest(TestCase):
    def setUp(self):
        # Základní DistribHub pro testy
        self.hub = DistribHub.objects.create(code="111", city="Praha")

    def test_is_missing_team_true(self):
        """Test kdyz team je None tak vrat True."""
        order = Order.objects.create(
            order_number="703777143100437749-R",
            distrib_hub=self.hub,
            mandant="1234",
            team_type=TeamType.BY_ASSEMBLY_CREW,
            team=None,
        )
        self.assertTrue(order.is_missing_team())

    def test_is_missing_team_false_with_team(self):
        """Test kdyz team je 'Company' tak vrat False."""
        team = Team.objects.create(
            name="Ferda comp",
            city="Praha",
            phone="+420123456789",
        )
        order = Order.objects.create(
            order_number="703777143100437750-R",
            distrib_hub=self.hub,
            mandant="1234",
            team_type=TeamType.BY_ASSEMBLY_CREW,
            team=team,
        )
        self.assertFalse(order.is_missing_team())

    def test_is_missing_team_false_with_other_type(self):
        """Test kdyz team je None ale team type je mimo montazni team."""
        order = Order.objects.create(
            order_number="703777143100437751-R",
            distrib_hub=self.hub,
            mandant="1234",
            team_type=TeamType.BY_CUSTOMER,
            team=None,
        )
        self.assertFalse(order.is_missing_team())
