# DealGuard

**A promotional-claim verifier: TF-IDF retrieval + deterministic verification, with an optional, guarded Gemini explanation layer.**
Developed during SDAIA Academy's Generative AI Solutions Development Program
([github.com/SDAIAAcademy](https://github.com/SDAIAAcademy)).

> **Synthetic data only.** All policies, coupon codes and offers are fictional. No real merchants or offers are involved.

> **Transparency notice.** By default DealGuard uses TF-IDF *retrieval*, deterministic Python rules and a *template* explanation (no LLM).
> If `GEMINI_API_KEY` is set, Gemini may **reword** the already-verified result; it never calculates prices or decides eligibility.
> The UI labels every explanation as *template-generated* or *LLM-generated*. The Gemini path is covered by mocked tests only;
> a live Gemini request has **not** been verified in this repository.

Presentation material for the team: [PRESENTATION_HANDOFF.md](PRESENTATION_HANDOFF.md)

## Objectives
- Demonstrate a grounded, auditable pipeline: every verdict cites the policy it came from.
- Keep eligibility and money calculations in deterministic code, never in free-form model output.
- Refuse (rather than guess) when no policy evidence exists.

## Real-world problem
Advertisements such as *"20% off everything!"* often hide exclusions, caps, minimum spends and expiry dates.
Shoppers (or support agents) need the *actual* discount. DealGuard compares the advertised claim with the governing policy and flags misleading claims.

## Architecture
```
 input (price, category, coupon, claim)
        |
  1. Validation ............ type/range/format checks (verifier.py)
        |
  2. TF-IDF retrieval ...... cosine similarity over 8 policy texts (retriever.py, stdlib only)
        |
  3. Policy lookup ......... coupon -> policy; unknown/missing coupon => REFUSED (never invents a policy)
        |
  4. Deterministic rules ... expiry, category allow/exclude, minimum spend (verifier.py)
        |
  5. Discount calculation .. percent (with cap) / flat / free-shipping, final price
        |
  6. Claim check ........... parse "%"/SAR amounts in the claim, warn if claim > actual discount
        |
  7. Explanation ........... template (default)  OR  optional Gemini rewording (llm.py)
                             -> grounding guard: cited IDs present + no new numbers, else template
```
- **Retrieval** surfaces relevant policy text as evidence (cosine scores shown). The governing policy of a known coupon is always included and cited.
- **Verification** is plain Python; neither retrieval nor the LLM decides eligibility.
- **Optional LLM** (`llm.py`, stdlib `urllib`, Gemini REST API) receives only the verified facts and evidence. It is skipped for `REFUSED` / `INVALID_INPUT`, and its output is rejected if it omits a cited source ID or contains any number not present in the verified facts/evidence.

## Setup and launch (local)
Requires Python 3.10+. The recommended launcher uses only the standard library - no `pip install` needed.

```bash
python app_web.py            # optional custom port: python app_web.py 9000
```
Open **http://127.0.0.1:8765**.

Optional Gemini explanations (free-tier API key from Google AI Studio; never commit it):
```powershell
$env:GEMINI_API_KEY = "<your key>"       # PowerShell; bash: export GEMINI_API_KEY=...
$env:GEMINI_MODEL   = "gemini-2.5-flash" # optional
python app_web.py
```
Without the key, the app runs fully in template mode.

Optional Gradio UI (template explanations only; needs `pip install -r requirements.txt`):
```bash
python app.py
```
> **Windows restriction:** on machines with Windows Application Control policies, `python app.py` can fail with
> `ImportError: DLL load failed while importing aggregations: An Application Control policy has blocked this file.`
> Gradio imports pandas, whose native DLL is blocked. Security settings are neither changed nor bypassed;
> use `app_web.py`, which has no third-party dependencies.

## Example scenario
Input: price `1000` SAR, category `Fashion`, coupon `SAVE20`, claim `20% off everything!`

| Output | Value |
|---|---|
| Status | ELIGIBLE |
| Calculation | 1000.00 x 20% = 200.00, capped at 150 SAR |
| Actual discount / final price | 150.00 SAR / 850.00 SAR |
| Warning | Misleading claim: advertised ~200.00 SAR vs. 150.00 SAR actual |
| Source | `DEAL-SAVE20` |

Try also: `SAVE20` + `Electronics` (excluded), `FLASH50` (expired), `FAKE99` (refused: unknown coupon).

## Demo
![DealGuard Demo](screenshots/dealguard-demo.png)

## Tests
```bash
python -m unittest -v
```
25 tests, standard library only, no network:
- `test_dealguard.py` (16): eligible/ineligible rules, caps, flat and shipping coupons, expiry, misleading claims, safe refusal, invalid inputs, retrieval relevance, claim parsing.
- `test_llm.py` (9): Gemini **mocked** - no-key fallback, grounded response accepted, invented numbers rejected, missing source ID rejected, no LLM call on refusals, API-error fallback, LLM cannot alter price/status, localhost Host check.

Last verified result: `Ran 25 tests ... OK` (Python 3.13, Windows).
Note: policies are valid until 2026-12-31 and `FLASH50` expired 2026-01-31. `test_dealguard.py` uses a fixed date; two web-layer tests in `test_llm.py` use today's date and assume `SAVE20` is still valid.

## Optional deployment (Render free plan)
Not deployed yet - no public URL exists. To deploy:
1. Push this repository to GitHub (done for `main`).
2. In Render: **New > Blueprint**, select the repo; `render.yaml` creates a free web service
   (`python app_web.py`, no packages installed, health check `/healthz`).
3. Render sets `PORT` and `RENDER_EXTERNAL_HOSTNAME`; `render.yaml` sets `DEALGUARD_HOST=0.0.0.0`.
4. Optionally add `GEMINI_API_KEY` as a secret in the Render dashboard (leave empty for template mode).

| Variable | Default | Purpose |
|---|---|---|
| `PORT` | `8765` | Listening port (CLI argument wins) |
| `DEALGUARD_HOST` | `127.0.0.1` | Bind address; `0.0.0.0` only on a hosting provider |
| `DEALGUARD_ALLOWED_HOSTS` | - | Extra public hostnames accepted in the `Host` header |
| `GEMINI_API_KEY` / `GEMINI_MODEL` | - / `gemini-2.5-flash` | Optional LLM explanations |

## Security considerations
- Local default binds to `127.0.0.1` and accepts only `127.0.0.1:PORT` / `localhost:PORT` Host headers (DNS-rebinding protection). Public mode accepts the configured hostnames.
- Server-side validation (numeric price range, category whitelist, coupon `[A-Z0-9]{3,20}`, claim <= 300 chars); JSON-only API, 4 KB body limit, 20 s connection timeout.
- All rendered text is HTML-escaped; responses send CSP, `nosniff`, `X-Frame-Options: DENY`, `no-referrer`.
- API keys only via environment variables; `.env` files are git-ignored; keys are never logged or returned.
- LLM output is treated as untrusted: the claim is passed as data, and the grounding guard falls back to the template on any violation.

## Known limitations
- Prototype with 8 fictional policies and 6 categories; not for real pricing decisions.
- TF-IDF is lexical (no synonyms/semantic search); claim parsing recognises `%`, `SAR`/`riyal`/`ريال`, `save`/`off N`.
- Single-item pricing; no coupon stacking, quantities, taxes or shipping fees.
- The grounding guard checks IDs and numbers, not full meaning; an LLM could still phrase something imprecisely.
- Live Gemini generation is unverified here (no key was available); only mocked tests exist.
- `http.server` is a demo server: no rate limiting or TLS of its own (Render provides HTTPS). A public deployment with a Gemini key could consume the key's quota.

## Files
- `policies.py` - 8 fictional policies (incl. one expired)
- `retriever.py` - TF-IDF + cosine retrieval
- `verifier.py` - validation, rules, calculation
- `llm.py` - optional Gemini explanation layer + grounding guard
- `app_web.py` - stdlib web UI (recommended)
- `app.py` - Gradio UI (optional)
- `test_dealguard.py`, `test_llm.py` - unit tests
- `render.yaml` - optional free Render deployment
- `PRESENTATION_HANDOFF.md` - presentation content for the team

## Attribution
Developed during SDAIA Academy's Generative AI Solutions Development Program - <https://github.com/SDAIAAcademy>.
