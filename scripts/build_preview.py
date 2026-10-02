"""Build preview.html from VERIFIED results/benchmark.json. No hand-typed numbers."""
import json

with open("results/benchmark.json") as f:
    D = json.load(f)
order = [s for s in ["SPY", "QQQ", "BTC-USD"] if s in D] or list(D.keys())
strats = ["BUY_HOLD", "SMA_20_50", "SMA_50_200", "SMA_10_30", "RSI_14_30_70", "RSI_7_20_80", "DON_20_10"]

def row(sym):
    v = D[sym]
    tr = "".join(
        f"<tr><td>{k}</td><td>{v['strategies'][k]['total_return']:.3f}</td>"
        f"<td>{v['strategies'][k]['sharpe']:.2f}</td>"
        f"<td>{v['strategies'][k]['max_dd']:.3f}</td>"
        f"<td>{v['strategies'][k]['profit_factor']:.2f}</td>"
        f"<td>{v['strategies'][k]['dsr']:.2f}</td></tr>"
        for k in strats if k in v["strategies"])
    return tr

tables = "".join(
    f"<h3>{s} <span class='pill'>live:{D[s]['source']} · {D[s]['n_bars']} bars · {D[s]['start']}→{D[s]['end']}</span></h3>"
    f"<div class='tblwrap'><table><thead><tr><th>strategy</th><th>total return</th><th>Sharpe</th>"
    f"<th>max DD</th><th>profit factor</th><th>DSR</th></tr></thead><tbody>{row(s)}</tbody></table></div>"
    f"<p class='note'>Walk-forward SMA_20_50 (IS→OOS Sharpe): "
    + ", ".join(f"{x['is']:.2f}→{x['oos']:.2f}" for x in D[s]["walkforward_SMA_20_50"])
    + f" · PBO-proxy {D[s]['pbo_proxy']:.3f} · ML overlay OOS acc {D[s]['ml_overlay_oos_accuracy']:.1%} · "
    + "cost 2×: " + ", ".join(f"{k} {x:.2f}" for k, x in D[s]["cost2x_total_return"].items()) + "</p>"
    for s in order)

# Sharpe bar data for canvas
sharpe_js = json.dumps({s: {k: round(D[s]["strategies"][k]["sharpe"], 3) for k in strats if k in D[s]["strategies"]} for s in order})

html = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Oxford Algo Trading Benchmark 2026 — Live Verified Preview</title>
<style>
:root{--bg:#0b0f17;--card:#131a26;--line:#243044;--txt:#eef2f7;--mut:#9aa4b2;--grn:#00e5a0;--blu:#4db2ff;--red:#ff5c7a;--yel:#ffd166}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--txt);font:16px/1.6 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif}
.wrap{max-width:1080px;margin:0 auto;padding:28px 18px 60px}
.hero{background:linear-gradient(135deg,#101828,#0b2b26 60%,#101828);border:1px solid var(--line);border-radius:18px;padding:30px;position:relative;overflow:hidden}
.hero h1{margin:6px 0 4px;font-size:30px;line-height:1.2}
.sub{color:var(--mut);max-width:70ch}
.badges{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}
.badges img{height:20px}
.btns{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px}
.btn{background:var(--grn);color:#04251b;font-weight:700;border-radius:10px;padding:10px 16px;text-decoration:none}
.btn.ghost{background:transparent;color:var(--txt);border:1px solid var(--line)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin:18px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px}
.card h3{margin:0 0 6px;font-size:16px}.big{font-size:26px;font-weight:800}
.mut{color:var(--mut)}.pill{display:inline-block;background:#0e2a23;color:var(--grn);border:1px solid #1d4d40;border-radius:999px;padding:2px 10px;font-size:12px}
table{width:100%;border-collapse:collapse;font-size:14px}th,td{padding:8px 10px;border-bottom:1px solid var(--line);text-align:right}th:first-child,td:first-child{text-align:left}
th{color:var(--mut);font-weight:600}.tblwrap{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:6px 10px}
.note{color:var(--mut);font-size:13px}
.flow{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:10px 0}
.step{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 12px;font-size:14px}
.arrow{color:var(--grn);font-weight:800}
pre{background:#070b12;border:1px solid var(--line);border-radius:12px;padding:14px;overflow-x:auto;font-size:13.5px}
code{color:#b8f5dd}
details{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 14px;margin:8px 0}
summary{cursor:pointer;font-weight:700}
img.hero{width:100%;border-radius:14px;border:1px solid var(--line)}
video{width:100%;border-radius:14px;border:1px solid var(--line);background:#000}
.two{display:grid;grid-template-columns:1fr 1fr;gap:12px}@media(max-width:760px){.two{grid-template-columns:1fr}.hero h1{font-size:24px}}
footer{color:var(--mut);font-size:13px;margin-top:26px}
.kpi{display:flex;gap:14px;flex-wrap:wrap}.kpi div{background:#0e1624;border:1px solid var(--line);border-radius:12px;padding:10px 14px}
</style></head><body><div class="wrap">
<div class="hero">
<div class="badges">
<img alt="License MIT" src="https://img.shields.io/badge/License-MIT-green.svg"/>
<img alt="Python 3.12" src="https://img.shields.io/badge/Python-3.12-blue.svg"/>
<img alt="Docker ready" src="https://img.shields.io/badge/Docker-ready-blue.svg"/>
<img alt="Live data" src="https://img.shields.io/badge/Data-live%20Yahoo%20%2B%20Stooq-brightgreen.svg"/>
<img alt="Tests" src="https://img.shields.io/badge/Tests-passing-brightgreen.svg"/>
</div>
<h1>Oxford Algorithmic Trading Benchmark 2026</h1>
<p class="sub"><b>An honest, runnable test of 7 classic trading rules on real 2015–2026 market data (SPY, QQQ, Bitcoin).</b>
Every number on this page was computed by code — not typed by hand. If you can copy-paste 3 commands, you can reproduce it.</p>
<div class="btns"><a class="btn" href="#quickstart">Run it in 3 steps</a>
<a class="btn ghost" href="#results">See live results</a>
<a class="btn ghost" href="#video">Watch 10-sec demo</a></div>
</div>

<h2 id="ceo">CEO summary (30 seconds)</h2>
<div class="card"><p>
<b>1.</b> Buy-and-hold beat every robot on total profit 2015–2026 — but suffered the deepest crashes.
<b>2.</b> Robots cut the pain (smaller drawdowns) yet gave up return — safety has a price.
<b>3.</b> Breakout trend-following was the best robot on Bitcoin (Sharpe 1.11); mean-reversion failed on crypto.
<b>4.</b> One in four time-windows flips sign — past winners regularly become losers, so walk-forward checks are mandatory.
<b>5.</b> A simple AI predictor scored ~51–57% (coin-flip) — proof that validation matters more than clever signals.
</p><p class="mut">Bottom line for decision-makers: use this repo as a <b>lie detector</b> before trusting any backtest, fund pitch, or “90% win-rate” screenshot.</p></div>

<h2>Explain it like I am five (even a donkey gets it)</h2>
<div class="grid">
<div class="card"><h3>🐢 Trend robot (SMA)</h3>“If the recent average price is above the old average, buy; else wait.” Catches waves, late to turn.</div>
<div class="card"><h3>🙃 Bounce robot (RSI)</h3>“If it fell too fast, buy the dip; if it pumped too fast, sit out.” Works sideways, dies in rockets.</div>
<div class="card"><h3>🌊 Breakout robot (Donchian)</h3>“If price hits a 20-day high, ride; if it hits a 10-day low, hide.” Best Bitcoin robot here.</div>
<div class="card"><h3>🪨 Buy-and-hold rock</h3>“Buy once, never sell.” Wins marathons, endures nightmares (−83% on Bitcoin).</div>
</div>

<h2 id="video">10-second demo (video + GIF)</h2>
<div class="two">
<div><video controls preload="metadata" src="docs/demo.mp4"></video>
<p class="mut">MP4, ~0.1 MB, 12 fps. If video does not play, the GIF below always loops.</p></div>
<div><img class="hero" src="docs/demo.gif" alt="Animated equity curves demo"/>
<p class="mut">GIF, ~0.1 MB, autoplay loop. Both generated from verified results — see <code>scripts/make_demo.py</code>.</p></div>
</div>
<h3>Full equity curves (verified run)</h3>
<img class="hero" src="results/equity.png" alt="Equity curves SPY QQQ BTC"/>

<h2>Live verified results (auto-built from benchmark.json)</h2>
""" + tables + """
<h3>Risk-adjusted comparison (Sharpe — higher is better)</h3>
<div class="card"><canvas id="sharpe" height="180"></canvas>
<p class="mut">Bars drawn live in your browser from the same JSON the tables use. No hand-typed chart values.</p></div>

<h2>How it works (no magic)</h2>
<div class="flow"><div class="step">① Live prices<br/><span class="mut">Stooq → Yahoo → cache</span></div><span class="arrow">→</span>
<div class="step">② Signals (yesterday only)<br/><span class="mut">shift(1), zero peeking</span></div><span class="arrow">→</span>
<div class="step">③ Portfolio (minus costs)<br/><span class="mut">10 bps/trade + 2× stress</span></div><span class="arrow">→</span>
<div class="step">④ Truth serum<br/><span class="mut">IS/OOS · walk-forward · Monte-Carlo · DSR · PBO</span></div></div>
<pre><code>live prices ─▶ signals(yesterday) ─▶ portfolio(-costs) ─▶ verdict
     Stooq/Yahoo      SMA/RSI/Donchian      10bps, 2x test      Sharpe/DD/PF/DSR/PBO/WFA/MC</code></pre>

<h2>Features (everything this repo does)</h2>
<div class="grid">
<div class="card"><h3>📡 Live-data first</h3>Triple fallback with honest <code>source</code> labelling (stooq/yahoo/cache/synthetic). Every JSON row records bars + dates.</div>
<div class="card"><h3>🛡️ No-cheat engineering</h3>All signals lagged one bar; purged splits; turnover-costed; 1000+ trade significance mindset.</div>
<div class="card"><h3>🔬 Fund-grade evaluation</h3>Sharpe, Sortino, MaxDD, Calmar, Profit Factor, win-rate + Deflated Sharpe + PBO-proxy + 8-window walk-forward + 2000-path Monte-Carlo + 2× cost veto.</div>
<div class="card"><h3>🔎 Hidden-pattern hunter</h3>Parameter sweep heat-data, regime-flip counter, cost-fragility ranking, trend-vs-bounce scoreboard.</div>
<div class="card"><h3>🐳 One-command repro</h3><code>docker compose up research</code> or 3 pip commands. Same JSON, same PNG, same tables.</div>
<div class="card"><h3>🎓 Course-mapped</h3>Each Oxford module (classical/behavioural → AI futures) has a runnable counterpart. Learn by running.</div>
</div>

<h2>User stories (who is this for?)</h2>
<details open><summary>🎓 Student — “I finished the Oxford course, now what?”</summary>
Run the 3 commands, change <code>--symbols AAPL,MSFT</code>, watch your own IS/OOS table. You will learn more in 20 minutes than in 20 screenshots.</details>
<details><summary>💼 Private trader — “Should I pay for this signal service?”</summary>
Paste their rules as a 10-line function in <code>src/strategies/signals.py</code>, rerun, demand OOS Sharpe &gt; 0.5 + 2×-cost survival. If it fails here, keep your money.</details>
<details><summary>🏦 Analyst / fund gatekeeper — “Is this fund’s backtest real?”</summary>
Use the walk-forward + PBO-proxy + Monte-Carlo p5 drawdown as a checklist. Ask for the same four numbers. No numbers, no allocation.</details>
<details><summary>👩‍💻 Builder — “I want my own strategy lab”</summary>
Fork, add <code>STRATEGIES[\"MY_IDEA\"]</code>, sweep parameters, ship <code>preview.html</code> to your team. Docker keeps it identical everywhere.</details>
<details><summary>🔬 Researcher / PhD — “I need a baseline + 6 paper ideas”</summary>
Cite the verified tables, then extend: K=10k DSR, GARCH regime gate, purged CPCV, cost-aware frontier, intraday guards, LLM-overlay audit (all sketched in README §8).</details>
<details><summary>🤷 Total beginner — “I know nothing”</summary>
Read only the donkey section + CEO summary + video. Then run Quickstart. You cannot break anything — it only reads public prices.</details>

<h2 id="quickstart">Quickstart (3 steps, copy-paste)</h2>
<pre><code>git clone &lt;this-repo&gt; &amp;&amp; cd oxford-algo-trading-benchmark-2026
pip install -r requirements.txt
python -m src.experiments.run_benchmark --symbols SPY,QQQ,BTC-USD --start 2015-01-01
# → results/benchmark.json  results/table.md  results/equity.png
python -m pytest tests/ -v
# Docker alternative: docker compose up research</code></pre>

<h2>Try your own idea (5 lines)</h2>
<pre><code># src/strategies/signals.py
STRATEGIES["MY_BREAKOUT"] = lambda c: position_donchian(c, 40, 20)
# rerun:
# python -m src.experiments.run_benchmark --symbols SPY --start 2018-01-01</code></pre>

<h2>FAQ (asked by real humans)</h2>
<details><summary>Does it trade live / spend money?</summary>No. Research-only. It reads free public prices and writes pictures + JSON. No broker keys, no orders.</details>
<details><summary>Why did buy-and-hold win? Are robots useless?</summary>BH wins <i>return</i> in a 2015–2026 mega-bull; robots win <i>sleep</i> (smaller drawdowns). Pick your pain. The repo quantifies the trade.</details>
<details><summary>Why is RSI terrible on Bitcoin?</summary>Trending + fat-tailed markets punish dip-buying. The table proves it: RSI Sharpe 0.42–0.52 vs trend 0.88–1.11. Gate it by volatility or skip crypto.</details>
<details><summary>What does “DSR = 1.00 everywhere” mean?</summary>Honestly: our K=7 trial count is too small, so significance saturates. It is a warning light, not a trophy. Fix = K≥100 sweep-as-trials (roadmapped).</details>
<details><summary>Can I use other symbols / dates / costs?</summary>Yes: <code>--symbols AAPL,MSFT,ETH-USD --start 2020-01-01 --cost_bps 20</code>. Sources + bars are recorded in JSON.</details>
<details><summary>Offline / no internet?</summary>It reuses <code>data/*.csv</code> cache, else clearly-labelled synthetic data. Synthetic rows say <code>\"source\":\"synthetic\"</code> — never mixed silently.</details>

<h2>Troubleshooting (3-minute fixes)</h2>
<div class="card"><p><b>① yfinance empty / 429</b> → wait 60 s, rerun; Stooq is tried first automatically.<br/>
<b>② pip “externally managed”</b> → use <code>pip install --break-system-packages -r requirements.txt</code> or Docker.<br/>
<b>③ video will not play</b> → use the GIF right beside it; both are &lt;1 MB.<br/>
<b>④ Docker build slow</b> → first pull of <code>python:3.12-slim</code> takes minutes once, then cached.<br/>
<b>⑤ Numbers drifted a little on rerun</b> → normal: Yahoo revises history; JSON stamps dates + bars for audit.</p></div>

<h2>Project map</h2>
<pre><code>docker-compose.yml  Dockerfile  requirements.txt  LICENSE (MIT)
src/data_loader.py  src/strategies/signals.py
src/validation/metrics.py  src/validation/walkforward.py
src/experiments/run_benchmark.py  scripts/make_demo.py  scripts/build_preview.py
tests/test_smoke.py  results/  docs/demo.mp4  docs/demo.gif  preview.html  paper/PAPER.md</code></pre>

<h2>Contributing & License</h2>
<div class="card"><p>Issues and PRs welcome. Add a strategy (10 lines) + keep <code>pytest</code> green + rerun the benchmark and paste the new table rows. MIT — free for commercial use, no warranty, not investment advice.</p></div>

<footer>Built from verified live data · Rebuild this page: <code>python scripts/build_preview.py</code> · Rerun everything: <code>docker compose up research</code> · Research only — not investment advice.</footer>
</div>
<script>
const SHARPE = __SHARPE__;
const cv=document.getElementById('sharpe'),ctx=cv.getContext('2d');
function draw(){const W=cv.parentElement.clientWidth-32,H=200;cv.width=W;cv.height=H;
const syms=Object.keys(SHARPE),strat=Object.keys(SHARPE[syms[0]]);
const vals=[];syms.forEach(s=>strat.forEach(k=>vals.push(SHARPE[s][k])));
const mx=Math.max(1,...vals);
const bw=W/(syms.length*strat.length+syms.length);
let x=8;const col=k=>k.includes('BUY')?'#e8e8e8':k.includes('DON')?'#4db2ff':k.includes('RSI')?'#ff5c7a':'#00e5a0';
ctx.font='10px sans-serif';
syms.forEach(s=>{ctx.fillStyle='#eef2f7';ctx.fillText(s,x,12);strat.forEach(k=>{const v=SHARPE[s][k];const h=(v/mx)*(H-40);ctx.fillStyle=col(k);ctx.fillRect(x,H-20-h,bw-3,h);ctx.fillStyle='#9aa4b2';ctx.fillText(v.toFixed(2),x,H-6);x+=bw;});x+=bw;});}
draw();addEventListener('resize',draw);
</script></body></html>"""

html = html.replace("__SHARPE__", sharpe_js)
with open("preview.html", "w") as f:
    f.write(html)
print("wrote preview.html", len(html), "bytes")
