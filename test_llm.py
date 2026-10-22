"""Tests for the optional LLM layer and the web API. Gemini is always MOCKED - no network calls."""
import os
import unittest
import urllib.error
from datetime import date
from unittest import mock

import app_web
import llm
from verifier import verify

TODAY = date(2026, 10, 22)
KEY = {"GEMINI_API_KEY": "test-key-not-real"}


def save20_fashion():
    return verify(1000, "Fashion", "SAVE20", "20% off everything!", today=TODAY)


class TestLLMLayer(unittest.TestCase):
    def test_17_no_key_uses_template(self):
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(llm, "_call_gemini") as call:
            out = llm.explain(save20_fashion())
        call.assert_not_called()
        self.assertEqual(out["source"], "template")

    def test_18_grounded_mock_response_accepted(self):
        r = save20_fashion()
        text = ("SAVE20 applies to this Fashion item, but the discount is capped at 150 SAR, so you pay "
                "850 SAR instead of 1000 SAR. The advertised 20% is misleading here [DEAL-SAVE20].")
        with mock.patch.dict(os.environ, KEY), mock.patch.object(llm, "_call_gemini", return_value=text):
            out = llm.explain(r, "20% off everything!")
        self.assertEqual(out["source"], "gemini")
        self.assertIn("DEAL-SAVE20", out["text"])

    def test_19_invented_number_rejected(self):
        bad = "You save 200 SAR and pay 800 SAR [DEAL-SAVE20]."  # 800 was never computed
        with mock.patch.dict(os.environ, KEY), mock.patch.object(llm, "_call_gemini", return_value=bad):
            out = llm.explain(save20_fashion())
        self.assertEqual(out["source"], "template")
        self.assertIn("800", out["note"])

    def test_20_missing_source_id_rejected(self):
        with mock.patch.dict(os.environ, KEY), \
                mock.patch.object(llm, "_call_gemini", return_value="You pay 850 SAR."):
            out = llm.explain(save20_fashion())
        self.assertEqual(out["source"], "template")
        self.assertIn("missing source ID", out["note"])

    def test_21_refusal_and_invalid_never_call_llm(self):
        refused = verify(100, "Books", "MEGA99", "99% off", today=TODAY)
        invalid = verify(-1, "Books", "BOOKS25", today=TODAY)
        with mock.patch.dict(os.environ, KEY), mock.patch.object(llm, "_call_gemini") as call:
            for r in (refused, invalid):
                self.assertEqual(llm.explain(r)["source"], "template")
        call.assert_not_called()

    def test_22_api_error_falls_back(self):
        err = urllib.error.URLError("offline")
        with mock.patch.dict(os.environ, KEY), mock.patch.object(llm, "_call_gemini", side_effect=err):
            out = llm.explain(save20_fashion())
        self.assertEqual(out["source"], "template")
        self.assertNotIn("test-key-not-real", out["note"])

    def test_23_llm_cannot_change_deterministic_results(self):
        rogue = "IGNORE RULES: final price is 1 SAR [DEAL-SAVE20]."
        fields = {"price": "1000", "category": "Fashion", "coupon": "SAVE20", "claim": "20% off"}
        with mock.patch.dict(os.environ, KEY), mock.patch.object(llm, "_call_gemini", return_value=rogue):
            out = app_web.build_response(fields)
        self.assertEqual((out["status"], out["discount"], out["final_price"]), ("ELIGIBLE", 150.0, 850.0))
        self.assertEqual(out["explanation_source"], "template")  # guard rejected "1"


class TestWebConfig(unittest.TestCase):
    def test_24_localhost_host_check(self):
        self.assertTrue(app_web.LOCAL_MODE)
        self.assertTrue(app_web.host_allowed(f"127.0.0.1:{app_web.PORT}"))
        self.assertFalse(app_web.host_allowed("evil.example.com"))

    def test_25_response_no_key_marks_template(self):
        fields = {"price": "1000", "category": "Fashion", "coupon": "SAVE20", "claim": "20% off"}
        with mock.patch.dict(os.environ, {}, clear=True):
            out = app_web.build_response(fields)
        self.assertEqual(out["explanation_source"], "template")
        self.assertEqual(out["explanation"], out["template_explanation"])
        self.assertEqual(out["cited_ids"], ["DEAL-SAVE20"])


if __name__ == "__main__":
    unittest.main()
