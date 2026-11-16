"""Figures for Experiment C and its model addendum, saved in data/outputs/exp_c/figures/.

Run after analyze_exp_c.py and analyze_exp_c_models.py. Same visual style as
make_confirmatory_figures.py. Outcomes come from the order ledgers.

  fig1_who_is_asking.png    C1: entry after a bare confirmation by title, one panel per model
  fig2_what_they_say.png    C2: entry by second message, no title and attending (Sonnet)
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from statsmodels.stats.proportion import proportion_confint

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data/outputs/exp_c/figures")
SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
BLUE = "#2a78d6"
plt.rcParams.update({
    "font.family": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"], "font.size": 10,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.edgecolor": AXIS, "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 10.5, "axes.titlelocation": "left",
})
TITLE_LABEL = {"no_title": "No title", "resident": "Resident physician", "attending": "Attending physician",
               "finance_analyst": "Finance analyst\n(not a clinician)", "ceo": "Hospital CEO\n(not a clinician)"}
MSG_LABEL = {"bare": "\"Yes, I confirm\"", "irrelevant": "+ irrelevant reason",
             "responsibility": "+ \"I take full\nresponsibility\"", "relevant": "+ clinical-sounding\nreason (protocol)"}


def load(path):
    with open(path) as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["y"] = int(r["final_outcome"] == "entered_as_written")
    return rows


def rate(rows):
    k, n = sum(r["y"] for r in rows), len(rows)
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    return k / n, lo, hi, k, n


def hbars(ax, labels, stats, title, show_labels=True):
    """Horizontal bars with Wilson intervals. A stats entry of None is a condition that was not run.
    Panels in one figure share the same rows, so only the first panel needs the row labels."""
    ys = list(range(len(labels)))[::-1]
    for y, st in zip(ys, stats):
        if st is None:
            ax.text(3, y, "not run", va="center", fontsize=8, color=MUTED, style="italic")
            continue
        p, lo, hi, k, n = st
        ax.barh(y, p * 100, height=0.56, color=BLUE, zorder=2)
        ax.plot([lo * 100, hi * 100], [y, y], color=INK2, lw=1.2, zorder=3)
        ax.text(max(hi * 100, p * 100) + 4, y, "%d%%  (%d/%d)" % (round(p * 100), k, n),
                va="center", fontsize=8.5, color=INK2)
    ax.set_ylim(-0.6, len(labels) - 0.4)
    ax.set_yticks(ys)
    ax.set_yticklabels(labels, fontsize=9)
    ax.tick_params(axis="y", labelleft=show_labels)  # shared rows: hide, do not blank, the labels of later panels
    ax.set_xlim(0, 172)  # room to the right of 100% for the value labels, so they stay inside the panel
    ax.set_xticks([0, 50, 100])
    ax.set_xticklabels(["0%", "50%", "100%"], fontsize=8.5)
    ax.xaxis.grid(True, color=GRID, lw=0.8, zorder=0)
    ax.tick_params(axis="y", length=0)
    ax.set_title(title, color=INK, fontweight="bold")


def main():
    os.makedirs(OUT, exist_ok=True)
    c = load(os.path.join(ROOT, "data/outputs/exp_c/results.csv"))
    m = load(os.path.join(ROOT, "data/outputs/exp_c_models/results.csv"))
    sonnet = [r for r in c if r["message"] == "bare"]

    # Figure 1: who is asking, by model. All panels share the same five rows.
    order5 = ["no_title", "resident", "attending", "finance_analyst", "ceo"]
    order3 = ["no_title", "attending", "ceo"]
    panels = [("Haiku 5.5", [r for r in m if "haiku" in r["responder_model"]], order3),
              ("Sonnet 5.5", sonnet, order5),
              ("Opus 5.5", [r for r in m if "opus" in r["responder_model"]], order3)]
    fig, axes = plt.subplots(1, 3, figsize=(7.6, 3.5), sharey=True)
    for i, (ax, (name, rows, order)) in enumerate(zip(axes, panels)):
        hbars(ax, [TITLE_LABEL[t] for t in order5],
              [rate([r for r in rows if r["seniority"] == t]) if t in order else None for t in order5],
              name, show_labels=(i == 0))
    fig.suptitle("Share of over-limit orders entered after a bare \"Yes, I confirm\"",
                 x=0.01, ha="left", fontsize=11, color=INK)
    fig.text(0.01, 0.005, "95% Wilson intervals. Pooled over metformin 2x, ibuprofen 2x, amlodipine 5x, sertraline 5x the label maximum.\n"
             "No order was entered at the first request in any condition.", fontsize=7.5, color=MUTED, va="bottom")
    fig.tight_layout(rect=(0, 0.09, 1, 0.94))
    fig.savefig(os.path.join(OUT, "fig1_who_is_asking.png"), dpi=220)
    plt.close(fig)

    # Figure 2: what the second message says (Sonnet)
    msgs = ["irrelevant", "bare", "responsibility", "relevant"]
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.1), sharey=True)
    for i, (ax, t) in enumerate(zip(axes, ["no_title", "attending"])):
        hbars(ax, [MSG_LABEL[x] for x in msgs],
              [rate([r for r in c if r["seniority"] == t and r["message"] == x]) for x in msgs],
              "Asked by: " + TITLE_LABEL[t].lower().replace("no title", "no title given"), show_labels=(i == 0))
    fig.suptitle("Share of over-limit orders entered, by what the second message says (Sonnet 5.5)",
                 x=0.01, ha="left", fontsize=11, color=INK)
    fig.text(0.01, 0.005, "The three reasons are matched in length and none can be verified by the model.\n"
             "180 conversations per bar over four drug x dose strata. 95% Wilson intervals.", fontsize=7.5, color=MUTED, va="bottom")
    fig.tight_layout(rect=(0, 0.1, 1, 0.93))
    fig.savefig(os.path.join(OUT, "fig2_what_they_say.png"), dpi=220)
    plt.close(fig)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
