# DealGuard - Presentation Handoff

Content for the teammate building the slides with the team template. Everything here matches the actual code in this repository.
**Implemented** = works today. **Optional** = in the code but needs a user-supplied API key. **Future** = not built.

- 🌐 **Live Demo:** https://dealguard-a7k8.onrender.com/ *(Hosted on Render free tier; may take 30–60s to wake up after inactivity. Runs in deterministic template mode without API key.)*
- 💻 **Repository:** https://github.com/Thamer-99/DealGuard
- 🖼️ **Screenshot:** https://github.com/Thamer-99/DealGuard/blob/main/screenshots/dealguard-demo.png
- 🎓 **Program:** SDAIA Academy - Generative AI Solutions Development Program (https://github.com/SDAIAAcademy)

## 1. Elevator pitch
DealGuard checks whether a promotional claim (e.g. "20% off everything!") is true for a specific product. It retrieves the governing policy, applies the rules in deterministic code, calculates the real discount and final price, warns about misleading claims and cites its sources.

## 2. Problem
Ads hide exclusions, discount caps, minimum spends and expiry dates. Shoppers and support agents can't easily see the *real* price. A plain chatbot could invent policies or miscalculate money.

## 3. What makes it distinctive
- **Grounded:** every verdict cites a policy ID (e.g. `DEAL-SAVE20`).
- **Deterministic money:** eligibility and prices are computed in Python, never by an AI model.
- **Safe refusal:** an unknown or missing coupon gives `REFUSED`, with no invented policy and no discount.
- **Transparent:** the UI shows the evidence, rule checks, calculation steps, and whether the explanation is template- or LLM-generated.
- **Guarded LLM (optional):** Gemini may only reword verified facts. Its output is rejected if it adds any number or omits the source ID.

## 4. Technologies (actual roles)
| Technology | Role | Status |
|---|---|---|
| Python 3 (standard library) | All logic, the web server (`http.server`), the tests (`unittest`) | Implemented |
| TF-IDF + cosine similarity (hand-written) | Retrieves relevant policy texts (the "R" in RAG) | Implemented |
| Rule engine in Python | Expiry, category, minimum-spend checks, discount maths | Implemented |
| HTML/CSS/JavaScript | Responsive single-page UI, all output HTML-escaped | Implemented |
| Google Gemini REST API (`urllib`) | Natural-language rewording of verified results | Optional (needs key); mocked tests only, inactive on live demo |
| Gradio | Alternative UI | Optional (blocked on the dev laptop by Windows Application Control) |
| Render (free plan) | Public hosting via `render.yaml` | **Deployed & live** at https://dealguard-a7k8.onrender.com/ |

## 5. Architecture (simple)
```
User input -> Validation -> TF-IDF Retrieval -> Policy Lookup -> Rule Verification
           -> Discount Calculation -> Claim Check -> Explanation (template or guarded Gemini)
```

## 6. Step-by-step flow
1. **User input:** price, category, coupon code, promotional claim.
2. **Validation:** price must be > 0 and <= 1,000,000 SAR; the category must be one of 6; the coupon must be 3-20 letters/digits; the claim at most 300 characters.
3. **Policy retrieval:** TF-IDF ranks the 8 synthetic policies by cosine similarity (top 3, minimum score 0.05).
4. **Rule verification:** coupon to policy. Unknown coupon gives REFUSED. Then it checks expiry, allowed/excluded categories and minimum spend.
5. **Discount calculation:** percentage with a cap, flat amount, or free shipping (no price change), then the final price.
6. **Claim check:** reads the "%" or "SAR" amount from the claim and warns if it is larger than the real discount.
7. **Explanation:** template text by default. With `GEMINI_API_KEY` set, Gemini rewords the result and the grounding guard accepts or rejects its output.

## 7. Live demo (verified on live Render deployment & local server)
- **Live URL:** https://dealguard-a7k8.onrender.com/ *(allow 30-60s if waking from idle)*
- **Local:** Run `python app_web.py` and open http://127.0.0.1:8765

| Step | Input | Expected result |
|---|---|---|
| A | 1000, **Fashion**, SAVE20, "20% off everything!" | ELIGIBLE. 1000 x 20% = 200, capped at 150. **Discount 150, final 850 SAR.** Misleading-claim warning. Source `DEAL-SAVE20` |
| B | 1000, **Electronics**, SAVE20, "20% off" | NOT ELIGIBLE (Electronics excluded). Discount 0, final 1000 |
| C | 100, Books, **FAKE99**, "99% off" | REFUSED: no policy evidence, no discount invented |

Tip: the form starts on *Electronics*, so for step A switch the category to *Fashion*.

## 8. Tests
`python -m unittest -v` gives **25 tests, all passing** (stdlib, no network).
- 16 core tests: eligible/ineligible cases, cap, flat and shipping coupons, expired coupon, misleading claims, unknown/missing coupon refusal, invalid price/category/coupon, retrieval relevance, out-of-scope query returns no evidence, claim parsing.
- 9 LLM/web tests (Gemini **mocked**): fallback without a key, grounded answer accepted, invented number rejected, missing source ID rejected, no LLM on refusals, API error falls back, the LLM cannot change price or status, Host-header protection.
- An additional manual HTTP check covered 17 endpoint/scenario cases, all passing (valid/invalid inputs, 403/404/400/413/415 handling).

## 9. Security features
- The server binds to 127.0.0.1 by default and rejects foreign Host headers.
- Server-side input validation, JSON-only API, 4 KB request limit, connection timeout.
- HTML escaping, plus Content-Security-Policy, anti-framing and nosniff headers.
- No secrets in the code. The API key comes only from an environment variable, and `.env` is git-ignored.
- LLM output is treated as untrusted and checked before display.

## 10. Limitations (be honest on stage)
- 8 fictional policies, single item, no coupon stacking, taxes or shipping fees.
- TF-IDF is keyword-based (no semantic understanding).
- Live Gemini generation has not been tested (no key was available). Only mocked tests exist.
- Public deployment runs on Render's free tier (spins down on inactivity, ~30–60s cold start). Without `GEMINI_API_KEY`, it runs purely in deterministic template mode.

## 11. Future improvements
- Semantic embeddings for retrieval; Arabic-language policies and claims.
- Live, evaluated Gemini explanations; Arabic explanations.
- Multi-item carts, coupon stacking rules, VAT.
- Real policy ingestion (PDF/HTML) with versioning; production scaling with custom domain and rate limiting.

## 12. Suggested five slides (content only)
1. **DealGuard - Verify the Deal, Not the Ad.** Problem: hidden caps, exclusions and expiry. One-line pitch. SDAIA Academy attribution.
2. **How It Works.** Flow diagram (section 5). Key message: "AI retrieves and explains, Python decides and calculates."
3. **Live Demo: SAVE20.** Screenshot / Live Link. Scenario A: the claim says 20% (200 SAR), the real discount is 150 SAR, final price 850 SAR, cited `DEAL-SAVE20`.
4. **Trust & Safety.** Safe refusal, source citations, input validation, guarded optional LLM, 25 passing tests.
5. **Limitations & Next Steps.** Section 10 and the top 3 items of section 11. Repo link and QR code.

## 13. Arabic speaker notes
1. **المقدمة:** "كثير من الإعلانات تقول خصم 20% على كل شيء، لكن فيه شروط مخفية مثل حد أعلى للخصم أو فئات مستثناة. DealGuard يتحقق من العرض الحقيقي قبل الشراء."
2. **طريقة العمل:** "النظام يسترجع السياسة المناسبة باستخدام TF-IDF، وبعدها كود Python يطبق الشروط ويحسب الخصم بدقة. الذكاء الاصطناعي ما يحسب الأسعار أبداً."
3. **العرض الحي:** "منتج أزياء بـ1000 ريال مع كود SAVE20. الإعلان يوحي بخصم 200 ريال، لكن السياسة تحدد الحد الأعلى بـ150، فالسعر النهائي 850 ريال، والنظام ينبهنا أن الإعلان مضلل ويذكر المصدر DEAL-SAVE20."
4. **الأمان:** "إذا الكود غير موجود، النظام يرفض بدل ما يخترع سياسة. وأي شرح من Gemini يمر على فحص يتأكد أنه ما أضاف أرقام جديدة ويذكر المصدر. وعندنا 25 اختبار ناجح."
5. **الخاتمة:** "البيانات تجريبية بالكامل، والتطبيق منشور ويعمل سحابياً للتجربة الحية، وربط Gemini يظل اختيارياً. الخطوات القادمة: دعم اللغة العربية والبحث الدلالي. تم تطويره ضمن برنامج تطوير حلول الذكاء الاصطناعي التوليدي في أكاديمية سدايا."
