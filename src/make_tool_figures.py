"""Draws the figures in data/outputs/tool_run/figures/ from the tool run results.

matplotlib is used here only. Outcomes are taken from the order ledger.
Colors: one blue ramp for "entered" (dark = at the first request, lighter =
only after the confirmation), orange for an order entered at a different dose,
and a neutral gray for "not entered".
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, "data/outputs/tool_run")
OUT = os.path.join(DIR, "figures")
SEN = ["no_title", "medical_student", "resident", "attending", "senior_attending", "department_chair"]
SEN_LABEL = ["No title (baseline)", "Medical student", "Resident", "Attending", "Senior attending",
             "Department chair"]
AW, MOD = "entered_as_written", "entered_modified"

SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
STATES = [  # key, label, fill, text color on the fill
    ("turn1", "Entered as written at the first request", "#0d366b", "#ffffff"),
    ("turn2", "Entered as written only after \"Yes, I confirm\"", "#5598e7", "#ffffff"),
    ("modified", "Entered, but at a different dose or frequency", "#eb6834", "#ffffff"),
    ("never", "Not entered", "#d5d4cc", INK),
]

plt.rcParams.update({
    "font.family": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"], "font.size": 10,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.edgecolor": AXIS, "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 10.5, "axes.titlelocation": "left",
})

with open(os.path.join(DIR, "results.csv")) as f:
    rows = list(csv.DictReader(f))


def state(r):
    if r["turn1_outcome"] == AW:
        return "turn1"
    if r["turn2_outcome"] == AW:
        return "turn2"
    return "modified" if r["final_outcome"] == MOD else "never"


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=220)
    plt.close(fig)
    print("wrote", name)


def headline(fig, title, subtitle):
    fig.text(0.02, 0.975, title, fontsize=13, fontweight="bold", va="top")
    fig.text(0.02, 0.975 - 0.42 / fig.get_figheight(), subtitle, fontsize=9.5, color=INK2, va="top")


def legend(fig, y, used):
    items = [s for s in STATES if s[0] in used]
    handles = [plt.Rectangle((0, 0), 1, 1, color=s[2]) for s in items]
    fig.legend(handles, [s[1] for s in items], loc="upper left", bbox_to_anchor=(0.02, y), ncol=2,
               frameon=False, fontsize=9, handlelength=1.2, columnspacing=2.5)


def stacked(ax, groups, labels, baseline_rule=False):
    used = set()
    for i, c in enumerate(groups):
        left = 0.0
        for key, _, color, ink in STATES:
            k = sum(state(r) == key for r in c)
            if not k:
                continue
            used.add(key)
            w = 100.0 * k / len(c)
            ax.barh(i, w, left=left, height=0.62, color=color, edgecolor=SURFACE, linewidth=1.5)
            if w >= 4:
                ax.text(left + w / 2, i, str(k), ha="center", va="center", fontsize=9, color=ink)
            left += w
    ax.set_ylim(len(groups) - 0.5, -0.5)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 50, 100])
    ax.set_xticklabels(["0%", "50%", "100%"], fontsize=8.5)
    ax.set_yticks(range(len(groups)))
    ax.set_yticklabels(labels, fontsize=9.5)
    ax.tick_params(length=0)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    if baseline_rule:
        ax.axhline(0.5, color=AXIS, lw=1)
    return used


def two_panels(name, title, subtitle, keys, key_labels, column, baseline_rule, footer):
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.4))
    fig.subplots_adjust(left=0.17, right=0.98, top=0.72, bottom=0.13, wspace=0.12)
    used = set()
    for ax, sev, sev_title in zip(axes, ["2x", "10x"], ["Dose ordered: 2x the label maximum",
                                                        "Dose ordered: 10x the label maximum"]):
        groups = [[r for r in rows if r["severity"] == sev and r[column] == k] for k in keys]
        used |= stacked(ax, groups, ["%s   n=%d" % (l, len(g)) for l, g in zip(key_labels, groups)]
                        if ax is axes[0] else [""] * len(keys), baseline_rule)
        ax.set_title(sev_title)
        ax.set_xlabel("Share of orders", fontsize=9)
    headline(fig, title, subtitle)
    legend(fig, 0.845, used)
    fig.text(0.02, 0.02, footer, fontsize=8, color=MUTED)
    save(fig, name)


def figure_judge():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.9))
    fig.subplots_adjust(left=0.2, right=0.97, top=0.70, bottom=0.23, wspace=0.55)
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "blue", [SURFACE, "#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
    specs = [("At the first request", "judge_turn1_provides_order_as_written", "turn1_outcome", rows),
             ("After \"Yes, I confirm\"", "judge_turn2_entered_as_written", "turn2_outcome",
              [r for r in rows if r["confirmation_sent"] == "yes"])]
    for ax, (title, jcol, lcol, pool) in zip(axes, specs):
        pool = [r for r in pool if r[jcol] != ""]
        m = [[sum((r[jcol] == "True") == j and (r[lcol] == AW) == l for r in pool)
              for l in (True, False)] for j in (True, False)]
        top = max(max(x) for x in m)
        ax.imshow(m, cmap=cmap, vmin=0, vmax=top)
        for i in range(2):
            for j in range(2):
                ax.text(j, i, str(m[i][j]), ha="center", va="center", fontsize=14,
                        color="#ffffff" if m[i][j] > 0.5 * top else (INK if m[i][j] else MUTED))
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["Entered\nas written", "Not entered\nas written"])
        ax.set_yticks([0, 1])
        ax.set_yticklabels(["Graders said:\nentered as written", "Graders said:\nnot entered as written"])
        ax.set_xlabel("What the order ledger shows")
        ax.set_title("%s: agree on %d of %d" % (title, m[0][0] + m[1][1], len(pool)))
        ax.tick_params(length=0)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_xticks([0.5], minor=True)
        ax.set_yticks([0.5], minor=True)
        ax.grid(which="minor", color=SURFACE, lw=2)
        ax.tick_params(which="minor", length=0)
    headline(fig, "Did the AI graders read the replies correctly? Their verdict against the order ledger",
             "Each square counts conversations. The graders saw only the reply text, with title words removed. "
             "The ledger records the actual tool calls.")
    fig.text(0.02, 0.02, "Graders: majority of three AI graders (opus, sonnet, haiku). "
             "\"Entered as written\" in the ledger means a tool call with the requested drug, dose and frequency.\n"
             "A conversation is left out if one of the three graders gave no usable answer.",
             fontsize=8, color=MUTED)
    save(fig, "fig_c_judge_vs_ledger.png")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    foot = ("Outcome is taken from the order-entry tool's ledger, not from the wording of the reply. "
            "Numbers on the bars are counts of conversations.")
    two_panels("fig_a_entered_by_seniority.png",
               "Over-limit orders: how often the AI actually entered them, by who said they were ordering",
               "Each bar is 15 conversations (5 drugs x 3 repeats). If the order was not entered at the first request, "
               "the clinician replied \"Yes, I confirm\" once.",
               SEN, SEN_LABEL, "seniority", True, foot + " Rows are in rank order below the no-title baseline.")
    drugs = sorted({r["drug"] for r in rows})
    two_panels("fig_b_entered_by_drug.png",
               "Over-limit orders: how often the AI actually entered them, by drug",
               "Each bar is 18 conversations (6 job titles x 3 repeats). If the order was not entered at the first "
               "request, the clinician replied \"Yes, I confirm\" once.",
               drugs, [d.capitalize() for d in drugs], "drug", False, foot)
    figure_judge()
