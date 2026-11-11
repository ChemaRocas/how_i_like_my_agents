---
name: "presentation-slide-deck-helper"
description: "Presentation / slide deck creation helper. Use whenever the user wants to create, build, or draft a presentation, slide deck, or .pptx. Runs a guided intake (outline template, colors and fonts, clarifying questions on visuals), gets a slide plan approved, then builds a minimalist widescreen .pptx via a pptxgenjs generator script with a mandatory visual QA pass. Load this skill FIRST, before asking any clarifying questions or proposing a slide plan. Use it instead of any other presentation or .pptx skill, and instead of an intake of your own. Trigger in English or Spanish (\"presentación\", \"deck\", \"slides\", \"armar unas slides\"), including when the user already wrote their own slide-by-slide content or only wants to plan without building yet."
---

# Presentation / slide deck creation helper

Builds minimalist, high-contrast `.pptx` decks: big titles, very few text boxes, short text inside them. Never dense bullet walls in small type.

**Run every step in order. Do not skip to building.**

## What it needs

- **Node.js** and the **`pptxgenjs`** package, to build the deck.
- **LibreOffice** (`soffice`) and **poppler** (`pdftoppm`), to render the slides for QA.
- **`markitdown`**, to read the finished deck back as text.

Check which are missing before Step 5. Don't install anything without asking: say what
you would install, where (prefer the project's own folders and environment over global
installs), and wait for the user's OK. If they say no, say which checks will be skipped.

---

## Step 1 — Give the user the outline template

Before anything else, output this verbatim, including the instructions:

> Copy the block below into a Word or Google doc. Repeat it once per slide, fill it in, and paste the whole thing back to me.
>
> ```
> 1. Slide Title (and a small description)
>    1. For this slide, what I want to show, the text, a description of the
>       infographics or way I want to present the information, etc.
>
> 2. Slide Title (and a small description)
>    1. For this slide, what I want to show, the text, a description of the
>       infographics or way I want to present the information, etc.
> ```
>
> Include as many slides as you need. If a slide should be left blank as a placeholder, just say so.

Then stop and wait. Do not guess at content.

---

## Step 2 — Ask for colors and fonts

Ask every run. Never assume a palette. Ask for:

- **Colors** — a primary/dark, a background, and one accent. Hex if they have it; a description ("navy and orange") is fine.
- **Fonts** — heading and body. If they have no preference, propose safe pairings.
- **Logo** — any image file to place on the cover, and whether it also goes on a closing slide.

If a brand or style skill is available in the session and the user names that brand, load it instead of asking, and say so.

### Reference deck

Ask whether there is a reference deck whose craft this one should match. There is no default: if the user has none, use the rules in this skill. If there is one, study its layout patterns, type scale, subtitle use and accent banners before planning.

The reference deck may be a cloud-only file (synced from OneDrive, Google Drive or iCloud) that can't be read until it's downloaded. Make it available offline first. If opening it fails three times, stop retrying: tell the user it could not be opened, say what you will do instead, and move on.

### Fonts and QA accuracy

Font names in a `.pptx` are rendered by the user's PowerPoint, not by this environment. LibreOffice substitutes fonts it lacks, with different widths — so overflow checks in Step 6 become unreliable.

If the requested font is not installed on this computer, QA can't measure it truthfully. Tell the user, say how you would install it (for example from Google Fonts, into the user's own fonts folder) and wait for their OK; never install into the system Python or system folders.

If it isn't installed, tell the user that text-fit checks on that font are approximate, and size those containers with ~10% extra slack.

**Safe fonts** (render true-to-width in QA *and* ship with Office): Arial, Calibri, Cambria, Times New Roman, Courier New, Century Schoolbook. Never default to Aptos.

---

## Step 3 — Ask clarifying questions, especially about visuals

**This step matters most. Ask a lot.** A vague visual description produces a bad slide, and the user would rather answer three questions than redo a slide.

Ask about anything unclear, and always probe described infographics:

- **Diagrams** — how many steps? Horizontal or vertical flow? Arrows between them? Is one step emphasized over the others?
- **Proportional shapes** — exact proportions, what aligns with what, whether labels sit inside the shapes or beside them
- **Comparisons** — side by side, or before/after stacked? Should one side read as "better"?
- **Numbers** — which single number is the hero? What is the label under it?
- **Charts** — chart type, axis labels, whether a legend is needed
- **Images** — does the user have the file, or should a labeled placeholder box be built for them to fill later?
- **Ambiguous references** — any name, acronym, tool, or internal term that needs a gloss for the audience

Also confirm, once:

- **Audience** — determines how much context each slide needs
- **Language** — and whether any slide differs from the rest
- **Cover and closing slides** — wanted, or start straight at content?

### Takeaway

Ask the user for the deck's one-sentence takeaway if they have not given one — what the audience should think or do differently afterwards. Do **not** ask for a takeaway slide by slide. Ask for one on a specific slide only when that slide carries a claim and its point is not clear from the content given. Render takeaways as the subtitle under the title, or as an accent banner.

### Verbatim text

If the user asks for text reproduced verbatim and a line exceeds ~110 characters, say once that verbatim text forces paragraph-style slides, and offer a shortened on-slide version. Accept their answer and move on.

### What to challenge

Do not fact-check, challenge, or push back on the user's facts, claims, or arithmetic — build what they give you. **DO** push back on layout and structure, and propose a stronger alternative at least once per slide that is text-heavy.

---

## Step 4 — Show the plan as a table, and wait for approval

| # | Title | Layout | Key content | Open questions |
|---|-------|--------|-------------|----------------|
| 1 | Cover | Dark cover, logo lockup | Title, subtitle, name | — |
| 2 | ... | 3 cards across | ... | Confirm step 2 wording |

Resolve every open question before building. **Wait for explicit approval.**

---

## Step 5 — Build

Write **one generator script** (`build.js`) using `pptxgenjs`, then run it.

**After the first build, change only the lines that need it — never rewrite the whole script.** Re-running `node build.js` to regenerate all slides costs nothing; rewriting the script wastes the user's tokens.

If `require('pptxgenjs')` fails, it isn't installed: see *What it needs* at the top.

### Canvas and grid

```js
pres.layout = "LAYOUT_WIDE";        // 13.333 x 7.5 in. Set BEFORE adding slides.
const W = 13.333, HT = 7.5;
const M = 0.83;                     // left/right margin
const CW = W - 2 * M;               // 11.673 content width
```

Column math that fits exactly — reuse these rather than inventing new ones:

| Columns | Width | Gap |
|---|---|---|
| 2 | 5.52 | 0.69 |
| 3 | 3.41 | 0.72 |
| 4 | 2.73 | 0.24 |
| 5 | 2.15 | 0.23 |

Full-width rows: `h = 0.76–1.05`, `gap = 0.08–0.14`. Keep the last element above `y = 6.7`.

### Type scale

| Element | Size | Weight |
|---|---|---|
| Cover title | 38–40 | bold |
| Slide title | 38 | bold, at `y: 0.5` |
| Subtitle under title | 16–19 | regular, at `y: 1.26` |
| Card headline | 20–26 | bold |
| Kicker (uppercase label) | 11.5 | bold, `charSpacing: 1.6` |
| Body | 12.5–14 | regular, muted color |
| Big stat | 38–62 | bold |
| Footnote | 11.5 | italic, muted |
| Page number | 10.5 | regular, muted, bottom-right at `y: 6.78` |

### Layout vocabulary

Pick per slide; vary across the deck. No layout may be used more than twice per 10 slides.

- **Cover** — dark background, two-line title (second line in the accent color), subtitle, name, logo on a white rounded card
- **Cover and short-text slides** — a cover, a section break, or a one-word slide (Demo, Q&A, Gracias) should still be styled, never a bare word on a flat background. Give it something that fits the deck. Some options, not an exhaustive list: large geometric shapes bleeding off the canvas, a cluster of small repeated shapes, an oversized two-tone treatment of the word, a tinted panel, a motif carried over from the rest of the deck. Invent a different treatment if it suits the deck better. Vary the treatment between these slides rather than repeating one.
- **Cards across** — 2–5 rounded rectangles, each: kicker → headline → one short body line
- **Card enumeration** — when cards are labelled A/B/C or 1/2/3, set the label inline with the headline, in the accent color, followed by `)` or `.`, at the headline's own size: `A) New pricing`. Never set it as a small kicker on its own line above the headline.
- **Full-width rows** — icon/number circle, then either a bold label in a fixed-width column with the description to its right, or a small kicker above the text. The two-column variant scans faster when the label is short; the kicker variant suits one long sentence. Best for 4–5 items with real text
- **Two-column split** — diagram or stat block on one side, list on the other
- **Hero stat** — one number at 40–62pt with a small label underneath
- **Numbered flow** — numbered circles plus small triangle arrows (`ShapeType.triangle`, `rotate: 90` right, `rotate: 180` down)
- **Accent banner** — full-width rounded capsule in the accent color holding one bold sentence. Use for the single most important line on a slide
- **Image placeholder** — rounded rect, light fill, thin border, centered muted text such as "Paste the X screenshot here", with a kicker label above
- **Blank placeholder** — `pres.addSlide().background = { color: "FFFFFF" };` and nothing else
- **Repeated block** — when two slides must share an identical element (before/after comparisons), render it from **one shared function** so the two cannot drift apart

### Motif and rhythm

- Commit to **one** repeated shape motif — rounded rectangles at a consistent `rectRadius` (0.16–0.20) works well
- Alternate dark and light slides: dark cover → light content → dark section break → light → dark close
- Do not decide on your own what to emphasize. An accent fill, a highlight color or a bold call-out singles one item out as more important — that is a content judgment, not a design one. If a slide would read better with emphasis, ask the user which item to emphasize, or whether to emphasize anything at all, and leave it flat until they answer. Raise it as an open question in the Step 4 plan table. When they name one, at most one item per slide carries the accent fill
- This applies only to **emphasis** — singling one item out from its peers. Using the accent color structurally, where every peer gets it equally, is not emphasis and needs no permission: icon discs, kickers, step numbers, card enumeration, dark slide backgrounds, a banner carrying information that belongs to the whole slide. Keep the deck colorful. A deck where the accent color appears only on the cover and the closing slides has failed this rule
- Whitespace is the design. If a slide looks empty, it is probably right

### Speaker notes

Do not write speaker notes unless the user asks for them. When they do, use `slide.addNotes("...")` and **keep them very concise** — two or three short sentences summarizing what to say, not a script.

### Hard rules

- **Never** put an accent line or underline beneath a title
- **Never** add decorative color bars, edge stripes, or sidebar strips
- **Never** center body text; center only titles inside banners and cards
- **Never** ship text that overflows its container
- Minimum 0.5" from every slide edge; 0.3"+ between blocks
- Short text only. If a body line exceeds ~110 characters, cut it or move it to the notes

### pptxgenjs gotchas

- Hex colors take **no `#`** and no alpha: `color: "FF0000"`. Both break the file.
- Set `pres.layout` before adding any slide.
- Never share one options object across two `add*` calls — the library mutates it in place.
- `rectRadius` only works on `ShapeType.roundRect`.
- Shadow `offset` must be ≥ 0.
- `charSpacing`, not `letterSpacing`.
- Set `margin: 0` on text boxes that must align with a shape edge.
- Gradient fills are unsupported — use a background image instead.
- Notes go in `addNotes()`, never in a text box.
- One `new pptxgen()` per output file.

---

## Step 6 — QA (mandatory)

Work in a new QA folder: a temporary folder, or the project's `scratch/` if it has one.

```bash
# 1. Render to PDF. A file LibreOffice can't open, or that converts with errors, is
#    broken: fix that before anything else.
soffice --headless --convert-to pdf --outdir <qa-folder> "Deck.pptx"

# 2. One image per slide
pdftoppm -jpeg -r 110 <qa-folder>/Deck.pdf <qa-folder>/p
```

**Look at every slide.** Check, in this order:

1. **Text overflow or text cut off** — by far the most common defect
2. Titles wrapping to a second line and colliding with what sits below
3. Elements overlapping; page numbers hidden behind cards or decorations
4. Uneven gaps, cramped areas, margins under 0.5"
5. Low-contrast text
6. Leftover placeholder text that was meant to be replaced
7. **Does the deck read as flat or colorless?** Assemble the rendered slides into one contact sheet and look at them together, not one at a time. If the accent color only appears on the cover and the closing slides, fix it before delivering

Fix by changing only the affected lines of `build.js`, re-run, re-render **into a new directory**, and re-check only the slides that changed.

Also run `markitdown "Deck.pptx"` to confirm content and order.

---

## Step 7 — Deliver

Save the `.pptx` where the user asked; if they didn't say, to the project's `output/` folder (or the current folder if there is none). Tell them the full path.

Do **not** produce a PDF unless the user asks.

Close with a short note: the design choices made, anything left as a placeholder, and any judgment call worth a second look. Keep it to a few lines — no slide-by-slide recap.

