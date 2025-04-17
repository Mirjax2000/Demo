"""Model testy"""

from django.test import TestCase
from django.db import IntegrityError
from .models import DistribHub


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
