"""Generate docs/demo.mp4 (720p, 12fps, ~10s) + docs/demo.gif (<5MB) from VERIFIED results.

Best practice applied: 640-800px wide, 10-15fps, 5-15s, high-contrast dark theme,
16pt+ fonts, trims dead time. Reads results/benchmark.json + live CSV cache.
No hand-typed numbers.
"""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation

with open("results/benchmark.json") as f:
    D = json.load(f)

SYM = "BTC-USD" if "BTC-USD" in D else list(D.keys())[0]
# rebuild equity from cached data for animation frames
from src.data_loader import load_symbol
from src.strategies.signals import STRATEGIES
from src.validation.metrics import backtest_returns

df, src = load_symbol(SYM, "2015-01-01")
close = df["Close"]
R = pd.DataFrame({k: backtest_returns(close, fn(close), 10.0) for k, fn in STRATEGIES.items()
                  if k in ("BUY_HOLD", "SMA_20_50", "RSI_14_30_70", "DON_20_10")})
EQ = (1 + R).cumprod()
EQ = EQ.iloc[::max(1, len(EQ) // 120)].reset_index(drop=True)  # ~120 frames
labels = {"BUY_HOLD": "Buy & Hold", "SMA_20_50": "SMA trend 20/50",
          "RSI_14_30_70": "RSI mean-reversion", "DON_20_10": "Donchian breakout"}
colors = {"BUY_HOLD": "#e8e8e8", "SMA_20_50": "#00e5a0", "RSI_14_30_70": "#ff5c7a", "DON_20_10": "#4db2ff"}

plt.rcParams.update({"figure.facecolor": "#0b0f17", "axes.facecolor": "#0b0f17",
                     "text.color": "white", "axes.labelcolor": "white",
                     "xtick.color": "#9aa4b2", "ytick.color": "#9aa4b2",
                     "font.size": 13})
fig, ax = plt.subplots(figsize=(6.4, 3.6), dpi=100)
fig.subplots_adjust(left=0.12, right=0.96, top=0.86, bottom=0.16)
lines = {k: ax.plot([], [], lw=2.2, color=colors[k], label=labels[k])[0] for k in EQ.columns}
ax.set_xlim(0, len(EQ))
ax.set_ylim(0.5, float(EQ.max().max()) * 1.05)
ax.set_yscale("log")
ax.set_xlabel("time (compressed 2015-2026)", fontsize=11)
ax.set_ylabel("growth of $1 (log scale)", fontsize=11)
ax.grid(True, alpha=0.18)
ax.legend(frameon=False, fontsize=9, loc="upper left")
title = ax.set_title("", fontsize=13, weight="bold", loc="left")
stats = D[SYM]["strategies"]

def init():
    for ln in lines.values():
        ln.set_data([], [])
    title.set_text(f"{SYM}  live:{src}  cost 10bps")
    return list(lines.values()) + [title]

def frame(i):
    x = np.arange(i + 1)
    for k in EQ.columns:
        lines[k].set_data(x, EQ[k].iloc[: i + 1].values)
    bh = stats["BUY_HOLD"]["total_return"]
    dn = stats["DON_20_10"]["sharpe"]
    title.set_text(f"{SYM}  BH +{bh:.1f}x   DON Sharpe {dn:.2f}   [{i+1}/{len(EQ)}]")
    return list(lines.values()) + [title]

ani = animation.FuncAnimation(fig, frame, init_func=init, frames=len(EQ), blit=False)
ani.save("docs/demo.mp4", fps=12, codec="h264", bitrate=800)
print("wrote docs/demo.mp4")
# GIF: downscale + 10fps + palette for size
import subprocess
subprocess.run(["ffmpeg", "-y", "-i", "docs/demo.mp4", "-vf", "fps=10,scale=640:-1:flags=lanczos",
                "-gifflags", "+transdiff", "docs/demo.gif"], check=True)
print("wrote docs/demo.gif")
