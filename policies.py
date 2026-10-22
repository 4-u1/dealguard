"""Synthetic (fictional) promotion policies. No real merchants or offers."""
from datetime import date

CATEGORIES = ["Electronics", "Fashion", "Home & Kitchen", "Books", "Groceries", "Gift Cards"]

# discount_type: "percent" | "flat" | "shipping" (shipping = no price reduction)
POLICIES = [
    {
        "id": "DEAL-SAVE20",
        "code": "SAVE20",
        "title": "SAVE20 - 20% Off Site-Wide (Selected Categories)",
        "discount_type": "percent", "value": 20, "cap": 150, "min_spend": 200,
        "allowed_categories": None,
        "excluded_categories": ["Electronics", "Gift Cards"],
        "expires": date(2026, 12, 31),
        "source_text": ("SAVE20 gives 20% off eligible orders of at least 200 SAR, with a maximum "
                        "discount of 150 SAR. Electronics and Gift Cards are excluded from SAVE20. "
                        "Valid until 2026-12-31."),
    },
    {
        "id": "DEAL-WELCOME10",
        "code": "WELCOME10",
        "title": "WELCOME10 - 10% New Customer Offer",
        "discount_type": "percent", "value": 10, "cap": 50, "min_spend": 0,
        "allowed_categories": None,
        "excluded_categories": ["Gift Cards"],
        "expires": date(2026, 12, 31),
        "source_text": ("WELCOME10 gives new customers 10% off any order in any category except Gift "
                        "Cards. The maximum discount is 50 SAR. No minimum spend. Valid until 2026-12-31."),
    },
    {
        "id": "DEAL-FASHION30",
        "code": "FASHION30",
        "title": "FASHION30 - 30% Off Fashion",
        "discount_type": "percent", "value": 30, "cap": 300, "min_spend": 300,
        "allowed_categories": ["Fashion"],
        "excluded_categories": [],
        "expires": date(2026, 12, 31),
        "source_text": ("FASHION30 gives 30% off clothing, shoes and accessories in the Fashion category "
                        "only. Minimum spend 300 SAR. Maximum discount 300 SAR. Valid until 2026-12-31."),
    },
    {
        "id": "DEAL-HOME15",
        "code": "HOME15",
        "title": "HOME15 - 15% Off Home & Kitchen",
        "discount_type": "percent", "value": 15, "cap": 200, "min_spend": 150,
        "allowed_categories": ["Home & Kitchen"],
        "excluded_categories": [],
        "expires": date(2026, 12, 31),
        "source_text": ("HOME15 gives 15% off furniture, cookware and appliances for the home in the Home & "
                        "Kitchen category only. Minimum spend 150 SAR. Maximum discount 200 SAR. "
                        "Valid until 2026-12-31."),
    },
    {
        "id": "DEAL-TECH50",
        "code": "TECH50",
        "title": "TECH50 - 50 SAR Off Electronics",
        "discount_type": "flat", "value": 50, "cap": 50, "min_spend": 500,
        "allowed_categories": ["Electronics"],
        "excluded_categories": [],
        "expires": date(2026, 12, 31),
        "source_text": ("TECH50 takes a flat 50 SAR off phones, laptops and other Electronics when the "
                        "order is at least 500 SAR. It is not a percentage discount. Electronics only. "
                        "Valid until 2026-12-31."),
    },
    {
        "id": "DEAL-BOOKS25",
        "code": "BOOKS25",
        "title": "BOOKS25 - 25% Off Books",
        "discount_type": "percent", "value": 25, "cap": 40, "min_spend": 0,
        "allowed_categories": ["Books"],
        "excluded_categories": [],
        "expires": date(2026, 12, 31),
        "source_text": ("BOOKS25 gives 25% off printed books and textbooks in the Books category only. "
                        "The maximum discount is 40 SAR. No minimum spend. Valid until 2026-12-31."),
    },
    {
        "id": "DEAL-SHIPFREE",
        "code": "SHIPFREE",
        "title": "SHIPFREE - Free Shipping",
        "discount_type": "shipping", "value": 0, "cap": 0, "min_spend": 100,
        "allowed_categories": None,
        "excluded_categories": ["Gift Cards"],
        "expires": date(2026, 12, 31),
        "source_text": ("SHIPFREE waives the delivery fee on orders of at least 100 SAR in any category "
                        "except Gift Cards. It does not reduce the product price. Valid until 2026-12-31."),
    },
    {
        "id": "DEAL-FLASH50",
        "code": "FLASH50",
        "title": "FLASH50 - 50% Flash Sale (EXPIRED)",
        "discount_type": "percent", "value": 50, "cap": 500, "min_spend": 0,
        "allowed_categories": None,
        "excluded_categories": ["Gift Cards"],
        "expires": date(2026, 1, 31),
        "source_text": ("FLASH50 was a 50% flash sale discount with a maximum of 500 SAR, excluding Gift "
                        "Cards. The promotion ended on 2026-01-31 and is no longer valid."),
    },
]

POLICY_BY_CODE = {p["code"]: p for p in POLICIES}
POLICY_BY_ID = {p["id"]: p for p in POLICIES}
