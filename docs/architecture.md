# Architecture

[Back to the project overview](../README.md) · [Local development](development.md) · [Content maintenance](maintenance.md)

## Build flow

The site is a static publication. There is no runtime server, database, or content API.

```text
content/en + content/zh + site.json
                 ↓
       build.py + templates/base.html
                 ↓
        dist/ + assets + CNAME
                 ↓
              GitHub Pages
```

[`build.py`](../build.py) reads Markdown with simple `key: value` front matter and structured JSON. It renders pages with a small, intentionally limited Markdown parser, writes the site into the ignored `dist/` directory, copies `assets/` and the root [`CNAME`](../CNAME), and generates `sitemap.xml`, `robots.txt`, and English and Chinese 404 pages. The build uses only Python's standard library.

## Source map

| Path | Role |
| --- | --- |
| [`content/en/`](../content/en/) and [`content/zh/`](../content/zh/) | Paired articles, project case studies, and section data |
| [`translations.py`](../translations.py) | Shared English-to-Chinese interface labels |
| [`templates/base.html`](../templates/base.html) | Semantic page shell, navigation, metadata, and footer |
| [`assets/site.css`](../assets/site.css) | Editorial design and responsive layouts |
| [`assets/language.js`](../assets/language.js) | Saved language choice for the home page and footer switcher |
| [`assets/gallery.js`](../assets/gallery.js) | Photography filters and native-dialog lightbox |
| [`assets/gate.js`](../assets/gate.js) | Browser-side password screen for Film Notes and Photography |
| [`site.json`](../site.json) | Canonical URL, gate hash, and optional analytics token |

## Language and discoverability

English uses the root URLs; Simplified Chinese uses `/zh/`. Matching content files share a slug, so the footer language switcher can point to the same page in the other language. The selected language is saved in `localStorage`; only an English home-page visit may redirect to `/zh/`. Direct links to articles keep their specified language.

Pages carry the matching `lang` attribute, self-referencing canonical URL, Open Graph metadata, and language alternates. A new English entry without a Chinese counterpart gets a clearly labeled Chinese translation-pending page. That stub is `noindex`, has no Chinese `hreflang` alternate, and stays out of the sitemap until translated.

## Rendering and access boundaries

The Markdown renderer supports headings, paragraphs, bold and italic text, links, inline code, lists, blockquotes, and horizontal rules. Raw HTML in Markdown is escaped. A special `<!-- spoilers -->` marker splits film notes into an initial review and a collapsible spoiler section. See [maintenance](maintenance.md) for authoring examples.

Work, Research Notes, About, Contact, and Home are public. Film Notes and Photography use a visual password screen; their generated HTML and repository files remain publicly accessible. Unlock state lasts for the browser tab through `sessionStorage`, without a site cookie. Those two sections receive `noindex` and are omitted from the sitemap. The gate must never be used to protect sensitive information.

`python3 build.py --check` validates local links, page structure, language metadata, section access rules, and preservation of `byxiaoyu.com` in the generated `CNAME`.
