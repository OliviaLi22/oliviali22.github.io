# byxiaoyu.com

An editorial personal website for Olivia Li / Xiaoyu. It is a static site built from Markdown and a small Python script. No package installation, database, or JavaScript framework is needed.

## Preview locally

From the repository root:

```sh
python3 preview.py
```

Open the **exact address printed in the terminal**. The script chooses a free local port, builds the site, checks local links, and confirms that `dist/CNAME` still contains `byxiaoyu.com`. Do not add `/dist/` to the address. Stop the server with `Ctrl-C`.

## Add or update content

Content is in paired `content/en/` and `content/zh/` folders. Each `.md` file begins with simple `key: value` front matter between `---` lines. The filename becomes the URL slug in both languages. Use the **same lowercase hyphenated filename** for both versions. After editing, run `python3 build.py --check`.

| Section | Edit | URL pattern |
| --- | --- | --- |
| Professional experience | Edit `content/{en,zh}/experience.json` | `/work/`, `/zh/work/` |
| Research projects | Add `content/{en,zh}/work/my-project.md` | `/work/my-project/`, `/zh/work/my-project/` |
| Technical expertise | Edit `content/{en,zh}/expertise.json` | `/work/`, `/zh/work/` |
| Research Notes (public blog) | Add `content/{en,zh}/journal/my-entry.md` | `/journal/my-entry/`, `/zh/journal/my-entry/` |
| Film notes | Add `content/{en,zh}/film/my-film.md` | `/film/my-film/`, `/zh/film/my-film/` |
| About introduction | Edit `content/{en,zh}/pages/about.md` | `/about/`, `/zh/about/` |
| About journey | Edit `content/{en,zh}/journey.json` | `/about/`, `/zh/about/` |
| Beyond Work | Edit `content/{en,zh}/pages/about-beyond.md` | `/about/`, `/zh/about/` |
| Photography | Add images to `assets/`; edit `content/{en,zh}/photos.json` | `/photography/`, `/zh/photography/` |

Research Notes is a **public, work-related blog** at the existing `/journal/` URLs. The first note explains the methodology of the public Portfolio Risk Decision Engine prototype without claiming performance results. Add further notes on quantitative risk, portfolio analytics, financial data, and research methods in both language folders. The film archive currently lists *Resident Evil* (2026) and *You Can See Everything* (2026) as **awaiting review**, with no invented personal opinions. Copy `content/en/examples/film-note-template.md` to `content/en/film/` when writing a new review, then create its Chinese counterpart in `content/zh/film/`. Only files in the language-specific film folders are published. Equity Quant Research Platform remains a planned concept without a verified repository. Publish numerical results and charts only when their source data and assumptions can be reviewed.

### English and Chinese

English lives at the existing URLs; Chinese lives under `/zh/`. The language switcher appears at the bottom of every footer and points to the same page in the other language. A choice is saved in `localStorage`; a returning visitor who opens the root English home URL is redirected to `/zh/` before the page paints if Chinese was selected. Direct article URLs always show their specified language. Without storage, URLs and the switcher still work. The generated HTML uses `lang="en"` or `lang="zh-CN"`, self canonicals, and language alternates.

To publish or edit a translation, open the matching files in `content/en/` and `content/zh/`. Keep the same filename so the language switcher stays on the same article. Translate the `title`, `summary`, `category`, `tags`, optional image `cover_alt`, and body; keep technical acronyms and proper names where appropriate. Translate dates in visible prose, but keep the front matter `date` and `watched` fields in `YYYY-MM-DD` so the builder formats them for each language. Shared interface translations are in `translations.py`. If you add a new English article, film note, or project without a Chinese file, the build creates a **clearly labeled Chinese translation-pending page** linking to English. It receives `noindex` and is omitted from the sitemap until translated. A Chinese item without an English counterpart fails the build. Do not copy English prose into `content/zh/` and present it as a completed translation.

### Work page

The Work page reads its two professional experience areas from `content/{en,zh}/experience.json`. Each entry has an `area`, `period`, one-sentence `description`, compact `focus` list, and a `tone` (`sage` or `terracotta`) for the accent color. These are areas of work, not separate formal job titles. The current formal title and employer appear in About instead. Do not add confidential employer details. Project cards read `question` and `approach` from each project's Markdown front matter; full case studies live in the Markdown bodies. Use `stage: planned` for concepts, `stage: prototype` for implemented research prototypes, and `stage: complete` only for documented finished work. Implemented stages require a verified public `repository` URL. An optional `pipeline` field uses `|` to separate documented implementation stages for the case-study diagram. Keep both language files aligned.

The About introduction is in `content/{en,zh}/pages/about.md`; Beyond Work copy is in `content/{en,zh}/pages/about-beyond.md`. Its timeline is `content/{en,zh}/journey.json`, in **reverse chronological order**. Each entry has `years`, `location`, and `title`; `organization` and `description` are optional. Keep dates, locations, institutions, and employers factual. The Connect section links to the verified GitHub profile and the site's Contact page.

The expertise categories and skill order live in `content/{en,zh}/expertise.json`. A toolkit item's `evidence` field is `role` when it is explicitly in the supplied role responsibilities, and `supplied` when it comes from the supplied skill list without a role-specific claim. The page displays these as **In professional roles** and **Additional toolkit** in English, with corresponding Chinese labels. `core: true` adds typographic emphasis within that evidence group; it does not change the evidence level or assign a proficiency score.

Quantitative Research Methods are kept in the same files. Portfolio Optimization and Walk-forward Backtesting now have `published: true` with the implemented Portfolio Risk Decision Engine as their source; other draft methods remain unpublished. Change another method to `published: true` in each language only after it is supported by an implemented case study (`source: /work/project-slug/`) or confirmed experience (`confirmed: true`). The build rejects a published research method without either form of support.

### Front matter examples

Research Notes:

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

Film note:

```md
---
title: Film title
date: 2026-11-11
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

All fields are plain text. `date` uses `YYYY-MM-DD`. `year`, `watched`, and `rating` are optional. To add a project, copy a file in `content/en/work/`, then add a matching file in `content/zh/work/`; update their front matter and fill in the section prompts. Use `order: 3` to place it after the current projects. Start with `stage: planned` and an empty `repository`; an implemented stage requires a verified public repository URL.

The builder supports headings (`##`, `###`), paragraphs, bold, italics, links, inline code, lists, blockquotes, and horizontal rules. Keep one metadata field per line. HTML inside Markdown is escaped for safety. The spoiler marker is the only special comment. For an optional article cover, add `cover: /assets/your-image.webp` and `cover_alt: A useful description` to its front matter.

### Photography

The current gallery uses clearly labeled abstract SVG placeholders. Replace them with your own optimized WebP, AVIF, or JPEG images in `assets/`, then edit or add matching objects in `content/{en,zh}/photos.json`: `file`, `category` (`travel`, `cities`, or `everyday`), and `alt`. Translate `alt` and `caption`; keep the `category` identifier in English for the shared filter logic. `caption` is optional. Set `placeholder` to `false` for real photographs. The gallery automatically provides category filters and a keyboard accessible native dialog lightbox. Keep images reasonably sized and descriptive alt text accurate. Because Photography is behind the personal gate, the public home page shows a generic invitation instead of photo previews.

## Analytics

`site.json` is the single place for a Cloudflare Web Analytics token. Leave `cloudflare_web_analytics_token` empty to emit no analytics script. After creating a Web Analytics site in Cloudflare, paste its **actual 32 character token** in that field and rebuild. The builder then inserts Cloudflare's official beacon script on every page. Do not add a second snippet if Cloudflare is already injecting it automatically for the domain.

Cloudflare's dashboard can report page views, provider-defined unique visitors, popular pages, referrers, and geographic trends. It does not identify individual readers. This site adds no analytics cookies of its own.

## Personal section gate

`/film/` and `/photography/` (including their article pages) show a password form. Unlocking one opens the other for the current browser tab session via `sessionStorage`; no cookie is set. Research Notes, Work, About, Contact, and the home page are public. The home page previews the latest research note; Film Notes and Photography remain private invitations. Public research notes appear in `sitemap.xml` and have normal indexable metadata. Protected routes are omitted from the sitemap and use a `noindex` meta tag.

The password is represented by a SHA-256 hash in `site.json`, not by the literal password. To change it, run the command below, type the new password when prompted, and paste the printed hash into `personal_gate_sha256`:

```sh
python3 -c 'import getpass,hashlib; print(hashlib.sha256(getpass.getpass("New password: ").encode()).hexdigest())'
```

**This is a visual gate, not secure access control.** GitHub Pages serves static files publicly, and the generated HTML and repository source can still reveal personal content. The short password can also be guessed. Do not put private or sensitive material in these Markdown files. For real privacy, use an authenticated private content service or a protected hosting setup such as Cloudflare Access; that requires separate deployment and account configuration. See [GitHub Pages visibility guidance](https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https) and [Cloudflare Access application paths](https://developers.cloudflare.com/cloudflare-one/access-controls/policies/app-paths/).

## GitHub Pages deployment

The repository began with a root `index.html` and no deployment workflow. Its current Pages publishing setting was not available in the checkout. This version adds `.github/workflows/pages.yml`, which builds `dist/` on pull requests and on `main`, then deploys on `main` only. It includes `CNAME` in the artifact and keeps the source `CNAME` at the repository root. The actual custom domain association is a GitHub Pages setting; confirm it remains `byxiaoyu.com`.

**Before merging this branch**, in the repository's **Settings → Pages → Build and deployment**, check **Source** and set it to **GitHub Actions** if needed. Confirm that the custom domain still reads `byxiaoyu.com` and that DNS remains configured in Cloudflare. The workflow cannot make these settings changes for you. Do not merge while Source is still set to a branch, because the source root no longer contains a published `index.html`.

The workflow deploys only after a push to `main` or a manual run on `main`. This branch can be reviewed without publishing the new site. The generated `dist/` directory is ignored by Git.

## Structure

- `build.py`: content rendering, page assembly, sitemap, and local link validation
- `content/en/`, `content/zh/`: paired Markdown and data for both languages
- `translations.py`: shared interface translations
- `content/{en,zh}/experience.json`: two dated professional experience areas on Work
- `content/{en,zh}/journey.json`: reverse chronological About timeline
- `content/{en,zh}/expertise.json`: technical toolkit and evidence-linked research methods
- `preview.py`: one-command local build and preview server
- `templates/base.html`: shared page shell, metadata, navigation, and footer
- `assets/site.css`: design system and responsive layouts
- `assets/gallery.js`: gallery filters and lightbox
- `assets/language.js`: saved language preference and footer switcher
- `site.json`: canonical URL, personal gate hash, and optional analytics token
- `assets/gate.js`: password form and tab-session unlock for personal sections
- `CNAME`: custom domain; keep this file

No private credentials belong in this repository.
