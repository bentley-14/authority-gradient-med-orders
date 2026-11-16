"""Builds report/apart_submission.docx from report/apart_submission.md, laid out like
the Apart Research submission template (Old Standard TT, title block, authors, abstract
box, numbered sections). Handles only the Markdown this report uses: headings, paragraphs
with **bold** / *italic* / `code`, numbered and bulleted lists, pipe tables, and images.
The PDF for submission is built separately by report/build_pdf.py from the same Markdown.

Usage: python3 report/build_docx.py   (needs python-docx)
"""
import os
import re

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = os.path.join(HERE, "apart_submission.md"), os.path.join(HERE, "apart_submission.docx")
FONT = "Old Standard TT"
FOOTNOTE = "Research conducted at the AI x Epistemics Research Sprint, November 2026"


def runs(par, text, size=None, italic_all=False):
    for tok in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)", text):
        if not tok:
            continue
        bold = tok.startswith("**") and tok.endswith("**")
        code = tok.startswith("`") and tok.endswith("`") and len(tok) > 1
        ital = not bold and tok.startswith("*") and tok.endswith("*") and len(tok) > 1
        r = par.add_run(tok[2:-2] if bold else tok[1:-1] if (ital or code) else tok)
        r.bold, r.italic = bold, ital or italic_all
        r.font.name = "Courier New" if code else FONT
        if size:
            r.font.size = Pt(size)


def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hexcolor)
    tcPr.append(shd)


def main():
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    for side in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec, side, Inches(1))
    st = doc.styles["Normal"]
    st.font.name, st.font.size = FONT, Pt(11)
    st.paragraph_format.space_after = Pt(6)
    for name, size in (("Heading 1", 14), ("Heading 2", 13), ("Heading 3", 12)):
        h = doc.styles[name]
        h.font.name, h.font.size, h.font.bold = FONT, Pt(size), True
        h.font.color.rgb = RGBColor(0, 0, 0)
        h.paragraph_format.space_before, h.paragraph_format.space_after = Pt(12), Pt(4)
        h.paragraph_format.keep_with_next = True

    lines = open(SRC).read().split("\n")
    i = 0
    # Title block
    title = lines[0].lstrip("# ").strip()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    runs(p, title, size=20)
    for r in p.runs:
        r.bold = True
    authors = [a.strip() for a in lines[2].split("|")]
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    runs(p, "    ".join(a for a in authors if not a.startswith("With")), size=10.5)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    runs(p, "**With** Apart Research", size=11)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    runs(p, FOOTNOTE, size=8.5, italic_all=True)
    # Abstract box
    abstract = lines[6].strip()
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = "Table Grid"
    c = t.rows[0].cells[0]
    shade(c, "F3F3F1")
    c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    runs(c.paragraphs[0], "**Abstract**", size=14)
    ap = c.add_paragraph()
    ap.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    runs(ap, abstract, size=10)
    doc.add_paragraph()

    i = 8
    while i < len(lines):
        line = lines[i].rstrip()
        if not line:
            i += 1
            continue
        if line.startswith("### "):
            doc.add_heading(line[4:], level=3)
        elif line.startswith("## "):
            doc.add_heading(line[3:], level=1)
        elif line.startswith("!["):
            path = os.path.normpath(os.path.join(HERE, re.search(r"\(([^)]+)\)", line).group(1)))
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run().add_picture(path, width=Inches(6.2))
        elif line.startswith("|"):
            block = []
            while i < len(lines) and lines[i].startswith("|"):
                block.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            rows = [r for r in block if not set("".join(r)) <= set("-: ")]
            t = doc.add_table(rows=len(rows), cols=len(rows[0]))
            t.style = "Table Grid"
            t.alignment = WD_TABLE_ALIGNMENT.CENTER
            for ri, r in enumerate(rows):
                for ci, val in enumerate(r):
                    cell = t.rows[ri].cells[ci]
                    runs(cell.paragraphs[0], ("**%s**" % val) if ri == 0 else val, size=9)
                    if ri == 0:
                        shade(cell, "F3F3F1")
            doc.add_paragraph()
            continue
        elif re.match(r"^\d+\. ", line):  # literal numbers, so each list restarts at 1
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3)
            p.paragraph_format.first_line_indent = Inches(-0.25)
            runs(p, line)
        elif line.startswith("- "):
            p = doc.add_paragraph(style="List Bullet")
            runs(p, line[2:])
        elif line.startswith("*") and line.endswith("*") and not line.startswith("**"):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if line.startswith("*Figure") else WD_ALIGN_PARAGRAPH.LEFT
            runs(p, line[1:-1], size=9, italic_all=True)
        else:
            p = doc.add_paragraph()
            runs(p, line)
        i += 1
    doc.save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
