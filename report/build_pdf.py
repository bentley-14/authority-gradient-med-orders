"""Builds report/apart_submission.pdf from report/apart_submission.md through LaTeX.

The Markdown is the single source. This script converts the small subset of Markdown the
report uses (headings, paragraphs with **bold** / *italic* / `code`, numbered and bulleted
lists, pipe tables, images followed by an italic caption line) into
report/latex/apart_submission.tex, laid out like the Apart Research submission template
(Old Standard TT serif, centered title with the sprint footnote, authors, "With Apart
Research", boxed abstract, numbered sections), then compiles it with tectonic.

It also prints the page on which the main text ends (the end of the Conclusion; figures
from the main text are forced out before that point) and the total page count.

Usage: python3 report/build_pdf.py   (needs tectonic on PATH or at /opt/homebrew/bin)
"""
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "apart_submission.md")
TEXDIR = os.path.join(HERE, "latex")
TEX = os.path.join(TEXDIR, "apart_submission.tex")
PDF = os.path.join(HERE, "apart_submission.pdf")
FOOTNOTE = "Research conducted at the AI x Epistemics Research Sprint, November 2026"
MAIN_END_BEFORE = "Code and Data"  # first heading after the main text

PREAMBLE = r"""\documentclass[11pt]{article}
\usepackage[letterpaper,margin=1in]{geometry}
\usepackage{fontspec}
\setmainfont{OldStandard}[Extension=.otf,UprightFont=*-Regular,BoldFont=*-Bold,ItalicFont=*-Italic]
\usepackage{graphicx}
\usepackage{tabularx}
\usepackage{booktabs}
\usepackage{array}
\usepackage{xcolor}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{caption}
\usepackage{placeins}
\usepackage{needspace}
\usepackage[hyphens]{xurl}
\usepackage[hidelinks]{hyperref}
\linespread{1.0}
\setlength{\parindent}{0pt}
\setlength{\parskip}{3.5pt plus 1pt}
\titleformat{\section}{\fontsize{14}{17}\selectfont\bfseries}{}{0pt}{}
\titlespacing*{\section}{0pt}{11pt}{3pt}
\titleformat{\subsection}{\fontsize{12}{15}\selectfont\bfseries}{}{0pt}{}
\titlespacing*{\subsection}{0pt}{7pt}{2pt}
\setlist{nosep,leftmargin=1.6em,itemsep=1.5pt}
\renewcommand{\arraystretch}{1.15}
\setlength{\textfloatsep}{9pt plus 2pt minus 2pt}
\setlength{\floatsep}{8pt plus 2pt}
\setlength{\intextsep}{8pt plus 2pt}
\renewcommand{\topfraction}{0.9}
\renewcommand{\bottomfraction}{0.8}
\renewcommand{\textfraction}{0.1}
\renewcommand{\floatpagefraction}{0.75}
\graphicspath{{../}}
\newcolumntype{Y}{>{\raggedright\arraybackslash}X}
\begin{document}
"""


def esc(s):
    s = s.replace("\\", r"\textbackslash{}")
    for a, b in (("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"), ("_", r"\_"),
                 ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}")):
        s = s.replace(a, b)
    s = s.replace(r"\textbackslash\{\}", r"\textbackslash{}")
    return s


def quotes(s):
    out, prev = [], " "
    for ch in s:
        if ch == '"':
            out.append("``" if prev in " ([/\u00a0" or prev == "" else "''")
        else:
            out.append(ch)
        prev = ch
    return "".join(out)


URL = re.compile(r"(https?://\S+?)(?=[\s,;)]|\.(?:\s|$)|$)")


def inline(text):
    """Markdown inline -> LaTeX. Handles **bold**, *italic*, `code` and bare URLs."""
    parts = re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|https?://\S+)", text)
    out = []
    for tok in parts:
        if not tok:
            continue
        if tok.startswith("**") and tok.endswith("**"):
            out.append(r"\textbf{%s}" % inline(tok[2:-2]))
        elif tok.startswith("`") and tok.endswith("`"):
            out.append(r"\texttt{%s}" % esc(tok[1:-1]))
        elif tok.startswith("*") and tok.endswith("*") and len(tok) > 2:
            out.append(r"\emph{%s}" % inline(tok[1:-1]))
        elif tok.startswith("http"):
            trail = ""
            while tok and tok[-1] in ".,;)":
                trail, tok = tok[-1] + trail, tok[:-1]
            out.append(r"\url{%s}%s" % (tok, esc(trail)))
        else:
            out.append(quotes(esc(tok)))
    return "".join(out)


def table(rows, caption=None):
    head, body = rows[0], rows[1:]
    n = len(head)
    size = r"\footnotesize" if n >= 6 else r"\small"
    spec = "Y" + "l" * (n - 1)
    lines = [r"\par\noindent\begin{minipage}{\textwidth}"]
    if caption:
        lines.append(r"{\small %s\par}\vspace{3pt}" % caption)
    lines += [r"\centering", size, r"\begin{tabularx}{\textwidth}{%s}" % spec, r"\toprule",
             " & ".join(r"\textbf{%s}" % inline(c) for c in head) + r" \\", r"\midrule"]
    for r in body:
        lines.append(" & ".join(inline(c) for c in r) + r" \\")
    lines += [r"\bottomrule", r"\end{tabularx}", r"\end{minipage}\par\vspace{8pt}"]
    return "\n".join(lines)


def figure(path, caption):
    name = os.path.basename(path)
    width = {"fig_methods.png": 0.94, "fig2_entry_by_dose.png": 0.7, "fig2_what_they_say.png": 0.8,
             "fig1_who_is_asking.png": 0.95, "fig1_message_by_system_prompt.png": 0.95}.get(name, 1.0)
    cap = inline(caption)
    m = re.match(r"(Figure \d+\.)(.*)", caption)
    if m:
        cap = r"\textbf{%s}%s" % (m.group(1), inline(m.group(2)))
    return "\n".join([r"\begin{figure}[htbp]", r"\centering",
                      r"\includegraphics[width=%.2f\textwidth]{%s}" % (width, path),
                      r"\par\vspace{2pt}{\small %s\par}" % cap, r"\end{figure}"])


def convert(md):
    lines = md.split("\n")
    title = lines[0].lstrip("# ").strip()
    authors = [a.strip() for a in lines[2].split("|") if not a.strip().startswith("With")]
    abstract = lines[6].strip()
    out = [PREAMBLE]
    out.append(r"\begin{center}{\fontsize{20}{24}\selectfont\bfseries %s\footnote{%s}\par}"
               % (inline(title), esc(FOOTNOTE)))
    out.append(r"\vspace{10pt}")
    cells = []
    for a in authors:
        name, _, aff = a.partition(",")
        cells.append(r"\begin{tabular}[t]{c}%s\\{}%s\end{tabular}" % (inline(name.strip()), inline(aff.strip())))
    out.append(r"\hspace{2em}".join(cells) + r"\hspace{2em}\begin{tabular}[t]{c}\textbf{With}\\Apart Research\end{tabular}")
    out.append(r"\end{center}")
    out.append(r"\vspace{2pt}\begin{center}{\fontsize{14}{17}\selectfont\bfseries Abstract}\end{center}\vspace{-6pt}")
    out.append(r"\begin{center}\fbox{\begin{minipage}{0.9\textwidth}\vspace{4pt}\small\setlength{\parskip}{0pt}"
               r"\linespread{1.0}\selectfont %s\vspace{4pt}\end{minipage}}\end{center}" % inline(abstract))
    i = 8
    pending_caption = None
    while i < len(lines):
        line = lines[i].rstrip()
        if not line:
            i += 1
            continue
        if line.startswith("## "):
            head = line[3:]
            if head.startswith(MAIN_END_BEFORE):
                out.append(r"\FloatBarrier\label{endmain}")
            out.append(r"\section*{%s}" % inline(head))
        elif line.startswith("### "):
            out.append(r"\subsection*{%s}" % inline(line[4:]))
        elif line.startswith("!["):
            path = re.search(r"\(([^)]+)\)", line).group(1)
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            cap = lines[j].strip()[1:-1] if j < len(lines) and lines[j].strip().startswith("*Figure") else ""
            out.append(figure(path, cap))
            i = j + 1 if cap else i + 1
            continue
        elif line.startswith("|"):
            block = []
            while i < len(lines) and lines[i].startswith("|"):
                block.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            rows = [r for r in block if not set("".join(r)) <= set("-: ")]
            out.append(table(rows, pending_caption))
            pending_caption = None
            continue
        elif re.match(r"^\d+\. ", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                items.append(re.sub(r"^\d+\. ", "", lines[i].rstrip()))
                i += 1
            small = r"\small" if any("arXiv" in it or "doi:" in it for it in items) else ""
            out.append(r"\begin{enumerate}" + small)
            out += [r"\item " + inline(it) for it in items]
            out.append(r"\end{enumerate}")
            continue
        elif line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(lines[i][2:].rstrip())
                i += 1
            out.append(r"\begin{itemize}")
            out += [r"\item " + inline(it) for it in items]
            out.append(r"\end{itemize}")
            continue
        elif line.startswith("*Table") and line.endswith("*"):
            m = re.match(r"(Table [A-Z]?\d+\.)(.*)", line[1:-1])
            pending_caption = r"\textbf{%s}\emph{%s}" % (m.group(1), inline(m.group(2))) if m else inline(line[1:-1])
        else:
            if line.startswith("**") and line.endswith(":**"):  # lead-in to a list: keep with it
                out.append(r"\needspace{5\baselineskip}")
            out.append(inline(line) + "\n")
        i += 1
    out.append(r"\end{document}")
    return "\n".join(out)


def tectonic():
    exe = shutil.which("tectonic") or "/opt/homebrew/bin/tectonic"
    if not os.path.exists(exe):
        sys.exit("tectonic not found")
    return exe


def main():
    os.makedirs(TEXDIR, exist_ok=True)
    with open(SRC) as f:
        tex = convert(f.read())
    with open(TEX, "w") as f:
        f.write(tex)
    # cwd = report/latex so the relative \graphicspath (report/) works and no absolute paths leak
    subprocess.run([tectonic(), "--keep-intermediates", "--keep-logs", "apart_submission.tex"],
                   cwd=TEXDIR, check=True)
    shutil.move(os.path.join(TEXDIR, "apart_submission.pdf"), PDF)
    aux = open(os.path.join(TEXDIR, "apart_submission.aux")).read()
    m = re.search(r"\\newlabel\{endmain\}\{\{[^}]*\}\{(\d+)\}", aux)
    log = open(os.path.join(TEXDIR, "apart_submission.log")).read()
    pages = re.search(r"Output written on \S+ \((\d+) pages?", log)
    for ext in ("aux", "log", "out", "xdv"):
        p = os.path.join(TEXDIR, "apart_submission." + ext)
        if os.path.exists(p):
            os.remove(p)
    print("wrote", PDF)
    print("main text ends on page", m.group(1) if m else "?", "| total pages",
          pages.group(1) if pages else "?")


if __name__ == "__main__":
    main()
