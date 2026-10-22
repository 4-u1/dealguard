import unittest
from datetime import date

from retriever import TfidfRetriever
from verifier import parse_claim, verify

TODAY = date(2026, 10, 22)


def v(price, cat, coupon, claim="", ):
    return verify(price, cat, coupon, claim, today=TODAY)


class TestDealGuard(unittest.TestCase):
    # --- success
    def test_01_save20_electronics_ineligible(self):
        r = v(1000, "Electronics", "SAVE20", "20% off")
        self.assertEqual(r.status, "INELIGIBLE")
        self.assertEqual(r.final_price, 1000)
        self.assertIn("DEAL-SAVE20", r.cited_ids)
        self.assertTrue(any("MISLEADING" in w for w in r.warnings))

    def test_02_save20_fashion_capped(self):
        r = v(1000, "Fashion", "SAVE20", "20% off")
        self.assertEqual(r.status, "ELIGIBLE")
        self.assertEqual(r.discount, 150)  # 200 capped to 150
        self.assertEqual(r.final_price, 850)

    def test_03_books_percent(self):
        r = v(100, "Books", "books25", "25% off")
        self.assertEqual((r.status, r.discount, r.final_price), ("ELIGIBLE", 25, 75))
        self.assertFalse(r.warnings)

    def test_04_flat_discount(self):
        r = v(600, "Electronics", "TECH50", "50 SAR off")
        self.assertEqual((r.status, r.discount, r.final_price), ("ELIGIBLE", 50, 550))

    # --- ineligible rules
    def test_05_below_min_spend(self):
        r = v(100, "Fashion", "FASHION30", "30% off")
        self.assertEqual(r.status, "INELIGIBLE")
        self.assertEqual(r.discount, 0)

    def test_06_wrong_category(self):
        self.assertEqual(v(500, "Books", "HOME15").status, "INELIGIBLE")

    def test_07_expired(self):
        r = v(100, "Books", "FLASH50", "50% off")
        self.assertEqual(r.status, "INELIGIBLE")
        self.assertTrue(any("expired" in x for x in r.reasons))

    def test_08_excessive_claim_warning(self):
        r = v(1000, "Fashion", "WELCOME10", "50% off")
        self.assertEqual(r.discount, 50)
        self.assertTrue(r.warnings)

    # --- safe refusals / unsupported
    def test_09_unknown_coupon_refused(self):
        r = v(100, "Books", "MEGA99", "99% off")
        self.assertEqual(r.status, "REFUSED")
        self.assertEqual((r.discount, r.final_price), (0, 100))
        self.assertNotIn("DEAL-MEGA99", r.cited_ids)

    def test_10_missing_coupon_refused(self):
        self.assertEqual(v(100, "Books", "", "huge sale").status, "REFUSED")

    # --- invalid arguments
    def test_11_invalid_price(self):
        for bad in (-5, 0, "abc", None, float("inf"), 10**9):
            self.assertEqual(v(bad, "Books", "BOOKS25").status, "INVALID_INPUT", bad)

    def test_12_invalid_category_and_coupon(self):
        self.assertEqual(v(100, "Cars", "BOOKS25").status, "INVALID_INPUT")
        self.assertEqual(v(100, "Books", "BAD CODE!;").status, "INVALID_INPUT")

    # --- retrieval / out of scope
    def test_13_out_of_scope_query_no_evidence(self):
        self.assertEqual(TfidfRetriever().search("what is the weather in Riyadh tomorrow"), [])

    def test_14_retrieval_finds_right_policy(self):
        top = TfidfRetriever().search("free delivery fee shipping")[0]
        self.assertEqual(top["id"], "DEAL-SHIPFREE")

    def test_15_claim_parsing(self):
        self.assertEqual(parse_claim("20% off"), {"type": "percent", "value": 20.0})
        self.assertEqual(parse_claim("50 SAR off")["type"], "flat")
        self.assertIsNone(parse_claim("amazing deal"))

    def test_16_shipping_coupon_no_price_change(self):
        r = v(200, "Books", "SHIPFREE", "free shipping")
        self.assertEqual((r.status, r.discount, r.final_price), ("ELIGIBLE", 0, 200))


if __name__ == "__main__":
    unittest.main()
