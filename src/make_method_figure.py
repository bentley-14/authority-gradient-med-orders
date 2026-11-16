"""Methods diagram for the report, saved as report/figures/fig_methods.png.

Panel A: one conversation (user message -> isolated responder -> enter_order tool ->
ledger -> code checker, with the single second message sent only if the order was not
entered at turn 1). Panel B: the experiment ladder, Stage B -> Experiment C -> model
addendum -> Experiment D, each arrow labeled with the question the previous step raised.

Same visual style as make_exp_c_figures.py. No data is read: the few numbers in panel B
are copied from the analysis files named beside them (see report/CLAIMS_LEDGER.md).

Usage: python3 src/make_method_figure.py   (needs matplotlib)
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "report/figures")
SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
BLUE = "#2a78d6"
BLUE_FILL = "#e9f1fb"
plt.rcParams.update({
    "font.family": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"], "font.size": 8,
    "figure.facecolor": SURFACE, "savefig.facecolor": SURFACE, "text.color": INK,
})
W, H = 7.0, 4.42  # inches; drawn in inch coordinates
BODY = 8.0  # body text size in points; the figure is placed at about 0.9 of its drawn width


def box(ax, x0, y0, w, h, title, body, fill="white", edge=AXIS, lw=0.9, title_color=INK, size=BODY):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=0,rounding_size=0.06",
                                fc=fill, ec=edge, lw=lw, zorder=2))
    cx = x0 + w / 2
    ax.text(cx, y0 + h - 0.09, title, ha="center", va="top", fontsize=size + 0.8, fontweight="bold",
            color=title_color, zorder=3)
    ax.text(cx, y0 + h - 0.31, body, ha="center", va="top", fontsize=size, color=INK2,
            linespacing=1.25, zorder=3)


def arrow(ax, p, q, color=INK2, lw=1.1, style="-|>", ls="-", connection="arc3"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=9, color=color, lw=lw,
                                 linestyle=ls, connectionstyle=connection, zorder=1,
                                 shrinkA=0, shrinkB=0))


def panel_a(ax):
    ax.text(0.02, 4.38, "A   One conversation (every experiment uses this harness)", fontsize=10.5,
            fontweight="bold", va="top", color=INK)
    y0, h, w, gap = 3.13, 0.92, 1.22, 0.215
    xs = [0.02 + i * (w + gap) for i in range(5)]
    box(ax, xs[0], y0, w, h, "User, turn 1", "Claimed title (or\nnone) + order at\n2x to 5x the\nlabel maximum")
    box(ax, xs[1], y0, w, h, "Responder", "claude -p, fresh\nsession; no memory,\nsettings or\nother tools",
        fill=BLUE_FILL, edge=BLUE)
    box(ax, xs[2], y0, w, h, "enter_order", "MCP tool that\naccepts any dose;\nno alerts, no\nhard stops")
    box(ax, xs[3], y0, w, h, "Ledger", "one JSON line\nper tool call")
    box(ax, xs[4], y0, w, h, "Code checker", "entered as written,\nentered modified,\nor not entered")
    ym = y0 + h / 2
    for i in range(4):
        arrow(ax, (xs[i] + w, ym), (xs[i + 1], ym), color=BLUE if i in (1, 2) else INK2)
    ax.text(xs[1] + w + gap / 2, ym + 0.07, "call", ha="center", va="bottom", fontsize=7.5, color=BLUE)

    # Turn 2: only if the order was not entered at turn 1
    t2x, t2y, t2w, t2h = xs[0], 2.33, w + 0.6, 0.62
    ax.add_patch(FancyBboxPatch((t2x, t2y), t2w, t2h, boxstyle="round,pad=0,rounding_size=0.06",
                                fc="white", ec=INK2, lw=0.9, ls=(0, (3, 2)), zorder=2))
    ax.text(t2x + t2w / 2, t2y + t2h - 0.09, "User, turn 2 (one message)", ha="center", va="top",
            fontsize=BODY + 0.8, fontweight="bold", color=INK, zorder=3)
    ax.text(t2x + t2w / 2, t2y + t2h - 0.31, "\"Yes, I confirm\" or a reason,\nvaried by experiment",
            ha="center", va="top", fontsize=BODY, color=INK2, linespacing=1.25, zorder=3)
    # checker -> back to turn 2 (dashed), along the bottom
    cx = xs[4] + w / 2
    yb = 2.2
    xin = t2x + t2w / 2 + 0.25
    ax.plot([cx, cx], [y0, yb], color=INK2, lw=1.0, ls=(0, (3, 2)), zorder=1)
    ax.plot([cx, xin], [yb, yb], color=INK2, lw=1.0, ls=(0, (3, 2)), zorder=1)
    arrow(ax, (xin, yb), (xin, t2y), ls=(0, (3, 2)), lw=1.0)
    ax.text((cx + t2x + t2w) / 2 + 0.2, yb + 0.06,
            "only if not entered at turn 1; the conversation ends after turn 2",
            ha="center", va="bottom", fontsize=BODY, color=INK2, style="italic")
    # turn 2 -> responder
    arrow(ax, (t2x + t2w, t2y + t2h / 2), (xs[1] + w * 0.66, y0),
          connection="angle,angleA=0,angleB=90,rad=0.0")
    ax.text(xs[2] + w / 2 + 0.55, t2y + t2h / 2 + 0.08,
            "Primary outcome: the over-limit order was entered as\nwritten by the end of the conversation, read from\nthe ledger by code (no model judge)",
            ha="center", va="center", fontsize=BODY - 0.3, color=MUTED, linespacing=1.25)


def panel_b(ax):
    ax.text(0.02, 1.99, "B   Each experiment answers the question the previous one left open", fontsize=10.5,
            fontweight="bold", va="top", color=INK)
    y0, h, w, gap = 0.03, 0.96, 1.46, 0.36
    xs = [0.02 + i * (w + gap) for i in range(4)]
    steps = [
        ("Stage B (Sec. 4)", "1,350 conversations;\nsix clinical titles.\nSenior titles up\n(OR 4.32), student down"),
        ("Experiment C (Sec. 5)", "1,980 conversations;\nCEO, analyst 0%;\nprotocol reason 358/360;\nirrelevant reason 1/360"),
        ("Addendum (Sec. 6)", "720 conversations;\nOpus and Haiku:\nCEO 0%, attending\nabove no title"),
        ("Experiment D (Sec. 7)", "1,080 conversations;\nreworded reasons work;\nfalse claim 0/60;\nreminder: 81% to 6%"),
    ]
    for x, (t, b) in zip(xs, steps):
        box(ax, x, y0, w, h, t, b)
    qs = ["Is it seniority or clinical\nrole? Does the reason matter?",
          "Is it one model's quirk?",
          "Is it that one sentence?\nDoes truth matter? Can a\ndeployer close the gate?"]
    for i, q in enumerate(qs):
        p = (xs[i] + w * 0.7, y0 + h)
        r = (xs[i + 1] + w * 0.3, y0 + h)
        arrow(ax, p, r, color=BLUE, lw=1.2, connection="arc3,rad=-0.4")
        mid = (p[0] + r[0]) / 2
        ax.text(mid, y0 + h + 0.33, q, ha="center", va="bottom", fontsize=BODY, color=BLUE,
                style="italic", linespacing=1.2)


def main():
    os.makedirs(OUT, exist_ok=True)
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    panel_a(ax)
    ax.plot([0.02, W - 0.02], [2.09, 2.09], color=GRID, lw=0.8)
    panel_b(ax)
    path = os.path.join(OUT, "fig_methods.png")
    fig.savefig(path, dpi=250, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)
    print("wrote", path)


if __name__ == "__main__":
    main()
