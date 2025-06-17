from unittest.mock import MagicMock, patch

from django.conf import settings
from django.test import TestCase

from app_sprava_montazi.OOP_protokols import PdfConfig, Section, Utility

if not settings.configured:
    settings.configure(BASE_DIR="/tmp", DEBUG=True)


class MontageCalculationTests(TestCase):
    def setUp(self):
        # Initialize PdfConfig and mock Canvas for Utility and Section
        self.cfg = PdfConfig()
        self.mock_canvas = MagicMock()
        self.mock_buffer = MagicMock()
        self.utility = Utility(self.cfg, self.mock_canvas, self.mock_buffer)

        # Patch Utility's font_register to prevent actual font loading during tests
        with patch.object(Utility, "font_register"):
            self.section = Section(
                MagicMock()
            )  # Section expects a PdfGenerator instance
            self.section.cfg = self.cfg
            self.section.cvs = self.mock_canvas
            self.section.utils = self.utility

        self.patcher_draw_txt = patch.object(self.utility, "draw_txt")
        self.patcher_x_offset_length_2f = patch.object(
            self.utility,
            "x_offset_length_2f",
            side_effect=lambda num: (f"{num:.2f}", 10.0),
        )
        self.patcher_x_offset_length_0f = patch.object(
            self.utility, "x_offset_length_0f", side_effect=lambda num: (str(num), 10.0)
        )

        self.mock_draw_txt = self.patcher_draw_txt.start()
        self.mock_x_offset_length_2f = self.patcher_x_offset_length_2f.start()
        self.mock_x_offset_length_0f = self.patcher_x_offset_length_0f.start()

    def tearDown(self):
        self.patcher_draw_txt.stop()
        self.patcher_x_offset_length_2f.stop()
        self.patcher_x_offset_length_0f.stop()

    def create_mock_article(self, price=None, quantity=1, is_sofa=False):
        article = MagicMock()
        article.price = price
        article.quantity = quantity
        article.is_sofa = is_sofa
        return article

    def test_montage_calculation_no_articles(self):
        mock_order = MagicMock()
        mock_order.articles.all.return_value = []

        km = 0
        zona = 0
        result = self.section.montage_calculation(mock_order, km=km, zona=zona)

        expected_goods_value = 0
        expected_sofa_count = 0
        expected_percentage_value = 0
        expected_price_with_sofa = 0
        # When no articles, price should be minimal price
        expected_price = self.cfg.montage_minimal_price
        expected_total_price = expected_price + zona  # 454 + 0 = 454

        self.assertEqual(result["goods_value"], expected_goods_value)
        self.assertEqual(result["sofa_count"], expected_sofa_count)
        self.assertEqual(result["percentage_value"], expected_percentage_value)
        self.assertEqual(result["price_with_sofa"], expected_price_with_sofa)
        self.assertEqual(result["total_price"], expected_total_price)

        # Assert specific draw_txt calls
        self.mock_draw_txt.assert_any_call(
            text=f"{zona:.2f}",  # Should be 0.00
            x_offset=520 - 10.0,
            y_offset=283,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_goods_value:.2f}",
            x_offset=425 - 10.0,
            y_offset=331,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_percentage_value:.2f}",
            x_offset=520 - 10.0,
            y_offset=331,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_sofa_count}",
            x_offset=420 - 10.0,
            y_offset=354,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_price_with_sofa:.2f}",
            x_offset=520 - 10.0,
            y_offset=354,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_total_price:.2f}",
            x_offset=520 - 10.0,
            y_offset=622,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )

    def test_montage_calculation_no_articles_zona_1(self):
        mock_order = MagicMock()
        mock_order.articles.all.return_value = []

        km = 0
        zona = self.cfg.zone_1
        result = self.section.montage_calculation(mock_order, km=km, zona=zona)

        expected_goods_value = 0
        expected_sofa_count = 0
        expected_percentage_value = 0
        expected_price_with_sofa = 0
        # When no articles, price should be minimal price
        expected_price = self.cfg.montage_minimal_price
        expected_total_price = expected_price + zona

        self.assertEqual(result["goods_value"], expected_goods_value)
        self.assertEqual(result["sofa_count"], expected_sofa_count)
        self.assertEqual(result["percentage_value"], expected_percentage_value)
        self.assertEqual(result["price_with_sofa"], expected_price_with_sofa)
        self.assertEqual(result["total_price"], expected_total_price)

        # Assert specific draw_txt calls
        self.mock_draw_txt.assert_any_call(
            text=f"{zona:.2f}",  # Should be 0.00
            x_offset=520 - 10.0,
            y_offset=283,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_goods_value:.2f}",
            x_offset=425 - 10.0,
            y_offset=331,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_percentage_value:.2f}",
            x_offset=520 - 10.0,
            y_offset=331,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_sofa_count}",
            x_offset=420 - 10.0,
            y_offset=354,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_price_with_sofa:.2f}",
            x_offset=520 - 10.0,
            y_offset=354,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_total_price:.2f}",
            x_offset=520 - 10.0,
            y_offset=622,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )

    def test_montage_calculation_only_non_sofa_articles(self):
        articles = [
            self.create_mock_article(price=1000, quantity=2),
            self.create_mock_article(price=500, quantity=1),
        ]
        mock_order = MagicMock()
        mock_order.articles.all.return_value = articles

        km = 0
        zona = self.cfg.zone_1  # Zona 1, no extra km price for zone 1-3
        result = self.section.montage_calculation(mock_order, km=km, zona=zona)

        expected_goods_value = (1000 * 2) + (500 * 1)  # 2000 + 500 = 2500
        expected_percentage_value = expected_goods_value * 0.12  # 2500 * 0.12 = 300
        expected_price_with_sofa = 0

        # Montage price should be max(minimal_price, percentage_value + price_with_sofa)
        expected_price = max(
            self.cfg.montage_minimal_price,
            expected_percentage_value,
        )

        expected_total_price = expected_price + zona

        self.assertEqual(result["goods_value"], expected_goods_value)
        self.assertEqual(result["sofa_count"], 0)
        self.assertAlmostEqual(result["percentage_value"], expected_percentage_value)
        self.assertEqual(result["price_with_sofa"], expected_price_with_sofa)
        self.assertAlmostEqual(result["total_price"], expected_total_price)

        # Assert draw_txt calls for calculated values
        self.mock_draw_txt.assert_any_call(
            text=f"{zona:.2f}",
            x_offset=520 - 10.0,
            y_offset=283,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_goods_value:.2f}",
            x_offset=425 - 10.0,
            y_offset=331,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_percentage_value:.2f}",
            x_offset=520 - 10.0,
            y_offset=331,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_total_price:.2f}",
            x_offset=520 - 10.0,
            y_offset=622,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )

    def test_montage_calculation_only_sofa_articles(self):
        articles = [
            self.create_mock_article(quantity=1, is_sofa=True),
            self.create_mock_article(quantity=2, is_sofa=True),
        ]
        mock_order = MagicMock()
        mock_order.articles.all.return_value = articles

        km = 0
        zona = self.cfg.zone_2
        result = self.section.montage_calculation(mock_order, km=km, zona=zona)

        expected_goods_value = 0
        expected_percentage_value = 0
        expected_sofa_count = 3
        expected_price_with_sofa = (
            expected_sofa_count * self.cfg.montage_sofa_price
        )  # 3 * 495 = 1485

        # Montage price should be max(minimal_price, percentage_value + price_with_sofa)
        expected_price = max(
            self.cfg.montage_minimal_price,
            expected_percentage_value + expected_price_with_sofa,
        )

        expected_total_price = expected_price + zona  # 1485 + 379 = 1864

        self.assertEqual(result["goods_value"], expected_goods_value)
        self.assertEqual(result["sofa_count"], expected_sofa_count)
        self.assertEqual(result["percentage_value"], expected_percentage_value)
        self.assertEqual(result["price_with_sofa"], expected_price_with_sofa)
        self.assertAlmostEqual(result["total_price"], expected_total_price)

        # Assert draw_txt calls for calculated values
        self.mock_draw_txt.assert_any_call(
            text=f"{zona:.2f}",
            x_offset=520 - 10.0,
            y_offset=283,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_sofa_count}",
            x_offset=420 - 10.0,
            y_offset=354,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_price_with_sofa:.2f}",
            x_offset=520 - 10.0,
            y_offset=354,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_total_price:.2f}",
            x_offset=520 - 10.0,
            y_offset=622,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )

    def test_montage_calculation_mixed_articles_and_zone_4_shipping(self):
        articles = [
            self.create_mock_article(price=800, quantity=1),
            self.create_mock_article(quantity=1, is_sofa=True),
            self.create_mock_article(price=200, quantity=3),
        ]
        mock_order = MagicMock()
        mock_order.articles.all.return_value = articles

        km = 10
        zona = self.cfg.zone_4 + (km * self.cfg.km_price)  # Zone 4 with km price
        result = self.section.montage_calculation(mock_order, km=km, zona=zona)

        expected_goods_value = (800 * 1) + (200 * 3)  # 800 + 600 = 1400
        expected_sofa_count = 1
        expected_percentage_value = expected_goods_value * 0.12  # 1400 * 0.12 = 168
        expected_price_with_sofa = (
            expected_sofa_count * self.cfg.montage_sofa_price
        )  # 1 * 495 = 495

        # Montage price should be max(minimal_price, percentage_value + price_with_sofa)
        expected_price = max(
            self.cfg.montage_minimal_price,
            expected_percentage_value + expected_price_with_sofa,
        )

        # 495 + 168 = 663 (This sum is greater than minimal price, so expected_price is 663)
        expected_total_price = (
            expected_price + zona
        )  # 663 + (470 + (10 * 20)) = 663 + 670 = 1333

        self.assertEqual(result["goods_value"], expected_goods_value)
        self.assertEqual(result["sofa_count"], expected_sofa_count)
        self.assertAlmostEqual(result["percentage_value"], expected_percentage_value)
        self.assertEqual(result["price_with_sofa"], expected_price_with_sofa)
        self.assertAlmostEqual(result["total_price"], expected_total_price)

        # Assert draw_txt calls for calculated values, especially km and zona
        self.mock_draw_txt.assert_any_call(
            text=f"{km}",
            x_offset=424 - 10.0,
            y_offset=283,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{zona:.2f}",
            x_offset=520 - 10.0,
            y_offset=283,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_goods_value:.2f}",
            x_offset=425 - 10.0,
            y_offset=331,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_percentage_value:.2f}",
            x_offset=520 - 10.0,
            y_offset=331,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_sofa_count}",
            x_offset=420 - 10.0,
            y_offset=354,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_price_with_sofa:.2f}",
            x_offset=520 - 10.0,
            y_offset=354,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_total_price:.2f}",
            x_offset=520 - 10.0,
            y_offset=622,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )

    def test_montage_calculation_article_with_none_price(self):
        articles = [
            self.create_mock_article(price=None, quantity=2),  # Price is None
            self.create_mock_article(price=500, quantity=1),
        ]
        mock_order = MagicMock()
        mock_order.articles.all.return_value = articles

        km = 0
        zona = self.cfg.zone_1
        result = self.section.montage_calculation(mock_order, km=km, zona=zona)

        # Article with None price should not contribute to goods_value
        expected_goods_value = 500 * 1  # 500
        expected_percentage_value = expected_goods_value * 0.12  # 500 * 0.12 = 60
        expected_price_with_sofa = 0

        # Montage price should be max(minimal_price, percentage_value + price_with_sofa)
        expected_price = max(
            self.cfg.montage_minimal_price,
            expected_percentage_value + expected_price_with_sofa,
        )
        # Here, 60 is less than 454 (minimal_price), so expected_price should be 454.
        # This is the key change to reflect the `max` logic.

        expected_total_price = expected_price + zona  # 454 + 313 = 767

        self.assertEqual(result["goods_value"], expected_goods_value)
        self.assertAlmostEqual(result["percentage_value"], expected_percentage_value)
        self.assertAlmostEqual(result["total_price"], expected_total_price)


class MontageCalculationEdgeCasesTests(TestCase):
    def setUp(self):
        self.cfg = PdfConfig()
        self.mock_canvas = MagicMock()
        self.mock_buffer = MagicMock()
        self.utility = Utility(self.cfg, self.mock_canvas, self.mock_buffer)

        with patch.object(Utility, "font_register"):
            self.section = Section(MagicMock())
            self.section.cfg = self.cfg
            self.section.cvs = self.mock_canvas
            self.section.utils = self.utility

        self.patcher_draw_txt = patch.object(self.utility, "draw_txt")
        self.patcher_x_offset_length_2f = patch.object(
            self.utility,
            "x_offset_length_2f",
            side_effect=lambda num: (f"{num:.2f}", 10.0),
        )
        self.patcher_x_offset_length_0f = patch.object(
            self.utility, "x_offset_length_0f", side_effect=lambda num: (str(num), 10.0)
        )

        self.mock_draw_txt = self.patcher_draw_txt.start()
        self.mock_x_offset_length_2f = self.patcher_x_offset_length_2f.start()
        self.mock_x_offset_length_0f = self.patcher_x_offset_length_0f.start()

    def tearDown(self):
        self.patcher_draw_txt.stop()
        self.patcher_x_offset_length_2f.stop()
        self.patcher_x_offset_length_0f.stop()

    def create_mock_article(self, price=None, quantity=1, is_sofa=False):
        article = MagicMock()
        article.price = price
        article.quantity = quantity
        article.is_sofa = is_sofa
        return article

    def test_montage_calculation_zero_price_articles(self):
        # Test, kdy jsou všechny ceny článků 0, ale je zde množství
        articles = [
            self.create_mock_article(price=0, quantity=5),
            self.create_mock_article(price=0, quantity=1, is_sofa=True),
        ]
        mock_order = MagicMock()
        mock_order.articles.all.return_value = articles

        km = 0
        zona = self.cfg.zone_1
        result = self.section.montage_calculation(mock_order, km=km, zona=zona)

        expected_goods_value = 0
        expected_sofa_count = 1
        expected_percentage_value = 0
        expected_price_with_sofa = (
            expected_sofa_count * self.cfg.montage_sofa_price
        )  # 1 * 495 = 495

        # Montage price should be max(minimal_price, percentage_value + price_with_sofa)
        expected_price = max(
            self.cfg.montage_minimal_price,
            expected_percentage_value + expected_price_with_sofa,
        )
        # Here, 495 is greater than 454, so expected_price is 495.

        expected_total_price = expected_price + zona  # 495 + 313 = 808

        self.assertEqual(result["goods_value"], expected_goods_value)
        self.assertEqual(result["sofa_count"], expected_sofa_count)
        self.assertAlmostEqual(result["percentage_value"], expected_percentage_value)
        self.assertEqual(result["price_with_sofa"], expected_price_with_sofa)
        self.assertAlmostEqual(result["total_price"], expected_total_price)

    def test_montage_calculation_zero_quantity_articles(self):
        # Test, kdy jsou articles s cenou, ale s nulovým množstvím
        articles = [
            self.create_mock_article(price=1000, quantity=0),
            self.create_mock_article(price=500, quantity=0, is_sofa=True),
        ]
        mock_order = MagicMock()
        mock_order.articles.all.return_value = articles

        km = 0
        zona = self.cfg.zone_3
        result = self.section.montage_calculation(mock_order, km=km, zona=zona)

        expected_goods_value = 0
        expected_sofa_count = 0
        expected_percentage_value = 0
        expected_price_with_sofa = 0

        # Montage price should be max(minimal_price, percentage_value + price_with_sofa)
        expected_price = max(
            self.cfg.montage_minimal_price,
            expected_percentage_value + expected_price_with_sofa,
        )
        # Here, 0 is less than 454, so expected_price is 454.

        expected_total_price = expected_price + zona  # 454 + 470 = 924

        self.assertEqual(result["goods_value"], expected_goods_value)
        self.assertEqual(result["sofa_count"], expected_sofa_count)
        self.assertAlmostEqual(result["percentage_value"], expected_percentage_value)
        self.assertEqual(result["price_with_sofa"], expected_price_with_sofa)
        self.assertAlmostEqual(result["total_price"], expected_total_price)

    def test_montage_calculation_zone_4_with_valid_km(self):
        # Test Zone 4 s platným počtem km (např. 23 km)
        articles = [
            self.create_mock_article(price=1000, quantity=1),
        ]
        mock_order = MagicMock()
        mock_order.articles.all.return_value = articles

        km = 23  # Nastavujeme km na platnou hodnotu, např. 23
        zona = self.cfg.zone_4 + (
            km * self.cfg.km_price
        )  # Zóna s připočítanými km navíc

        result = self.section.montage_calculation(mock_order, km=km, zona=zona)

        expected_goods_value = 1000
        expected_percentage_value = expected_goods_value * 0.12  # 120
        expected_price_with_sofa = 0

        # Montage price should be max(minimal_price, percentage_value + price_with_sofa)
        expected_price = max(
            self.cfg.montage_minimal_price,
            expected_percentage_value + expected_price_with_sofa,
        )
        # Here, 120 is less than 454, so expected_price is 454.

        # Výpočet celkové dopravy: základní cena zóny (470) + (23 km * 20 Kč/km) = 470 + 460 = 930
        expected_transport_cost = self.cfg.zone_4 + (km * self.cfg.km_price)
        expected_total_price = (
            expected_price + expected_transport_cost
        )  # 454 + 930 = 1384

        self.assertEqual(result["goods_value"], expected_goods_value)
        self.assertAlmostEqual(result["percentage_value"], expected_percentage_value)
        self.assertAlmostEqual(result["total_price"], expected_total_price)

        self.mock_draw_txt.assert_any_call(
            text="23",  # Očekáváme text "23"
            x_offset=424 - 10.0,  # Používá se mockovaná délka 10.0 z x_offset_length_0f
            y_offset=283,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )

    def test_montage_calculation_large_values(self):
        # Test s velkými hodnotami pro goods_value a km
        articles = [
            self.create_mock_article(price=100000, quantity=10),  # 1,000,000
            self.create_mock_article(quantity=5, is_sofa=True),  # 5 * 495 = 2475
        ]
        mock_order = MagicMock()
        mock_order.articles.all.return_value = articles

        km = 200  # Velký počet km
        zona = self.cfg.zone_4 + (
            km * self.cfg.km_price
        )  # 470 + (200 * 20) = 470 + 4000 = 4470
        result = self.section.montage_calculation(mock_order, km=km, zona=zona)

        expected_goods_value = 1000000
        expected_sofa_count = 5
        expected_percentage_value = expected_goods_value * 0.12  # 120,000
        expected_price_with_sofa = (
            expected_sofa_count * self.cfg.montage_sofa_price
        )  # 2475

        # Montage price should be max(minimal_price, percentage_value + price_with_sofa)
        expected_price = max(
            self.cfg.montage_minimal_price,
            expected_percentage_value + expected_price_with_sofa,
        )
        # Here, 122475 is greater than 454, so expected_price is 122475.

        expected_total_price = expected_price + zona  # 122475 + 4470 = 126945

        self.assertEqual(result["goods_value"], expected_goods_value)
        self.assertEqual(result["sofa_count"], expected_sofa_count)
        self.assertAlmostEqual(result["percentage_value"], expected_percentage_value)
        self.assertEqual(result["price_with_sofa"], expected_price_with_sofa)
        self.assertAlmostEqual(result["total_price"], expected_total_price)

        self.mock_draw_txt.assert_any_call(
            text=f"{km}",
            x_offset=424 - 10.0,
            y_offset=283,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{zona:.2f}",
            x_offset=520 - 10.0,
            y_offset=283,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_goods_value:.2f}",
            x_offset=425 - 10.0,
            y_offset=331,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_percentage_value:.2f}",
            x_offset=520 - 10.0,
            y_offset=331,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_total_price:.2f}",
            x_offset=520 - 10.0,
            y_offset=622,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )

    def test_montage_calculation_below_minimal_price(self):
        # New test case to explicitly check the minimal price logic
        articles = [
            self.create_mock_article(
                price=100, quantity=1
            ),  # Goods value 100, percentage 12
        ]
        mock_order = MagicMock()
        mock_order.articles.all.return_value = articles

        km = 0
        zona = self.cfg.zone_1  # 313
        result = self.section.montage_calculation(mock_order, km=km, zona=zona)

        expected_goods_value = 100
        expected_sofa_count = 0
        expected_percentage_value = expected_goods_value * 0.12  # 12
        expected_price_with_sofa = 0

        # Calculated montage price (12 + 0 = 12) is less than minimal price (454)
        # So, expected_price should be cfg.montage_minimal_price
        expected_price = max(
            self.cfg.montage_minimal_price,
            expected_percentage_value + expected_price_with_sofa,
        )

        expected_total_price = expected_price + zona  # 454 + 313 = 767

        self.assertEqual(result["goods_value"], expected_goods_value)
        self.assertEqual(result["sofa_count"], expected_sofa_count)
        self.assertAlmostEqual(result["percentage_value"], expected_percentage_value)
        self.assertEqual(result["price_with_sofa"], expected_price_with_sofa)
        self.assertAlmostEqual(result["total_price"], expected_total_price)

        self.mock_draw_txt.assert_any_call(
            text=f"{zona:.2f}",
            x_offset=520 - 10.0,
            y_offset=283,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_goods_value:.2f}",
            x_offset=425 - 10.0,
            y_offset=331,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_percentage_value:.2f}",
            x_offset=520 - 10.0,
            y_offset=331,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
        self.mock_draw_txt.assert_any_call(
            text=f"{expected_total_price:.2f}",
            x_offset=520 - 10.0,
            y_offset=622,
            font="Roboto-Semibold",
            font_size=self.cfg.font_size_bigger,
        )
