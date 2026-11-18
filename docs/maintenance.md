# Content maintenance

[Back to the project overview](../README.md) · [Architecture](architecture.md) · [Local development](development.md)

Edit source files, then run `python3 build.py --check`. Content lives in paired [`content/en/`](../content/en/) and [`content/zh/`](../content/zh/) folders. A Markdown filename becomes the URL slug; use the same lowercase, hyphenated name in both languages.

| Section | Source files | URL pattern |
| --- | --- | --- |
| Experience and toolkit | `content/{en,zh}/experience.json`, `expertise.json` | `/work/` |
| Project case studies | `content/{en,zh}/work/*.md` | `/work/<slug>/` |
| Research Notes | `content/{en,zh}/journal/*.md` | `/journal/<slug>/` |
| Film Notes | `content/{en,zh}/film/*.md` | `/film/<slug>/` |
| About introduction and interests | `content/{en,zh}/pages/about.md`, `about-beyond.md` | `/about/` |
| About timeline | `content/{en,zh}/journey.json` | `/about/` |
| Photography | `content/{en,zh}/photos.json` and `assets/` | `/photography/` |

Chinese URLs add `/zh/` before the route shown above. The shared interface copy is in [`translations.py`](../translations.py). Translate titles, summaries, categories, tags, captions, image alt text, and article bodies naturally; retain technical acronyms and proper names where appropriate. Keep front matter `date` and `watched` in `YYYY-MM-DD` so the builder formats them by language. English entries without Chinese files get a clearly labeled, non-indexed translation-pending page; Chinese entries without English counterparts fail the build.

## Work and About

Each `experience.json` entry has an area, period, one-sentence description, focus terms, and a required `tone` value (`sage` or `terracotta`). The current stylesheet presents both areas with the same sage card styling. These are areas of experience, not separate formal job titles. Keep employer details and the official title in About; do not add confidential work details.

Project Markdown front matter supplies each card's `question`, `approach`, `summary`, `status`, and `stage`. Use `stage: planned` for concepts, `prototype` for implemented research prototypes, and `complete` only for documented finished work. An implemented stage requires a verified public `repository` URL. An optional `pipeline` field uses `|` between documented implementation steps; `order: 3` places a new project after the current two. The Portfolio Risk Decision Engine is a public research prototype; the Equity Quant Research Platform remains planned. Publish numerical findings or charts only when their source data and assumptions can be reviewed.

The About introduction and Beyond Work copy are Markdown. Keep `journey.json` in reverse chronological order; each entry needs `years`, `location`, and `title`, with optional `organization` and `description`. Avoid inventing dates, employers, or qualifications.

Toolkit items use `evidence: role` for responsibilities explicitly supplied for professional work and `evidence: supplied` for the broader skill list. The page labels those groups separately; it does not assign proficiency scores. A `core: true` field remains in the data but currently does not change tag appearance. Research-method entries appear only when `published: true` and accompanied by a case-study `source` or `confirmed: true`; review the evidence before publishing one. Portfolio Optimization and Walk-forward Backtesting currently link to the implemented risk case study; other draft methods remain unpublished.

## Articles and film notes

Each Markdown file begins with plain `key: value` front matter between `---` lines. For a public Research Note:

```md
---
title: A specific research question or project note
date: 2026-11-12
category: Research note
tags: Portfolio Risk, Data Analysis
summary: One clear sentence for cards and search previews.
---
## Opening section

State the question, method, evidence, and limitations here.
```

The existing [portfolio risk note](../content/en/journal/portfolio-risk-decision-workflow.md) is a factual project-methodology example. The film archive lists *Resident Evil* and *You Can See Everything* as awaiting review, with no invented personal opinions. Copy the [film template](../content/en/examples/film-note-template.md) into `content/en/film/`, then add its Chinese counterpart. Only files in the language-specific film folders are published.

```md
---
title: Film title
date: 2026-11-12
category: Film essay
tags: Memory, Cinema
summary: A spoiler-free reflection for the archive.
year: 2000
watched: 2026-11-10
rating:
status: Published
---
Your spoiler-free review begins here.

<!-- spoilers -->
## Spoiler discussion

Plot-specific thoughts go here. This section becomes a collapsed panel.
```

`year`, `watched`, and `rating` are optional film fields. A project's `repository` may stay empty while planned; an implemented stage requires a verified URL. The builder supports headings (`##`, `###`), paragraphs, bold, italics, links, inline code, lists, blockquotes, and horizontal rules. Raw HTML inside Markdown is escaped; the spoiler marker is a special exception. For an optional article cover, add `cover: /assets/your-image.webp` and a descriptive `cover_alt` to the front matter.

## Photography

The gallery currently uses clearly labeled abstract SVG placeholders, not Olivia's photographs. Add your own optimized WebP, AVIF, or JPEG files to `assets/`, then update matching objects in both `photos.json` files. Each object needs `file`, `category` (`travel`, `cities`, or `everyday`), and `alt`; translate `alt` and optional `caption`. Keep category identifiers in English for the shared filter logic. Set `placeholder` to `false` for real photographs. The gallery provides category filters and a keyboard-accessible native-dialog lightbox. Keep file sizes reasonable and descriptions accurate. The public home page shows an invitation rather than gated photo previews.
