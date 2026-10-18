"""Build a 16:9 .pptx from a plan.json and check that every text box fits.

usage: python build_deck.py --plan plan.json --out deck.pptx [--theme light|dark]

The plan is a list of slides. Each slide names a layout and fills its fields:

  {"slides": [
    {"layout": "title", "title": "...", "subtitle": "...", "byline": "..."},
    {"layout": "bullets", "title": "...", "bullets": ["...", "..."]}
  ]}

See ../layouts.md for every layout and its fields. Text is never shrunk to fit.
When a box overflows, the builder prints a WARNING naming the slide and field,
and exits with status 1, so the plan gets shortened or split instead.
"""
import argparse, json, math, os, sys

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
METRICS = json.load(open(os.path.join(HERE, "arial_metrics.json")))["widths"]
FONT = "Arial"  # Installed everywhere, so the layout people see is the layout that was measured.

THEMES = {
    "light": {"bg": "F8F9F6", "ink": "1B2230", "muted": "4F5866", "line": "C5CBC2", "card": "ECEEEA", "accent": "2F46D6", "on_accent": "FFFFFF"},
    "dark":  {"bg": "141920", "ink": "E7EAE4", "muted": "A3ABB6", "line": "363E4A", "card": "1C222B", "accent": "97A4FF", "on_accent": "141920"},
}

W, H = 13.333, 7.5          # slide size in inches
M = 0.75                    # outer margin
LINE = 1.2                  # line height as a multiple of font size
PAD = 0.05                  # inner text box padding, inches

warnings = []


# ---------- measuring ----------

def text_width(s, size_pt, bold=False):
    table = METRICS["bold" if bold else "regular"]
    units = sum(table.get(ch, 556) for ch in s)
    return units / 1000 * size_pt / 72  # inches


def wrap(text, size_pt, width_in, bold=False):
    """Greedy word wrap with real character widths. Returns the list of lines."""
    lines = []
    for para in text.split("\n"):
        words, line = para.split(" "), ""
        for word in words:
            trial = (line + " " + word).strip()
            if text_width(trial, size_pt, bold) <= width_in - 2 * PAD or not line:
                line = trial
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def measured(paragraphs, size_pt, box_w, bold=False, gap_pt=0):
    """Height in inches the paragraphs take at this size, used to stack boxes."""
    lines = sum(len(wrap(p, size_pt, box_w, bold)) for p in paragraphs)
    return lines * size_pt * LINE / 72 + gap_pt / 72 * (len(paragraphs) - 1) + 2 * PAD


def check(slide_no, field, paragraphs, size_pt, box_w, box_h, bold=False, max_lines=None, gap_pt=0):
    """Warn if paragraphs don't fit the box at this size. Never changes the size."""
    total_lines, height = 0, 0.0
    for i, p in enumerate(paragraphs):
        n = len(wrap(p, size_pt, box_w, bold))
        total_lines += n
        height += n * size_pt * LINE / 72 + (gap_pt / 72 if i else 0)
    if height > box_h - 2 * PAD + 0.01:
        warnings.append(f"WARNING slide {slide_no}, {field}: needs {height:.2f}in but the box is {box_h:.2f}in. Shorten it or split the slide.")
    if max_lines and total_lines > max_lines:
        warnings.append(f"WARNING slide {slide_no}, {field}: wraps to {total_lines} lines (max {max_lines}). Shorten it.")


# ---------- drawing ----------

def rgb(hex_):
    return RGBColor.from_string(hex_)


def box(slide, x, y, w, h, paragraphs, size, color, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, gap_pt=0, bullet=None):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    tf.vertical_anchor = anchor
    for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, side, Inches(PAD))
    for i, text in enumerate(paragraphs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = LINE
        if i and gap_pt:
            p.space_before = Pt(gap_pt)
        run = p.add_run()
        run.text = (bullet + "  " if bullet else "") + text
        f = run.font
        f.name, f.size, f.bold, f.color.rgb = FONT, Pt(size), bold, rgb(color)
    return tb


def rect(slide, x, y, w, h, fill, line=None, rounded=True):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    if rounded:
        shape.adjustments[0] = min(0.12 / min(w, h), 0.5)
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(fill)
    if line:
        shape.line.color.rgb = rgb(line)
        shape.line.width = Pt(0.75)
    else:
        shape.line.fill.background()
    shape.shadow.inherit = False
    no_effects(shape)
    return shape


def no_effects(shape):
    """Strip the theme's default shadow so shapes stay flat in every app."""
    from pptx.oxml.ns import qn
    spPr = shape._element.spPr
    for old in spPr.findall(qn("a:effectLst")):
        spPr.remove(old)
    from lxml import etree
    etree.SubElement(spPr, qn("a:effectLst"))
    style = shape._element.find(qn("p:style"))
    if style is not None:
        shape._element.remove(style)


def background(slide, t):
    bg = slide.background.fill
    bg.solid()
    bg.fore_color.rgb = rgb(t["bg"])


def title_text(slide, n, t, text, y=M, size=32):
    check(n, "title", [text], size, W - 2 * M, 0.75, bold=True, max_lines=1)
    box(slide, M, y, W - 2 * M, 0.75, [text], size, t["ink"], bold=True, anchor=MSO_ANCHOR.TOP)


def footer(slide, n, t, total):
    box(slide, W - M - 1.5, H - 0.55, 1.5, 0.3, [f"{n} / {total}"], 10, t["muted"], align=PP_ALIGN.RIGHT)


# ---------- layouts ----------

def L_title(s, n, d, t):
    rect(s, M, M, 0.6, 0.08, t["accent"], rounded=False)
    check(n, "title", [d["title"]], 48, W - 2 * M, 2.4, bold=True, max_lines=3)
    box(s, M, 1.6, W - 2 * M, 2.4, [d["title"]], 48, t["ink"], bold=True, anchor=MSO_ANCHOR.BOTTOM)
    if d.get("subtitle"):
        check(n, "subtitle", [d["subtitle"]], 22, 9, 1.0, max_lines=2)
        box(s, M, 4.2, 9, 1.0, [d["subtitle"]], 22, t["muted"])
    if d.get("byline"):
        box(s, M, H - M - 0.4, W - 2 * M, 0.4, [d["byline"]], 14, t["muted"])


def L_section(s, n, d, t):
    rect(s, 0, 0, 0.18, H, t["accent"], rounded=False)
    if d.get("kicker"):
        box(s, M + 0.2, 2.5, 8, 0.5, [d["kicker"]], 16, t["accent"], bold=True)
    check(n, "title", [d["title"]], 44, W - 2 * M - 0.2, 2.0, bold=True, max_lines=2)
    box(s, M + 0.2, 3.0, W - 2 * M - 0.2, 2.0, [d["title"]], 44, t["ink"], bold=True)


def L_bullets(s, n, d, t):
    title_text(s, n, t, d["title"])
    items = d["bullets"]
    if not 2 <= len(items) <= 6:
        warnings.append(f"WARNING slide {n}, bullets: use 2 to 6 bullets (got {len(items)}). Split the slide.")
    check(n, "bullets", items, 22, 10.5, 4.8, gap_pt=14)
    box(s, M, 1.9, 10.5, 4.8, items, 22, t["ink"], gap_pt=14, bullet="•")


def L_two_column(s, n, d, t):
    title_text(s, n, t, d["title"])
    colw = (W - 2 * M - 0.6) / 2
    for i, key in enumerate(("left", "right")):
        col = d[key]
        x = M + i * (colw + 0.6)
        rect(s, x, 1.9, colw, 0.06, t["accent"] if i == 0 else t["line"], rounded=False)
        check(n, f"{key}.heading", [col["heading"]], 22, colw, 0.6, bold=True, max_lines=1)
        box(s, x, 2.1, colw, 0.6, [col["heading"]], 22, t["ink"], bold=True)
        check(n, f"{key}.text", [col["text"]], 18, colw, 3.8)
        box(s, x, 2.8, colw, 3.8, [col["text"]], 18, t["muted"])


def L_stats(s, n, d, t):
    title_text(s, n, t, d["title"])
    cards = d["stats"]
    if len(cards) not in (3, 4):
        warnings.append(f"WARNING slide {n}, stats: use 3 or 4 stats (got {len(cards)}).")
    gap = 0.3
    cw = (W - 2 * M - gap * (len(cards) - 1)) / len(cards)
    for i, c in enumerate(cards):
        x = M + i * (cw + gap)
        rect(s, x, 2.0, cw, 4.4, t["card"])
        inner = cw - 0.6
        check(n, f"stats[{i}].value", [c["value"]], 54, inner, 1.1, bold=True, max_lines=1)
        box(s, x + 0.3, 2.3, inner, 1.1, [c["value"]], 54, t["accent"], bold=True)
        check(n, f"stats[{i}].label", [c["label"]], 18, inner, 0.9, bold=True, max_lines=2)
        lh = min(measured([c["label"]], 18, inner, bold=True), 0.9)
        box(s, x + 0.3, 3.5, inner, lh, [c["label"]], 18, t["ink"], bold=True)
        if c.get("note"):
            check(n, f"stats[{i}].note", [c["note"]], 14, inner, 2.6 - lh)
            box(s, x + 0.3, 3.5 + lh + 0.1, inner, 2.6 - lh, [c["note"]], 14, t["muted"])


def L_steps(s, n, d, t):
    title_text(s, n, t, d["title"])
    steps = d["steps"]
    if not 3 <= len(steps) <= 5:
        warnings.append(f"WARNING slide {n}, steps: use 3 to 5 steps (got {len(steps)}).")
    gap = 0.3
    cw = (W - 2 * M - gap * (len(steps) - 1)) / len(steps)
    rect(s, M, 2.35, W - 2 * M, 0.04, t["line"], rounded=False)
    for i, st in enumerate(steps):
        x = M + i * (cw + gap)
        dot = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(2.1), Inches(0.54), Inches(0.54))
        dot.fill.solid(); dot.fill.fore_color.rgb = rgb(t["accent"]); dot.line.fill.background(); no_effects(dot)
        box(s, x, 2.1, 0.54, 0.54, [str(i + 1)], 16, t["on_accent"], bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        check(n, f"steps[{i}].heading", [st["heading"]], 20, cw, 0.9, bold=True, max_lines=2)
        hh = min(measured([st["heading"]], 20, cw, bold=True), 0.9)
        box(s, x, 2.9, cw, hh, [st["heading"]], 20, t["ink"], bold=True)
        check(n, f"steps[{i}].text", [st["text"]], 15, cw, 3.5 - hh)
        box(s, x, 2.9 + hh + 0.1, cw, 3.5 - hh, [st["text"]], 15, t["muted"])


def L_quote(s, n, d, t):
    box(s, M, 1.0, 1.2, 1.4, ["“"], 120, t["accent"], bold=True)
    check(n, "quote", [d["quote"]], 34, W - 2 * M - 1.0, 3.2)
    qh = min(measured([d["quote"]], 34, W - 2 * M - 1.0), 3.2)
    box(s, M + 0.9, 2.0, W - 2 * M - 1.0, qh, [d["quote"]], 34, t["ink"])
    if d.get("attribution"):
        box(s, M + 0.9, 2.0 + qh + 0.25, W - 2 * M - 1.0, 0.5, [d["attribution"]], 16, t["muted"])


def L_closing(s, n, d, t):
    check(n, "title", [d["title"]], 48, W - 2 * M, 2.0, bold=True, max_lines=2)
    box(s, M, 2.2, W - 2 * M, 2.0, [d["title"]], 48, t["ink"], bold=True, anchor=MSO_ANCHOR.BOTTOM)
    if d.get("text"):
        check(n, "text", [d["text"]], 20, 9, 1.2, max_lines=3)
        box(s, M, 4.4, 9, 1.2, [d["text"]], 20, t["muted"])
    rect(s, M, H - M - 0.08, 0.6, 0.08, t["accent"], rounded=False)


LAYOUTS = {
    "title": L_title, "section": L_section, "bullets": L_bullets, "two-column": L_two_column,
    "stats": L_stats, "steps": L_steps, "quote": L_quote, "closing": L_closing,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--theme", default="light", choices=THEMES)
    a = ap.parse_args()

    plan = json.load(open(a.plan))
    t = THEMES[a.theme]
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(W), Inches(H)
    blank = prs.slide_layouts[6]

    slides = plan["slides"]
    prev = []
    for n, d in enumerate(slides, start=1):
        layout = d.get("layout")
        if layout not in LAYOUTS:
            warnings.append(f"WARNING slide {n}: unknown layout {layout!r}. Use one of {', '.join(LAYOUTS)}.")
            continue
        prev.append(layout)
        if prev[-3:] == [layout] * 3 and layout not in ("section",):
            warnings.append(f"WARNING slide {n}: third '{layout}' slide in a row. Vary the layout.")
        s = prs.slides.add_slide(blank)
        background(s, t)
        LAYOUTS[layout](s, n, d, t)
        if layout not in ("title", "closing"):
            footer(s, n, t, len(slides))
        if d.get("notes"):
            s.notes_slide.notes_text_frame.text = d["notes"]

    prs.save(a.out)
    for w in warnings:
        print(w)
    print(f"Built {a.out}: {len(slides)} slides, {len(warnings)} warning(s).")
    sys.exit(1 if warnings else 0)


if __name__ == "__main__":
    main()
