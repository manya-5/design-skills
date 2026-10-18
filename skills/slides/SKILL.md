---
name: slides
description: Turns notes, a doc or bullet points into a clean 16:9 PowerPoint deck with light or dark themes, and checks that every text box fits before handing it over. Use when someone asks for a presentation, deck or slides from their content.
---

# Slides

Turn raw content into a checked `.pptx`. The builder draws every slide from a small set of layouts and measures every text box with real font widths, so the deck looks the same in PowerPoint, Keynote and Google Slides.

## Files

| File | What it is | When to read it |
|---|---|---|
| `layouts.md` | The 8 layouts, their fields and how much text each holds | Step 4 |
| `scripts/build_deck.py` | Builds the deck from a plan and warns about anything that doesn't fit | Run it, don't read it |
| `scripts/render.py` | Turns the deck into one PNG per slide | Run it, don't read it |
| `examples/plan.json` | A complete 8-slide plan using every layout | When writing your first plan |

## Hard rules

- Text that doesn't fit gets shorter or moves to another slide. Never make it smaller.
- The builder's warnings are the authority on fit. A deck with warnings is not finished.
- One message per slide. If a slide needs two headlines, it's two slides.
- Never invent facts, numbers, names or quotes. If the content doesn't have a number, don't use a stats slide.

## Workflow

Copy this checklist and tick it off as you go:

```
- [ ] 1. Read the content
- [ ] 2. Light or dark
- [ ] 3. Split into slides
- [ ] 4. Pick a layout for each slide
- [ ] 5. Write plan.json and build (repeat until 0 warnings)
- [ ] 6. Render and look at every slide (repeat 5 and 6 until clean)
- [ ] 7. Deliver
```

**1. Read the content.** Note the main message, the sections, and every number, name, quote and date. If something the deck needs is missing (the presenter's name, a date), ask.

**2. Light or dark.** If the user didn't say, ask. Don't mix them in one deck.

**3. Split into slides.** A typical deck is a title slide, a section slide before each part, the content slides, and a closing slide. Most talks need fewer slides than people think.

**4. Pick layouts.** Match each slide to a layout in `layouts.md`.

| Content | Layout |
|---|---|
| Opening | `title` |
| New part of the talk | `section` |
| A short list of points | `bullets` |
| A comparison or before and after | `two-column` |
| 3 or 4 numbers that matter | `stats` |
| A process or timeline | `steps` |
| One line people should remember | `quote` |
| The ask or the takeaway | `closing` |

- Use each layout's item counts: `stats` takes 3 or 4, `steps` takes 3 to 5, `bullets` takes 2 to 6.
- Don't use the same layout three times in a row. The builder warns if you do.

**5. Write the plan and build.**

```bash
pip install python-pptx      # if missing
python scripts/build_deck.py --plan plan.json --out "Deck name.pptx" --theme light
```

Every `WARNING` names the slide and the field. Shorten the text or split the slide, then build again. Only continue when it prints `0 warning(s)`.

Optional `"notes"` on any slide become speaker notes.

**6. Render and look.**

```bash
python scripts/render.py "Deck name.pptx" renders/
```

Open every image and check: nothing overlaps, titles sit in the same place on every slide, no slide feels empty or crowded, and nothing reads as a placeholder. If anything is off, fix the plan and go back to step 5. If `render.py` can't run (it needs LibreOffice), say in your reply that the slides weren't checked visually.

**7. Deliver.** Give the user the `.pptx` and tell them, in plain words:
- It opens in PowerPoint and Keynote as is. For Google Slides, upload it to Drive and choose **Open with, Google Slides**.
- Every text box and shape is editable.
- Which slides still need their input, if any.
