"""Figures for Stage B of CONFIRMATORY_PLAN.md, saved in data/outputs/confirmatory/figures/.

Run only after Stage B is complete and analyze_confirmatory.py has been run.
matplotlib is used here only. Outcomes are taken from the order ledger.

Usage: python3 src/make_confirmatory_figures.py [results.csv] [output folder]
(the two optional arguments exist so the layout can be tried on other data)
"""
import csv
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from statsmodels.stats.proportion import proportion_confint

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_confirmatory as a

ROOT = a.ROOT
SEN, SENIOR = a.SEN, a.SENIOR
LABEL = {"no_title": "No title (baseline)", "medical_student": "Medical student", "resident": "Resident",
         "attending": "Attending", "senior_attending": "Senior attending", "department_chair": "Department chair"}
SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
BLUE, GRAY = "#2a78d6", "#898781"

plt.rcParams.update({
    "font.family": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"], "font.size": 10,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.edgecolor": AXIS, "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 10.5, "axes.titlelocation": "left",
})

rows = a.load(sys.argv[1] if len(sys.argv) > 1 else None)
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(a.DIR, "figures")
doses = sorted({r["mult"] for r in rows})


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=220)
    plt.close(fig)
    print("wrote", name)


def headline(fig, title, subtitle):
    fig.text(0.02, 0.975, title, fontsize=13, fontweight="bold", va="top")
    fig.text(0.02, 0.975 - 0.42 / fig.get_figheight(), subtitle, fontsize=9.5, color=INK2, va="top")


def rate(c):
    k, n = sum(r["y"] for r in c), len(c)
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    return k, n, 100.0 * k / n, 100 * lo, 100 * hi


def figure1():
    fig, axes = plt.subplots(1, len(doses), figsize=(4.2 * len(doses) + 2.2, 5.2), squeeze=False)
    fig.subplots_adjust(left=1.9 / fig.get_figwidth(), right=0.97, top=0.74, bottom=0.17, wspace=0.32)
    for ax, d in zip(axes[0], doses):
        for i, t in enumerate(SEN):
            k, n, p, lo, hi = rate([r for r in rows if r["mult"] == d and r["seniority"] == t])
            ax.plot([lo, hi], [i, i], color=BLUE, lw=2, solid_capstyle="round")
            ax.plot([p], [i], "o", color=BLUE, ms=8, mec=SURFACE, mew=1.5)
            ax.text(103, i, "%d of %d" % (k, n), va="center", fontsize=8.5, color=INK2)
        ax.axhline(0.5, color=AXIS, lw=1)
        ax.set_ylim(len(SEN) - 0.5, -0.5)
        ax.set_xlim(-3, 100)
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=8.5)
        ax.set_yticks(range(len(SEN)))
        ax.set_yticklabels([LABEL[t] for t in SEN] if ax is axes[0][0] else [""] * len(SEN), fontsize=9.5)
        ax.grid(axis="x", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(length=0)
        ax.spines["left"].set_visible(False)
        ax.set_title("Dose ordered: %dx the label maximum" % d)
        ax.set_xlabel("Share of orders entered", fontsize=9)
    fig.subplots_adjust(right=1 - 0.75 / fig.get_figwidth())
    headline(fig, "Over-limit orders entered after \"Yes, I confirm\", by who said they were ordering",
             "Dots are the share of orders the AI entered as written. Lines are 95% intervals (Wilson). "
             "Counts are at the right of each row.")
    fig.text(0.02, 0.02, "Stage B, fresh conversations. Outcome is taken from the order-entry tool's ledger. "
             "Each row pools 5 drugs.", fontsize=8, color=MUTED)
    save(fig, "fig1_entry_by_title.png")


def figure2():
    def source(path, keep):
        with open(os.path.join(ROOT, path)) as f:
            out = [r for r in csv.DictReader(f) if r["severity"] in keep]
        for r in out:
            r["y"], r["mult"] = int(r["final_outcome"] == a.AW), int(r["severity"].rstrip("x"))
        return out
    earlier = [("Earlier tool run (15 per point)", source("data/outputs/tool_run/results.csv", ("2x", "10x")), "s"),
               ("Stage A dose finding (15 per point)", source("data/outputs/dose_finding/results.csv", ("3x", "5x")), "D")]
    fig, axes = plt.subplots(2, 3, figsize=(11, 7.2), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.08, right=0.98, top=0.78, bottom=0.11, wspace=0.08, hspace=0.25)
    for ax, t in zip(axes.flat, SEN):
        for name, data, marker in earlier:
            for d in sorted({r["mult"] for r in data}):
                c = [r for r in data if r["mult"] == d and r["seniority"] == t]
                ax.plot([d], [100.0 * sum(r["y"] for r in c) / len(c)], marker, color=SURFACE, mec=GRAY,
                        mew=1.5, ms=7, label=name if (ax is axes.flat[0] and d == min(r["mult"] for r in data)) else None)
        pts = [(d,) + rate([r for r in rows if r["mult"] == d and r["seniority"] == t]) for d in doses]
        for d, k, n, p, lo, hi in pts:
            ax.plot([d, d], [lo, hi], color=BLUE, lw=1.5)
        ax.plot([p[0] for p in pts], [p[3] for p in pts], "-o", color=BLUE, lw=2, ms=8, mec=SURFACE, mew=1.5,
                label="Stage B confirmatory (75 per point, with 95% interval)" if ax is axes.flat[0] else None)
        ax.set_xscale("log")
        ax.set_xticks([2, 3, 5, 10])
        ax.set_xticklabels(["2x", "3x", "5x", "10x"])
        ax.set_xticks([], minor=True)
        ax.set_xlim(1.7, 11.8)
        ax.set_ylim(-4, 104)
        ax.set_yticks([0, 50, 100])
        ax.set_yticklabels(["0%", "50%", "100%"])
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(length=0)
        ax.set_title(LABEL[t])
    for ax in axes[1]:
        ax.set_xlabel("Dose ordered, as a multiple of the label maximum", fontsize=9)
    for ax in axes[:, 0]:
        ax.set_ylabel("Share of orders entered", fontsize=9)
    handles, labels = axes.flat[0].get_legend_handles_labels()
    order = [labels.index(l) for l in sorted(labels, key=lambda l: not l.startswith("Stage B"))]
    fig.legend([handles[i] for i in order], [labels[i] for i in order], loc="upper left",
               bbox_to_anchor=(0.02, 0.895), ncol=3, frameon=False, fontsize=9, columnspacing=2.2)
    headline(fig, "How the share of over-limit orders entered falls as the dose rises, for each stated title",
             "Share entered as written after \"Yes, I confirm\". Three sets of conversations are shown. "
             "Only Stage B is used in the statistical tests.")
    fig.text(0.02, 0.015, "Outcome is taken from the order-entry tool's ledger. Each point pools 5 drugs. "
             "The earlier tool run and Stage A are exploratory and shown for context only.", fontsize=8, color=MUTED)
    save(fig, "fig2_entry_by_dose.png")


def figure3():
    items = [("Medical student (H1, primary)", a.cmh(rows, ["medical_student"]), True),
             ("Resident", a.cmh(rows, ["resident"]), False),
             ("Attending", a.cmh(rows, ["attending"]), False),
             ("Senior attending", a.cmh(rows, ["senior_attending"]), False),
             ("Department chair", a.cmh(rows, ["department_chair"]), False),
             ("Attending, senior attending and\nchair pooled (H2, primary)", a.cmh(rows, SENIOR), True)]
    fig, ax = plt.subplots(figsize=(9.5, 5.4))
    fig.subplots_adjust(left=0.33, right=0.80, top=0.76, bottom=0.17)
    finite = [v for _, c, _ in items for v in (c["or"], c["lo"], c["hi"]) if v == v and 0 < v < float("inf")]
    xmin = min([0.5] + finite) / 1.5
    xmax = max([2.0] + finite) * 1.5
    for i, (name, c, primary) in enumerate(items):
        ok = c["or"] == c["or"] and 0 < c["or"] < float("inf") and c["lo"] == c["lo"]
        if ok:
            ax.plot([c["lo"], c["hi"]], [i, i], color=BLUE, lw=2, solid_capstyle="round")
            ax.plot([c["or"]], [i], "o" if primary else "o", color=BLUE if primary else SURFACE,
                    ms=9, mec=BLUE if not primary else SURFACE, mew=1.5)
            text = "%.2f (%.2f to %.2f)" % (c["or"], c["lo"], c["hi"])
        else:
            text = a.or_text(c).split(" (")[0] + ", no interval"
        ax.annotate(text, (1.02, i), xycoords=("axes fraction", "data"), va="center", fontsize=8.5,
                    color=INK2, annotation_clip=False)
    ax.axvline(1, color=AXIS, lw=1)
    ax.set_xscale("log")
    ax.set_xlim(xmin, xmax)
    ticks = [t for t in (0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20) if xmin <= t <= xmax]
    ax.set_xticks(ticks)
    ax.set_xticklabels([("%g" % t) for t in ticks])
    ax.set_xticks([], minor=True)
    ax.set_ylim(len(items) - 0.5, -0.5)
    ax.set_yticks(range(len(items)))
    ax.set_yticklabels([n for n, _, _ in items], fontsize=9.5)
    ax.axhline(len(items) - 1.5, color=AXIS, lw=1)
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Odds ratio against the untitled user (log scale)\nleft of 1: entered less often      right of 1: entered more often", fontsize=9)
    ax.annotate("Odds ratio (95% CI)", (1.02, 1.03), xycoords="axes fraction", fontsize=8.5, color=MUTED,
                annotation_clip=False)
    headline(fig, "Each title compared with an untitled user: odds of an over-limit order being entered",
             "Mantel-Haenszel odds ratios with 95% intervals, comparing within the same drug and dose. "
             "Filled dots are the two pre-registered tests.")
    fig.text(0.02, 0.02, "Stage B, fresh conversations. Outcome is taken from the order-entry tool's ledger. "
             "Open dots are secondary comparisons.", fontsize=8, color=MUTED)
    save(fig, "fig3_odds_ratios.png")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    figure1()
    figure2()
    figure3()
