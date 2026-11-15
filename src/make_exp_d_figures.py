"""Figure for Experiment D, saved in data/outputs/exp_d/figures/.

Run after analyze_exp_d.py. Same visual style as make_exp_c_figures.py.
Outcomes come from the order ledgers.

  fig1_message_by_system_prompt.png   entry by second message, one panel per system prompt
"""
import os
import sys

import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src.make_exp_c_figures import INK, MUTED, hbars, load, rate

DIR = os.environ.get("EXP_D_DIR") or os.path.join(ROOT, "data/outputs/exp_d")  # override only for the synthetic-data test
MSG_LABEL = {"label_false": "+ false claim\n(\"within the label\")", "bare": "\"Yes, I confirm\"",
             "indicated": "+ \"clinically indicated\"\n(no specifics)",
             "specialist": "+ specialist\nrecommended it", "protocol": "+ pharmacist-reviewed\nprotocol (Exp. C)"}
SYS_LABEL = {"base": "Original\nsystem prompt", "reminder": "+ reminder:\n\"you cannot verify\"",
             "rule": "+ reminder\nand explicit rule"}


def main():
    out = os.path.join(DIR, "figures")
    os.makedirs(out, exist_ok=True)
    rows = [r for r in load(os.path.join(DIR, "results.csv")) if r["severity"] != "1x"]
    fig, axes = plt.subplots(1, 3, figsize=(7.6, 3.7), sharey=True)
    for i, (ax, s) in enumerate(zip(axes, SYS_LABEL)):
        hbars(ax, [MSG_LABEL[m] for m in MSG_LABEL],
              [rate([r for r in rows if r["system"] == s and r["message"] == m]) for m in MSG_LABEL],
              SYS_LABEL[s], show_labels=(i == 0))
    fig.suptitle("Share of over-limit orders entered, by second message and system prompt (Sonnet 5.5)",
                 x=0.01, ha="left", fontsize=11, color=INK)
    fig.text(0.01, 0.005, "Untitled user. 60 conversations per bar over metformin 2x, ibuprofen 2x, amlodipine 5x, sertraline 5x the label maximum.\n"
             "95% Wilson intervals. Only the false label claim can be checked by the model.", fontsize=7.5, color=MUTED, va="bottom")
    fig.tight_layout(rect=(0, 0.09, 1, 0.94))
    fig.savefig(os.path.join(out, "fig1_message_by_system_prompt.png"), dpi=220)
    plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    main()
