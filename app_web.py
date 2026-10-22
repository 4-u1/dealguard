"""DealGuard - stdlib-only web UI (fallback when Gradio/pandas cannot load).

Run: python app_web.py [port]   ->  http://127.0.0.1:8765
Uses only http.server + the existing policies/verifier/retriever modules.
"""
import json
import sys
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from policies import CATEGORIES, POLICIES
from verifier import verify

HOST = "127.0.0.1"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 8765
MAX_BODY = 4096
ALLOWED_HOSTS = {f"127.0.0.1:{PORT}", f"localhost:{PORT}"}

PAGE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DealGuard - Promotion Claim Verifier</title>
<meta name="description" content="DealGuard verifies promotional claims against policy. Synthetic training data only.">
<style>
:root{--bg:#0b1020;--card:#ffffff;--ink:#0f172a;--mut:#64748b;--teal:#0f766e;--ind:#4338ca}
*{box-sizing:border-box}
body{margin:0;font-family:"Segoe UI",system-ui,sans-serif;color:var(--ink);min-height:100vh;
background:radial-gradient(1200px 600px at 10% -10%,#1e3a8a55,transparent),
radial-gradient(900px 500px at 100% 0,#0f766e55,transparent),var(--bg)}
.wrap{max-width:1100px;margin:0 auto;padding:24px 16px 48px}
header{background:linear-gradient(120deg,var(--teal),var(--ind));color:#fff;border-radius:18px;
padding:26px 28px;box-shadow:0 12px 40px #0006;animation:in .6s ease}
header h1{margin:0;font-size:2rem}header p{margin:6px 0 0;opacity:.92}
.tag{display:inline-block;margin-top:12px;background:#ffffff26;border:1px solid #ffffff55;
padding:4px 12px;border-radius:99px;font-size:.8rem;font-weight:600}
main{display:grid;grid-template-columns:minmax(260px,1fr) 2fr;gap:18px;margin-top:18px}
@media(max-width:800px){main{grid-template-columns:1fr}}
.panel{background:var(--card);border-radius:16px;padding:20px;box-shadow:0 8px 28px #0004;animation:in .6s ease}
label{display:block;font-weight:600;font-size:.85rem;margin:12px 0 5px}
input,select{width:100%;padding:10px 12px;border:1px solid #cbd5e1;border-radius:10px;font:inherit;
transition:border .15s,box-shadow .15s}
input:focus,select:focus{outline:0;border-color:var(--ind);box-shadow:0 0 0 3px #4338ca33}
button{margin-top:18px;width:100%;padding:12px;border:0;border-radius:10px;font:inherit;font-weight:700;
color:#fff;background:linear-gradient(120deg,var(--teal),var(--ind));cursor:pointer;transition:transform .15s,filter .15s}
button:hover{transform:translateY(-2px);filter:brightness(1.1)}button:disabled{opacity:.6;cursor:wait}
.hint{font-size:.8rem;color:var(--mut);margin-top:14px}
.chip{display:inline-block;margin:2px;padding:2px 8px;border-radius:99px;background:#e0e7ff;color:#3730a3;
font-size:.75rem;cursor:pointer;border:0;width:auto;margin-top:2px;font-weight:600}
.chip:hover{transform:none;filter:none;background:#c7d2fe}
.badge{font-size:1.5rem;font-weight:800;margin:0 0 10px}
.ELIGIBLE{color:#15803d}.INELIGIBLE{color:#b91c1c}.REFUSED{color:#b45309}.INVALID_INPUT{color:#9f1239}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:12px}
@media(max-width:500px){.stats{grid-template-columns:1fr}}
.stat{background:#f1f5f9;border-radius:12px;padding:10px 12px}
.stat small{color:var(--mut);display:block}.stat b{font-size:1.2rem}
.card{border-radius:12px;padding:12px 16px;margin:10px 0;border:1px solid;animation:in .4s ease}
.card h3{margin:0 0 6px;font-size:1rem}.card ul{margin:4px 0;padding-left:20px}
.ev{background:#eff6ff;border-color:#93c5fd}.calc{background:#f0fdf4;border-color:#86efac}
.gen{background:#fffbeb;border-color:#fcd34d}.warn{background:#fef2f2;border-color:#fca5a5;color:#991b1b;font-weight:600}
.ok{background:#f8fafc;border-color:#e2e8f0}
.src{margin:6px 0;padding-bottom:6px;border-bottom:1px dashed #bfdbfe}.src:last-child{border:0}
.empty{color:var(--mut);text-align:center;padding:40px 0}
footer{color:#94a3b8;text-align:center;margin-top:22px;font-size:.8rem}
@keyframes in{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
</style></head><body><div class="wrap">
<header><h1>&#128737;&#65039; DealGuard</h1>
<p>Verify promotional claims against policy - SDAIA Academy demo.</p>
<span class="tag">SYNTHETIC DATA ONLY - fictional policies, no real merchants or offers</span></header>
<main>
<section class="panel" aria-label="Deal inputs"><form id="f" autocomplete="off">
<label for="price">Product price (SAR)</label>
<input id="price" type="number" min="0.01" max="1000000" step="0.01" value="1000" required>
<label for="category">Category</label><select id="category"></select>
<label for="coupon">Coupon code</label>
<input id="coupon" maxlength="20" value="SAVE20" pattern="[A-Za-z0-9]{0,20}">
<label for="claim">Promotional claim</label>
<input id="claim" maxlength="300" value="20% off everything!">
<button id="go" type="submit">Verify deal</button></form>
<p class="hint">Known demo codes (click to fill):<br><span id="codes"></span></p></section>
<section class="panel" id="out" aria-live="polite"><div class="empty">Enter a deal and press <b>Verify deal</b>.</div></section>
</main>
<footer>Retrieval: TF-IDF + cosine &middot; Rules &amp; math: deterministic Python &middot; No LLM connected</footer>
</div>
<script>
const CFG=__CONFIG__;
const BADGE={ELIGIBLE:"\u2705 ELIGIBLE",INELIGIBLE:"\u274C NOT ELIGIBLE",
REFUSED:"\u26A0\uFE0F REFUSED (no policy evidence)",INVALID_INPUT:"\uD83D\uDEAB INVALID INPUT"};
const $=id=>document.getElementById(id);
function esc(s){return String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
const li=a=>a.map(x=>"<li>"+esc(x)+"</li>").join("");
CFG.categories.forEach(c=>{const o=document.createElement("option");o.value=o.textContent=c;
if(c==="Electronics")o.selected=true;$("category").appendChild(o)});
CFG.codes.forEach(c=>{const b=document.createElement("button");b.type="button";b.className="chip";
b.textContent=c;b.onclick=()=>{$("coupon").value=c};$("codes").appendChild(b)});
function render(r){
 let h='<p class="badge '+esc(r.status)+'">'+esc(BADGE[r.status]||r.status)+"</p>";
 if(r.price!==null){h+='<div class="stats"><div class="stat"><small>Original</small><b>'+r.price.toFixed(2)+
 ' SAR</b></div><div class="stat"><small>Actual discount</small><b>'+r.discount.toFixed(2)+
 ' SAR</b></div><div class="stat"><small>Final price</small><b>'+r.final_price.toFixed(2)+" SAR</b></div></div>"}
 h+="<p><b>Source IDs:</b> "+(r.cited_ids.length?esc(r.cited_ids.join(", ")):"none")+"</p>";
 h+='<div class="card '+(r.warnings.length?"warn":"ok")+'">'+(r.warnings.length?
  r.warnings.map(w=>"&#9888;&#65039; "+esc(w)).join("<br>"):"No claim conflicts detected.")+"</div>";
 h+='<div class="card ev"><h3>&#128218; Retrieved evidence (TF-IDF + cosine) - synthetic policies</h3>'+
  (r.evidence.length?r.evidence.map(e=>'<div class="src"><b>'+esc(e.id)+"</b> (cosine "+esc(e.score)+"): "+
  esc(e.source_text)+"</div>").join(""):"<i>No supporting evidence retrieved.</i>")+"</div>";
 h+='<div class="card calc"><h3>&#129518; Executed calculation (deterministic Python)</h3><b>Rule checks:</b><ul>'+
  li(r.reasons)+"</ul><b>Steps:</b><ul>"+(r.calculation.length?li(r.calculation):"<li>No calculation executed.</li>")+"</ul></div>";
 h+='<div class="card gen"><h3>&#128221; Explanation (template-generated, no LLM connected)</h3>'+esc(r.explanation)+"</div>";
 $("out").innerHTML=h}
$("f").addEventListener("submit",async e=>{
 e.preventDefault();$("go").disabled=true;
 const body={price:$("price").value,category:$("category").value,coupon:$("coupon").value,claim:$("claim").value};
 try{const res=await fetch("/api/verify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
  const d=await res.json();
  if(!res.ok)$("out").innerHTML='<div class="card warn">'+esc(d.error||"Request failed")+"</div>";else render(d)}
 catch(err){$("out").innerHTML='<div class="card warn">Server unreachable.</div>'}
 $("go").disabled=false});
</script></body></html>"""

CONFIG = {"categories": list(CATEGORIES), "codes": [p["code"] for p in POLICIES]}
# "<" escaped so embedded JSON can never close the script tag
PAGE_BYTES = PAGE.replace("__CONFIG__", json.dumps(CONFIG).replace("<", "\\u003c")).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = "DealGuard"

    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj).encode("utf-8"), "application/json; charset=utf-8")

    def _host_ok(self):  # blocks DNS-rebinding style requests
        return self.headers.get("Host", "") in ALLOWED_HOSTS

    def do_GET(self):
        if not self._host_ok():
            return self._json(403, {"error": "Forbidden host."})
        if self.path in ("/", "/index.html"):
            self._send(200, PAGE_BYTES, "text/html; charset=utf-8")
        else:
            self._json(404, {"error": "Not found."})

    def do_POST(self):
        if not self._host_ok():
            return self._json(403, {"error": "Forbidden host."})
        if self.path != "/api/verify":
            return self._json(404, {"error": "Not found."})
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return self._json(400, {"error": "Bad Content-Length."})
        if length <= 0 or length > MAX_BODY:
            return self._json(413, {"error": "Request body missing or too large."})
        try:
            data = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return self._json(400, {"error": "Invalid JSON."})
        if not isinstance(data, dict):
            return self._json(400, {"error": "JSON object expected."})
        fields = {k: data.get(k, "") for k in ("price", "category", "coupon", "claim")}
        if not all(isinstance(v, str) for v in fields.values()):
            return self._json(400, {"error": "All fields must be strings."})
        # verify() performs the real validation (price, category, coupon, claim length)
        self._json(200, asdict(verify(fields["price"], fields["category"], fields["coupon"], fields["claim"])))

    def log_message(self, fmt, *args):
        sys.stderr.write("[DealGuard] %s\n" % (fmt % args))


if __name__ == "__main__":
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"DealGuard fallback UI running at http://{HOST}:{PORT}  (Ctrl+C to stop)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        srv.server_close()
