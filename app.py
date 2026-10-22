"""DealGuard - Gradio UI. Run: python app.py"""
import gradio as gr

from policies import CATEGORIES, POLICIES
from verifier import verify

CSS = """
.gradio-container {max-width: 1000px !important}
.dg-title {background: linear-gradient(120deg,#0f766e,#4338ca); color:#fff; padding:20px 24px;
  border-radius:14px; margin-bottom:8px}
.dg-title h1 {margin:0; font-size:1.8rem; color:#fff}
.dg-title p {margin:4px 0 0; opacity:.9}
.dg-card {border-radius:12px; padding:14px 16px; margin:6px 0; border:1px solid #e2e8f0}
.dg-evidence {background:#eff6ff; border-color:#93c5fd}
.dg-calc {background:#f0fdf4; border-color:#86efac}
.dg-gen {background:#fffbeb; border-color:#fcd34d}
.dg-warn {background:#fef2f2; border-color:#fca5a5; color:#991b1b; font-weight:600}
.dg-card, .dg-card * {color:#0f172a}
.dg-warn, .dg-warn * {color:#991b1b}
"""

BADGE = {"ELIGIBLE": "✅ ELIGIBLE", "INELIGIBLE": "❌ NOT ELIGIBLE",
         "REFUSED": "⚠️ REFUSED (no policy evidence)", "INVALID_INPUT": "🚫 INVALID INPUT"}


def run(price, category, coupon, claim):
    r = verify(price, category, coupon, claim)
    summary = f"## {BADGE[r.status]}\n"
    if r.price is not None:
        summary += (f"**Original:** {r.price:.2f} SAR &nbsp;|&nbsp; **Actual discount:** "
                    f"{r.discount:.2f} SAR &nbsp;|&nbsp; **Final price:** {r.final_price:.2f} SAR\n")
    summary += "\n**Source IDs:** " + (", ".join(r.cited_ids) if r.cited_ids else "none")

    warn = "\n".join(f"⚠️ {w}" for w in r.warnings) or "No claim conflicts detected."
    warn_html = f'<div class="dg-card {"dg-warn" if r.warnings else ""}">{warn.replace(chr(10), "<br>")}</div>'

    ev = "\n\n".join(f"**{e['id']}** (cosine {e['score']}): {e['source_text']}" for e in r.evidence) \
        or "_No supporting evidence retrieved._"
    evidence = f"### 📚 Retrieved evidence (TF-IDF + cosine)\n{ev}"

    calc = "\n".join(f"- {s}" for s in r.calculation) or "- No calculation executed."
    rules = "\n".join(f"- {s}" for s in r.reasons)
    calculation = f"### 🧮 Executed calculation (deterministic Python)\n**Rule checks:**\n{rules}\n\n**Steps:**\n{calc}"

    generated = ("### 📝 Explanation (template-generated, **no LLM connected**)\n" + r.explanation)
    return summary, warn_html, evidence, calculation, generated


with gr.Blocks(title="DealGuard", css=CSS, theme=gr.themes.Soft()) as demo:
    gr.HTML('<div class="dg-title"><h1>🛡️ DealGuard</h1>'
            "<p>Verify promotional claims against policy. Synthetic training data only - "
            "no real merchants or offers.</p></div>")
    with gr.Row():
        with gr.Column(scale=1):
            price = gr.Number(label="Product price (SAR)", value=1000, minimum=0)
            category = gr.Dropdown(CATEGORIES, value="Electronics", label="Category")
            coupon = gr.Textbox(label="Coupon code", value="SAVE20")
            claim = gr.Textbox(label="Promotional claim", value="20% off everything!")
            btn = gr.Button("Verify deal", variant="primary")
            gr.Markdown("Known demo codes: " + ", ".join(p["code"] for p in POLICIES))
        with gr.Column(scale=2):
            out_sum = gr.Markdown()
            out_warn = gr.HTML()
            out_ev = gr.Markdown(elem_classes="dg-card dg-evidence")
            out_calc = gr.Markdown(elem_classes="dg-card dg-calc")
            out_gen = gr.Markdown(elem_classes="dg-card dg-gen")
    btn.click(run, [price, category, coupon, claim], [out_sum, out_warn, out_ev, out_calc, out_gen])

if __name__ == "__main__":
    demo.launch()
