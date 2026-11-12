#!/usr/bin/env python3
"""Small, dependency-free Markdown site builder for byxiaoyu.com."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
from string import Template
from urllib.parse import urlparse
from translations import ZH, tr


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dist"
CONFIG = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
SITE_URL = CONFIG["site_url"].rstrip("/")
PRIVATE_PREFIXES = ("/film/", "/photography/")
LANGUAGE = "en"
MISSING_TRANSLATIONS: set[str] = set()


def locale_path(path: str, lang: str | None = None) -> str:
    lang = lang or LANGUAGE
    return "/zh" + path if lang == "zh" else path


def localize_markup(markup: str) -> str:
    if LANGUAGE == "en":
        return markup
    # Longest phrases first keeps the smaller shared labels from altering them.
    for source, target in sorted(ZH.items(), key=lambda pair: len(pair[0]), reverse=True):
        markup = markup.replace(source, target)
    return markup


def localize_links(markup: str) -> str:
    if LANGUAGE == "zh":
        return re.sub(r'href="/(?!assets/|zh/)', 'href="/zh/', markup)
    return markup


def is_private(path: str) -> bool:
    if path.startswith("/zh/"):
        path = path[3:]
    return path.startswith(PRIVATE_PREFIXES)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def read_content(path: Path) -> dict:
    source = path.read_text(encoding="utf-8")
    if not source.startswith("---\n"):
        raise ValueError(f"Missing front matter: {path}")
    _, front, body = source.split("---\n", 2)
    meta = {}
    for line in front.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"Invalid front matter in {path}: {line}")
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"')
    if "\n<!-- spoilers -->\n" in body:
        body, meta["spoilers"] = body.split("\n<!-- spoilers -->\n", 1)
    meta["body"] = body.strip()
    meta["slug"] = path.stem
    return meta


def content_collection(name: str) -> list[dict]:
    items = [read_content(p) for p in (ROOT / "content" / LANGUAGE / name).glob("*.md")]
    if name == "work":
        return sorted(items, key=lambda item: (int(item.get("order", "999")), item["slug"]))
    return sorted(items, key=lambda item: (item.get("date", ""), item["slug"]), reverse=True)


INLINE = re.compile(r"(`[^`]+`|\[[^\]]+\]\((?:https?://|/)[^\s)]+\))")


def inline(text: str) -> str:
    parts = []
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("`"):
            parts.append(f"<code>{esc(part[1:-1])}</code>")
        elif part.startswith("["):
            label, url = part[1:].split("](", 1)
            url = url[:-1]
            parts.append(f'<a href="{esc(url)}">{esc(label)}</a>')
        else:
            safe = esc(part)
            safe = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe)
            safe = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", safe)
            parts.append(safe)
    return "".join(parts)


def markdown(source: str) -> str:
    """Render the intentionally small Markdown set documented in README."""
    lines = source.splitlines()
    blocks = []
    paragraph = []
    list_kind = None

    def flush_paragraph() -> None:
        if paragraph:
            blocks.append(f"<p>{inline(' '.join(paragraph))}</p>")
            paragraph.clear()

    def close_list() -> None:
        nonlocal list_kind
        if list_kind:
            blocks.append(f"</{list_kind}>")
            list_kind = None

    for raw in lines + [""]:
        line = raw.strip()
        if not line:
            flush_paragraph()
            close_list()
        elif line.startswith("### ") or line.startswith("## "):
            flush_paragraph()
            close_list()
            level = 3 if line.startswith("### ") else 2
            blocks.append(f"<h{level}>{inline(line[level + 1:])}</h{level}>")
        elif line in ("---", "***"):
            flush_paragraph()
            close_list()
            blocks.append("<hr>")
        elif line.startswith("> "):
            flush_paragraph()
            close_list()
            blocks.append(f"<blockquote><p>{inline(line[2:])}</p></blockquote>")
        elif re.match(r"^(?:[-*] |\d+\. )", line):
            flush_paragraph()
            kind = "ol" if re.match(r"^\d+\. ", line) else "ul"
            if list_kind != kind:
                close_list()
                blocks.append(f"<{kind}>")
                list_kind = kind
            item = re.sub(r"^(?:[-*] |\d+\. )", "", line)
            blocks.append(f"<li>{inline(item)}</li>")
        else:
            close_list()
            paragraph.append(line)
    return "\n".join(blocks)


def pretty_date(value: str) -> str:
    if not value:
        return "日期未定" if LANGUAGE == "zh" else "Undated"
    parsed = datetime.strptime(value, "%Y-%m-%d")
    return f"{parsed.year}年{parsed.month}月{parsed.day}日" if LANGUAGE == "zh" else parsed.strftime("%B %-d, %Y")


def reading_time(body: str) -> str:
    count = len(re.findall(r"[\u4e00-\u9fff]", body)) if LANGUAGE == "zh" else len(body.split())
    minutes = max(1, round(count / (400 if LANGUAGE == "zh" else 220)))
    return f"约{minutes}分钟阅读" if LANGUAGE == "zh" else f"{minutes} min read"


def tags(item: dict) -> str:
    values = [x.strip() for x in item.get("tags", "").split(",") if x.strip()]
    return "".join(f"<span class='tag'>{esc(value)}</span>" for value in values)


def link(path: str, label: str, css: str = "text-link") -> str:
    return f'<a class="{css}" href="{esc(path)}">{esc(label)} <span aria-hidden="true">↗</span></a>'


NAV = [
    ("/work/", "Work"), ("/journal/", "Research Notes"), ("/film/", "Film notes"),
    ("/photography/", "Photography"), ("/about/", "About"), ("/contact/", "Contact"),
]


def shell(title: str, description: str, path: str, body: str, active: str = "", kind: str = "website") -> str:
    nav = "".join(
        f'<a href="{locale_path(url)}"' + (' aria-current="page"' if active == url else "") + f'>{esc(tr(label, LANGUAGE))}</a>'
        for url, label in NAV
    )
    token = CONFIG.get("cloudflare_web_analytics_token", "").strip()
    if token and not re.fullmatch(r"[a-fA-F0-9]{32}", token):
        raise ValueError("Cloudflare Web Analytics token must be 32 hexadecimal characters")
    analytics = (
        '<script type="module" src="https://static.cloudflareinsights.com/beacon.min.js" '
        f"data-cf-beacon='{esc(json.dumps({'token': token}))}'></script>"
        if token else ""
    )
    private = is_private(path)
    gate_script = ""
    robots = ""
    skip_target = "#main"
    if private:
        password_hash = CONFIG.get("personal_gate_sha256", "")
        if not re.fullmatch(r"[a-f0-9]{64}", password_hash):
            raise ValueError("site.json needs a SHA-256 hash for the personal gate")
        body = f'''<section class="gate-screen wrap" id="gate-screen" role="main" aria-labelledby="gate-title" data-hash="{password_hash}">
          <p class="eyebrow">Personal archive / private</p>
          <h2 id="gate-title">A quieter<br><em>corner.</em></h2>
          <p class="gate-intro">Film notes and photography are behind a small password gate.</p>
          <div class="gate-form"><label for="private-password">Password</label>
          <div class="gate-controls"><input id="private-password" type="password" autocomplete="current-password" aria-describedby="gate-error"><button id="unlock-button" type="button">Enter <span aria-hidden="true">↗</span></button></div>
          <p id="gate-error" role="status" aria-live="polite"></p><noscript><p>JavaScript is required to open this section.</p></noscript></div>
          <p class="gate-back"><a href="/work/">← Return to work & research</a></p>
        </section><div id="protected-content" hidden>{body}</div>'''
        title = "Private notebook | byxiaoyu."
        description = "A private corner of Olivia Li's personal website."
        kind = "website"
        gate_script = '<script defer src="/assets/gate.js"></script>'
        robots = '<meta name="robots" content="noindex,nofollow">'
        skip_target = "#gate-screen"
    base_path = path[3:] if path.startswith("/zh/") else path
    if base_path == "/404.html":
        robots = '<meta name="robots" content="noindex,follow">'
    if base_path in MISSING_TRANSLATIONS and LANGUAGE == "zh":
        robots = '<meta name="robots" content="noindex,follow">'
    canonical = SITE_URL + path
    en_url = SITE_URL + locale_path(base_path, "en")
    zh_url = SITE_URL + locale_path(base_path, "zh")
    alternate = (f'<link rel="alternate" hreflang="en" href="{esc(en_url)}">'
                 + (f'<link rel="alternate" hreflang="zh-CN" href="{esc(zh_url)}">' if base_path not in MISSING_TRANSLATIONS else "")
                 + f'<link rel="alternate" hreflang="x-default" href="{esc(en_url)}">')
    footer_nav = "".join(f'<a href="{locale_path(url)}">{esc(tr(label, LANGUAGE))}</a>' for url, label in NAV)
    body = localize_links(localize_markup(body))
    title = localize_markup(title)
    description = localize_markup(description)
    return Template((ROOT / "templates" / "base.html").read_text(encoding="utf-8")).substitute(
        title=esc(title), description=esc(description), canonical=esc(canonical),
        og_type=esc(kind), og_locale="zh_CN" if LANGUAGE == "zh" else "en_US",
        nav=nav, body=body, analytics=analytics, year=str(date.today().year),
        robots=robots, gate_script=gate_script, skip_target=skip_target,
        html_lang="zh-CN" if LANGUAGE == "zh" else "en", alternates=alternate,
        language_script='<script src="/assets/language.js"></script>',
        skip_label=esc(tr("Skip to content", LANGUAGE)), home_url=locale_path("/"),
        home_label=esc(tr("byxiaoyu, home", LANGUAGE)), nav_label=esc(tr("Main navigation", LANGUAGE)),
        footer_intro=esc(tr("An independent notebook on numbers, stories, and everything between.", LANGUAGE)),
        footer_nav=footer_nav, language_label="语言" if LANGUAGE == "zh" else "Language",
        en_url=locale_path(base_path, "en"), zh_url=locale_path(base_path, "zh"),
        en_current=' aria-current="page"' if LANGUAGE == "en" else "",
        zh_current=' aria-current="page"' if LANGUAGE == "zh" else "",
    )


def write(path: str, markup: str) -> None:
    target = OUT / path.lstrip("/")
    if path.endswith("/"):
        target /= "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(markup, encoding="utf-8")


def section_head(kicker: str, title: str, aside: str = "") -> str:
    return f'<div class="section-heading"><div><p class="eyebrow">{esc(kicker)}</p><h2>{title}</h2></div><p class="section-aside">{esc(aside)}</p></div>'


def project_row(item: dict, number: int) -> str:
    url = f"/work/{item['slug']}/"
    accessible_label = f"阅读研究案例：{item['title']}" if LANGUAGE == "zh" else f"Read {item['title']} case study"
    return f'''<article class="project-row">
      <span class="row-number">0{number}</span>
      <div><p class="item-meta">{esc(item.get('status', 'Planned concept'))} · {esc(item.get('field', 'Research'))}</p>
      <h3><a href="{url}">{esc(item['title'])}</a></h3><p>{esc(item.get('summary', ''))}</p></div>
      <a class="row-arrow" href="{url}" aria-label="{esc(accessible_label)}">↗</a>
    </article>'''


def entry_card(item: dict, category: str) -> str:
    url = f"/{category}/{item['slug']}/"
    meta = f"{esc(item.get('category', 'Research note'))} · {pretty_date(item.get('date', ''))} · {reading_time(item['body'])}"
    return f'''<article class="entry-card"><p class="item-meta">{meta}</p>
      <h3><a href="{url}">{esc(item['title'])}</a></h3>
      <p>{esc(item.get('summary', ''))}</p>{link(url, 'Read the note')}</article>'''


def home(projects: list[dict], journal: list[dict], photos: list[dict]) -> str:
    rows = "".join(project_row(item, i) for i, item in enumerate(projects[:2], 1))
    note = entry_card(journal[0], "journal") if journal else ""
    journal_label = "From the research blog"
    if is_private("/photography/"):
        photo_preview = '<div class="private-photo-preview" aria-hidden="true"><span>THE VISUAL NOTEBOOK</span><b>✳</b></div>'
        preview_notice = ""
        photo_description = "A visual notebook of travel, cities, and ordinary moments, behind the gate."
    else:
        photo_preview = "".join(f'<img src="{esc(photo["file"])}" alt="{esc(photo["alt"])}" loading="lazy" decoding="async" width="800" height="600">' for photo in photos[:2])
        preview_notice = '<p class="placeholder-caption">Illustrative placeholders — photographs coming later.</p>' if any(p.get("placeholder") for p in photos[:2]) else ""
        photo_description = "A visual notebook from travel and everyday life."
    return f'''<main id="main">
      <section class="hero wrap" aria-labelledby="hero-title">
        <div class="hero-top"><span class="eyebrow">An independent notebook · {date.today().year}</span><span class="hero-index">OL / XY &nbsp; — &nbsp; 001</span></div>
        <div class="hero-grid"><div><h1 id="hero-title">Hi, I'm<br>Olivia Li.<br><em>Also Xiaoyu.</em></h1>
          <p class="hero-credential">NCSU graduate <span aria-hidden="true">/</span> Master of Financial Mathematics</p>
          <p class="hero-lede">Curious about numbers, stories, places, and everything in between.</p>
          <div class="hero-actions">{link('/work/', 'Explore my work', 'button-link')}{link('/about/', 'A little about me')}</div></div>
          <div class="hero-note"><span class="note-rule"></span><p class="eyebrow">A point of view</p>
          <p>I work at the intersection of quantitative risk, financial mathematics, and careful questions. Away from the models: cinema, photographs, books, and the wider world.</p>
          <span class="asterisk" aria-hidden="true">✳</span></div></div>
        <div class="hero-bottom"><span>Finance &amp; research</span><span>Cinema &amp; observations</span><span>Elsewhere, in between</span></div>
      </section>
      <section class="section work-section" aria-labelledby="selected-work"><div class="wrap">
        {section_head('01 / Work & research', '<span id="selected-work">Questions worth testing.</span>', 'An implemented risk workflow and a planned equity research direction.')}
        <div class="project-list">{rows}</div><div class="section-end">{link('/work/', 'All work & research')}</div>
      </div></section>
      <section class="section journal-section" aria-labelledby="journal-title"><div class="wrap journal-layout">
        <div>{section_head('02 / Research Notes', '<span id="journal-title">Questions behind the numbers.</span>')}
          <p class="section-intro">Notes on portfolio risk, financial data, modeling choices, and research practice.</p>
          {link('/journal/', 'Read research notes')}</div>
        <div class="featured-note"><span class="eyebrow">{journal_label}</span>{note}</div>
      </div></section>
      <section class="section film-section"><div class="wrap film-layout"><div><span class="eyebrow">03 / Film notes</span><h2>Some stories stay<br><em>after the credits.</em></h2>
        <p>Space for close attention to film: what it shows, what it leaves unsaid, and what lingers.</p>{link('/film/', 'Browse film notes')}</div>
        <div class="film-mark" aria-hidden="true"><div class="film-circle"></div><span>FRAME / FEELING / MEMORY</span></div></div></section>
      <section class="section photo-section"><div class="wrap">
        {section_head('04 / Photography', 'Looking, slowly.', photo_description)}
        <div class="home-photo-grid">{photo_preview}</div>
        {preview_notice}{link('/photography/', 'Open the gallery')}
      </div></section>
    </main>'''


def page_intro(kicker: str, title: str, description: str, extra_class: str = "") -> str:
    classes = "page-intro wrap" + (f" {extra_class}" if extra_class else "")
    return f'<header class="{classes}"><p class="eyebrow">{esc(kicker)}</p><h1>{title}</h1><p class="page-lede">{esc(description)}</p></header>'


def experience_section(roles: list[dict]) -> str:
    entries = []
    for role in roles:
        focus = " · ".join(esc(item) for item in role["focus"])
        entries.append(f'''<article class="experience-area experience-area--{esc(role['tone'])}"><div class="experience-area-heading"><p class="timeline-period">{esc(role['period'])}</p><h3>{esc(role['area'])}</h3></div>
          <div class="experience-area-copy"><p>{esc(role['description'])}</p><p class="experience-focus-line"><span>Focus</span>{focus}</p></div></article>''')
    return f'''<section class="work-experience work-block" aria-labelledby="experience-title"><div class="wrap">
      <div class="work-heading"><p class="eyebrow">01 / Professional experience</p><h2 id="experience-title">A foundation in<br><em>financial risk.</em></h2>
      <p>Two areas of experience across portfolio and market risk, with quantitative work and reporting at the center.</p></div>
      <div class="experience-areas">{''.join(entries)}</div></div></section>'''


def case_study_card(item: dict, number: int) -> str:
    path = f"/work/{item['slug']}/"
    source = link(item["repository"], "View source code") if item.get("repository") else ""
    method_label = ("Translation pending" if item.get("translation_missing") else
                    "Proposed method" if item.get("stage") == "planned" else "Implemented method")
    return f'''<article class="case-card case-card--{esc(item['stage'])}"><div class="case-card-meta"><span>0{number} / {esc(item.get('field', 'Research'))}</span><span class="case-status">{esc(item['status'])}</span></div>
      <h3><a href="{path}">{esc(item['title'])}</a></h3>
      <div class="case-question"><p class="case-label">Research question</p><p>{esc(item['question'])}</p></div>
      <p class="case-summary">{esc(item['summary'])}</p>
      <div class="case-method"><p class="case-label">{method_label}</p><p>{esc(item['approach'])}</p></div>
      <div class="case-card-links">{link(path, 'Explore case study')}{source}</div></article>'''


def expertise_section(expertise: dict) -> str:
    cards = []
    research_note = ""
    for number, category in enumerate(expertise["categories"], 1):
        if category["kind"] == "research":
            published = [skill for skill in category["skills"] if skill.get("published")]
            if not published:
                research_note = f'''<div class="research-methods-note"><span class="eyebrow">0{number} / {esc(category['title'])}</span>
                  <p>Research methods will be listed when supported by a completed case study or confirmed experience.</p></div>'''
                continue
            groups = [('Confirmed research methods', published)]
        else:
            groups = [
                ('In professional roles', [skill for skill in category['skills'] if skill['evidence'] == 'role']),
                ('Additional toolkit', [skill for skill in category['skills'] if skill['evidence'] == 'supplied']),
            ]
        skill_groups = []
        for label, skills in groups:
            if not skills:
                continue
            items = []
            for skill in skills:
                name = esc(skill["name"])
                if skill.get("source"):
                    name = f'<a href="{esc(skill["source"])}">{name}</a>'
                items.append(f'<li class="{"is-core" if skill.get("core") or category["kind"] == "research" else "is-secondary"}">{name}</li>')
            skill_groups.append(f'<div class="skill-group"><p class="skill-context">{esc(label)}</p><ul class="skill-tags">{"".join(items)}</ul></div>')
        cards.append(f'''<article class="expertise-card expertise-card--{esc(category['kind'])}"><div class="expertise-card-top"><span>0{number}</span><h3>{esc(category['title'])}</h3></div>
          {''.join(skill_groups)}</article>''')
    return f'''<section class="expertise-section work-block" aria-labelledby="expertise-title"><div class="wrap">
      <div class="work-heading"><p class="eyebrow">03 / Technical Expertise &amp; Toolkit</p><h2 id="expertise-title">The working<br><em>toolkit.</em></h2>
      <p>Financial domain knowledge, analytical programming, and the systems used to examine portfolio risk.</p></div>
      <div class="expertise-grid">{''.join(cards)}</div>{research_note}</div></section>'''


def work_index(projects: list[dict], roles: list[dict], expertise: dict) -> str:
    cards = "".join(case_study_card(item, i) for i, item in enumerate(projects, 1))
    return f'''<main id="main">{page_intro('Work & research', 'Risk, research,<br><em>and the work between.</em>', 'Exploring financial risk, portfolio analytics, and quantitative research through data, models, and code.', 'work-page-intro')}
      {experience_section(roles)}
      <section class="work-projects work-block" aria-labelledby="projects-title"><div class="wrap">
        <div class="work-heading"><p class="eyebrow">02 / Selected projects</p><h2 id="projects-title">Questions worth<br><em>testing.</em></h2>
        <p>Independent studies in portfolio risk and equity research.</p></div>
        <div class="case-grid">{cards}</div></div></section>
      {expertise_section(expertise)}</main>'''


def project_detail(item: dict) -> str:
    repo = item.get("repository", "")
    repo_html = link(repo, "View repository") if repo else '<span class="muted">Repository link will be added when available.</span>'
    steps = [step.strip() for step in item.get("pipeline", "").split("|") if step.strip()]
    pipeline = (f'<section class="project-pipeline" aria-label="Implementation pathway"><p class="eyebrow">Implementation pathway</p><ol>{"".join(f"<li>{esc(step)}</li>" for step in steps)}</ol></section>' if steps else "")
    kicker = "Research brief / " if item.get("stage") == "planned" else "Case study / "
    return f'''<main id="main"><div class="wrap breadcrumb"><a href="/work/">← All work</a><span> / {esc(item['title'])}</span></div>
      {page_intro(kicker + item.get('status', 'Planned concept'), esc(item['title']), item.get('summary', ''))}
      <div class="wrap detail-grid"><aside class="detail-sidebar"><p class="eyebrow">At a glance</p><dl>
        <dt>Area</dt><dd>{esc(item.get('field', 'Research'))}</dd><dt>Status</dt><dd>{esc(item.get('status', 'Planned concept'))}</dd>
        <dt>Code</dt><dd>{repo_html}</dd></dl></aside>
        <article class="prose">{pipeline}{markdown(item['body'])}</article></div></main>'''


def journal_index(items: list[dict]) -> str:
    cards = "".join(entry_card(item, "journal") for item in items)
    return f'''<main id="main">{page_intro('Research Notes / 02', 'Questions behind<br><em>the numbers.</em>', 'A public research blog on portfolio risk, quantitative methods, and financial data.')}
      <section class="wrap content-section"><div class="intro-rule"><span>Latest notes</span><span>Models & methods</span></div><div class="entry-grid">{cards}</div></section></main>'''


def article_detail(item: dict, section: str) -> str:
    is_film = section == "film"
    back = "Film notes" if is_film else "Research Notes"
    total_text = item["body"] + " " + item.get("spoilers", "")
    if is_film and item.get("status") in ("Awaiting review", "影评待写"):
        meta = "Film note in preparation"
    else:
        meta = f"{esc(item.get('category', 'Film note' if is_film else 'Research note'))} · {pretty_date(item.get('date', ''))} · {reading_time(total_text)}"
    extra = ""
    if is_film:
        film_meta = []
        if item.get("year"):
            film_meta.append("Released " + esc(item["year"]))
        if item.get("watched"):
            watched = pretty_date(item["watched"]) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", item["watched"]) else item["watched"]
            film_meta.append("Watched " + esc(watched))
        if item.get("rating"):
            film_meta.append("Personal rating " + esc(item["rating"]))
        if film_meta:
            extra = f'<p class="film-facts">{" · ".join(film_meta)}</p>'
    spoiler = ""
    if item.get("spoilers", "").strip():
        spoiler = f'<details class="spoilers"><summary>Spoilers / open this section</summary><div class="prose">{markdown(item["spoilers"])}</div></details>'
    cover = ""
    if item.get("cover"):
        if not item["cover"].startswith("/assets/") or not item.get("cover_alt"):
            raise ValueError(f"Cover in {item['slug']} needs an /assets/ path and cover_alt")
        cover = f'<figure class="article-cover"><img src="{esc(item["cover"])}" alt="{esc(item["cover_alt"])}" width="1200" height="800" decoding="async"></figure>'
    return f'''<main id="main"><div class="wrap breadcrumb"><a href="/{section}/">← {back}</a></div>
      <article class="article-page"><header class="article-header"><p class="eyebrow">{meta}</p><h1>{esc(item['title'])}</h1><p class="article-deck">{esc(item.get('summary', ''))}</p>{extra}<div class="tags">{tags(item)}</div></header>
      {cover}<div class="prose">{markdown(item['body'])}</div>{spoiler}</article></main>'''


def film_index(items: list[dict]) -> str:
    cards = []
    for i, item in enumerate(items, 1):
        if item.get("cover"):
            art = f'<img class="film-card-cover" src="{esc(item["cover"])}" alt="{esc(item.get("cover_alt", ""))}" loading="lazy" decoding="async" width="800" height="500">'
        else:
            art = f'<div class="film-card-art" aria-hidden="true"><span>{"影" if LANGUAGE == "zh" else "F"} / {i:02d}</span><div class="art-circle"></div></div>'
        facts = [item.get("year") or "Year to add", item.get("category") or "Film note"]
        if item.get("status") in ("Awaiting review", "影评待写"):
            facts.append("Review forthcoming")
        if item.get("watched"):
            facts.append("Watched " + (pretty_date(item["watched"]) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", item["watched"]) else item["watched"]))
        if item.get("rating"):
            facts.append("Rating " + item["rating"])
        if item.get("status") not in ("Awaiting review", "影评待写"):
            facts.append(reading_time(item["body"] + " " + item.get("spoilers", "")))
        action = "Open film entry" if item.get("status") in ("Awaiting review", "影评待写") else "Read the note"
        cards.append(f'''<article class="film-card">{art}<div class="film-card-copy"><p class="item-meta">{' · '.join(esc(x) for x in facts)}</p>
          <h2><a href="/film/{esc(item['slug'])}/">{esc(item['title'])}</a></h2><p>{esc(item.get('summary', ''))}</p><div class="tags">{tags(item)}</div>{link('/film/' + item['slug'] + '/', action)}</div></article>''')
    notice = '<p class="sample-notice">Film titles are listed here while their personal notes are in preparation.</p>' if any(item.get('status') in ('Awaiting review', '影评待写') for item in items) else ''
    return f'''<main id="main">{page_intro('Film notes / 03', 'The art of<br><em>paying attention.</em>', 'An archive of close readings, small observations, and films that invite another look.')}
      <section class="wrap content-section"><div class="intro-rule"><span>Film archive</span><span>Thoughtful notes, no spoilers up front</span></div>
        {notice}<div class="film-grid">{''.join(cards)}</div></section></main>'''


def photography(photos: list[dict]) -> str:
    cards = []
    for photo in photos:
        caption = photo.get("caption", "")
        caption_html = f'<figcaption><strong>{esc(caption)}</strong><span>{esc(photo["category"].title())}{" · illustration placeholder" if photo.get("placeholder") else ""}</span></figcaption>' if caption else ""
        cards.append(f'''<figure class="photo-card" data-category="{esc(photo['category'])}"><button class="photo-open" type="button" data-src="{esc(photo['file'])}" data-alt="{esc(photo['alt'])}" data-caption="{esc(caption)}" data-placeholder="{str(bool(photo.get('placeholder'))).lower()}" aria-label="Open {esc(caption or photo['alt'])}">
          <img src="{esc(photo['file'])}" alt="{esc(photo['alt'])}" loading="lazy" decoding="async" width="800" height="600"></button>{caption_html}</figure>''')
    notice = '<p class="sample-notice">These abstract illustrations mark where original photographs will go. They are not presented as Olivia\'s photographs.</p>' if any(photo.get("placeholder") for photo in photos) else ""
    return f'''<main id="main">{page_intro('Photography / 04', 'A practice of<br><em>looking closer.</em>', 'An evolving visual notebook for travel, cities, and ordinary moments.')}
      <section class="wrap content-section">{notice}
      <div class="filter-bar" role="group" aria-label="Filter photographs"><button type="button" class="is-active" data-filter="all" aria-pressed="true">All frames</button><button type="button" data-filter="travel" aria-pressed="false">Travel</button><button type="button" data-filter="cities" aria-pressed="false">Cities</button><button type="button" data-filter="everyday" aria-pressed="false">Everyday</button></div>
      <div class="photo-grid">{''.join(cards)}</div></section>
      <dialog id="photo-dialog" class="photo-dialog" aria-label="Photograph preview"><button class="dialog-close" type="button" aria-label="Close image">×</button><img src="" alt=""><p></p></dialog>
      <script defer src="/assets/gallery.js"></script></main>'''


def about(journey: list[dict]) -> str:
    item = read_content(ROOT / "content" / LANGUAGE / "pages" / "about.md")
    beyond = read_content(ROOT / "content" / LANGUAGE / "pages" / "about-beyond.md")
    entries = []
    for entry in journey:
        organization = f'<p class="journey-organization">{esc(entry["organization"])}</p>' if entry.get("organization") else ""
        description = f'<p>{esc(entry["description"])}</p>' if entry.get("description") else ""
        entries.append(f'''<article class="journey-entry"><div class="journey-when"><strong>{esc(entry['years'])}</strong><span>{esc(entry['location'])}</span></div>
          <div class="journey-copy"><h3>{esc(entry['title'])}</h3>{organization}{description}</div></article>''')
    return f'''<main id="main">{page_intro('About / 05', 'Olivia Li<br><em>(Xiaoyu).</em>', item.get('summary', ''))}
      <section class="about-intro about-section wrap" aria-labelledby="about-intro-title"><div><p class="eyebrow">01 / Introduction</p><h2 id="about-intro-title">A little<br><em>about me.</em></h2></div>
      <div class="prose">{markdown(item['body'])}</div></section>
      <section class="journey-section about-section" aria-labelledby="journey-title"><div class="wrap"><div class="about-section-heading"><p class="eyebrow">02 / My Journey</p><h2 id="journey-title">Places and<br><em>paths.</em></h2></div>
      <div class="journey-list">{''.join(entries)}</div></div></section>
      <section class="beyond-section about-section wrap" aria-labelledby="beyond-title"><div><p class="eyebrow">03 / Beyond Work</p><h2 id="beyond-title">Outside the<br><em>numbers.</em></h2></div>
      <div><div class="prose">{markdown(beyond['body'])}</div><div class="beyond-links">{link('/film/', 'Film notes')}{link('/photography/', 'Photography')}</div></div></section>
      <section class="about-connect about-section" aria-labelledby="about-connect-title"><div class="wrap about-connect-inner"><div><p class="eyebrow">04 / Connect</p><h2 id="about-connect-title">Continue the<br><em>conversation.</em></h2></div>
      <div><p>Find my public work on GitHub, or visit the contact page for a way to get in touch.</p><div class="beyond-links">{link('https://github.com/OliviaLi22', 'GitHub')}{link('/contact/', 'Contact')}</div></div></div></section></main>'''


def contact() -> str:
    return f'''<main id="main">{page_intro('Contact / 06', 'Keep the<br><em>conversation going.</em>', 'For professional conversations, project questions, or a thoughtful note, you can reach me by email or find my work on GitHub.')}
      <section class="wrap contact-section"><a class="contact-link" href="https://github.com/OliviaLi22" rel="me"><span><small>Verified profile</small><strong>GitHub</strong><span>github.com/OliviaLi22</span></span><b aria-hidden="true">↗</b></a>
      <a class="contact-link" href="mailto:mailtoolivia22@gmail.com"><span><small>Get in touch</small><strong>Email</strong><span>mailtoolivia22@gmail.com</span></span><b aria-hidden="true">↗</b></a>
      <p>LinkedIn can be added here if I choose to share it later.</p></section></main>'''


def missing_translation(item: dict, section: str) -> dict:
    """Create a clearly labeled, indexable-list stub, never English article copy."""
    result = dict(item)
    result["summary"] = "此内容暂无中文译文。"
    result["body"] = ("## 翻译待补充\n\n这篇内容尚未翻译。可通过下方链接阅读英文原文。\n\n"
                      f"[阅读英文原文](https://byxiaoyu.com/{section}/{item['slug']}/)")
    result["category"] = "翻译待补充"
    result["tags"] = "翻译待补充"
    result["translation_missing"] = True
    if section == "work":
        result.update(status="翻译待补充", field="研究", question="中文译文待补充。", approach="请阅读英文原文。", pipeline="")
    if section == "film":
        result["status"] = "影评待写" if item.get("status") == "Awaiting review" else "翻译待补充"
    return result


class LocalLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.h1_count = 0
        self.main_count = 0
        self.missing_alts = 0
        self.ids = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "h1":
            self.h1_count += 1
        if tag == "main" and values.get("id") == "main":
            self.main_count += 1
        if tag == "img" and "alt" not in values:
            self.missing_alts += 1
        if "id" in values:
            self.ids.append(values["id"])
        for key in ("href", "src"):
            if key in values:
                self.links.append(values[key])


def check_links() -> None:
    missing = []
    structure = []
    for page in OUT.rglob("*.html"):
        parser = LocalLinks()
        parser.feed(page.read_text(encoding="utf-8"))
        if parser.h1_count != 1 or parser.main_count != 1 or parser.missing_alts or len(parser.ids) != len(set(parser.ids)):
            structure.append(f"{page.relative_to(OUT)}: h1={parser.h1_count}, main={parser.main_count}, missing alts={parser.missing_alts}, duplicate ids={len(parser.ids) - len(set(parser.ids))}")
        for url in parser.links:
            parsed = urlparse(url)
            if parsed.scheme or parsed.netloc or url.startswith("#"):
                continue
            target = OUT / parsed.path.lstrip("/") if parsed.path.startswith("/") else page.parent / parsed.path
            if target.is_dir() or parsed.path.endswith("/"):
                target /= "index.html"
            if not target.exists():
                missing.append(f"{page.relative_to(OUT)} → {url}")
    if missing:
        raise ValueError("Broken local links:\n" + "\n".join(missing))
    if structure:
        raise ValueError("Invalid page structure:\n" + "\n".join(structure))
    if (OUT / "CNAME").read_text(encoding="utf-8").strip() != "byxiaoyu.com":
        raise ValueError("Custom domain CNAME was not preserved")


def check_localization() -> None:
    problems = []
    for english in OUT.rglob("*.html"):
        relative = english.relative_to(OUT)
        if relative.parts[0] == "zh":
            continue
        chinese = OUT / "zh" / relative
        if not chinese.exists():
            problems.append(f"Missing Chinese page for {relative}")
            continue
        base = "/" + str(relative.parent).replace(".", "").strip("/") + "/" if relative.name == "index.html" else "/" + str(relative)
        if base == "//":
            base = "/"
        for lang, page, route in (("en", english, base), ("zh", chinese, "/zh" + base)):
            source = page.read_text(encoding="utf-8")
            expected_lang = "zh-CN" if lang == "zh" else "en"
            for required in (
                f'<html lang="{expected_lang}">',
                f'<link rel="canonical" href="{SITE_URL + route}">',
                f'<meta property="og:locale" content="{"zh_CN" if lang == "zh" else "en_US"}">',
                f'href="{base}" lang="en" data-language="en"',
                f'href="/zh{base}" lang="zh-CN" data-language="zh"',
                f'data-language="{lang}" aria-current="page"',
            ):
                if required not in source:
                    problems.append(f"{page.relative_to(OUT)} missing {required}")
            if base not in MISSING_TRANSLATIONS and 'hreflang="zh-CN"' not in source:
                problems.append(f"{page.relative_to(OUT)} missing Chinese alternate")
            if lang == "zh" and base in MISSING_TRANSLATIONS:
                if 'name="robots" content="noindex' not in source or "此内容暂无中文译文" not in source:
                    problems.append(f"{page.relative_to(OUT)} does not identify missing translation")
    if problems:
        raise ValueError("Localization validation failed:\n" + "\n".join(problems))


def check_section_access() -> None:
    """Keep the research blog public and the two personal archives gated."""
    sitemap = (OUT / "sitemap.xml").read_text(encoding="utf-8")
    problems = []
    for page in OUT.rglob("*.html"):
        parts = page.relative_to(OUT).parts
        lang = "zh" if parts[0] == "zh" else "en"
        section_parts = parts[1:] if lang == "zh" else parts
        section = section_parts[0]
        if section not in ("journal", "film", "photography"):
            continue
        base = "/" + "/".join(section_parts[:-1]) + "/"
        route = "/zh" + base if lang == "zh" else base
        source = page.read_text(encoding="utf-8")
        in_sitemap = f"<loc>{SITE_URL + route}</loc>" in sitemap
        has_gate = 'id="gate-screen"' in source and 'src="/assets/gate.js"' in source
        has_noindex = 'name="robots" content="noindex' in source
        if section == "journal":
            untranslated = lang == "zh" and base in MISSING_TRANSLATIONS
            if has_gate or has_noindex != untranslated or in_sitemap == untranslated:
                problems.append(f"{route} must be a public research note, unless its Chinese translation is pending")
        elif not has_gate or not has_noindex or in_sitemap:
            problems.append(f"{route} must retain the personal gate and stay out of the sitemap")
    if problems:
        raise ValueError("Section access validation failed:\n" + "\n".join(problems))


def main() -> None:
    global LANGUAGE
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Build and validate local links")
    args = parser.parse_args()
    collections = {}
    for lang in ("en", "zh"):
        LANGUAGE = lang
        root = ROOT / "content" / lang
        data = {
            "projects": content_collection("work"), "journal": content_collection("journal"),
            "films": content_collection("film"),
            "roles": json.loads((root / "experience.json").read_text(encoding="utf-8")),
            "journey": json.loads((root / "journey.json").read_text(encoding="utf-8")),
            "expertise": json.loads((root / "expertise.json").read_text(encoding="utf-8")),
            "photos": json.loads((root / "photos.json").read_text(encoding="utf-8")),
        }
        for photo in data["photos"]:
            if photo.get("category") not in ("travel", "cities", "everyday") or not photo.get("file", "").startswith("/assets/") or not photo.get("alt"):
                raise ValueError(f"Each {lang} photo needs file, alt, and a supported category")
        for item in data["projects"] + data["journal"] + data["films"]:
            if not item.get("title") or not item.get("summary"):
                raise ValueError(f"Missing {lang} title or summary in {item['slug']}")
        for item in data["projects"]:
            if not item.get("question") or not item.get("approach"):
                raise ValueError(f"Missing {lang} research question or methodology preview in {item['slug']}")
            if item.get("stage") not in ("planned", "prototype", "complete"):
                raise ValueError(f"Project {item['slug']} needs a planned, prototype, or complete stage")
            if item["stage"] != "planned" and not item.get("repository"):
                raise ValueError(f"Implemented project {item['slug']} needs a verified repository")
        for role in data["roles"]:
            if not all(role.get(key) for key in ("area", "period", "description", "focus")):
                raise ValueError(f"{lang} experience areas need area, period, description, and focus")
            if role.get("tone") not in ("sage", "terracotta"):
                raise ValueError(f"{lang} experience area {role['area']} needs a supported tone")
        for entry in data["journey"]:
            if not all(entry.get(key) for key in ("years", "location", "title")):
                raise ValueError(f"{lang} journey entries need years, location, and title")
        journey_years = [int(re.match(r"^\d{4}", entry["years"]).group()) for entry in data["journey"]]
        if journey_years != sorted(journey_years, reverse=True):
            raise ValueError(f"{lang} journey entries must be in reverse chronological order")
        for category in data["expertise"]["categories"]:
            if category.get("kind") not in ("toolkit", "research") or not category.get("title"):
                raise ValueError(f"{lang} expertise category needs title and kind")
            for skill in category.get("skills", []):
                if not skill.get("name"):
                    raise ValueError(f"{lang} expertise skill needs a name")
                if category["kind"] == "toolkit" and skill.get("evidence") not in ("role", "supplied"):
                    raise ValueError(f"Toolkit skill {skill['name']} needs role or supplied evidence")
                if category["kind"] == "research" and skill.get("published") and not (skill.get("source") or skill.get("confirmed")):
                    raise ValueError(f"Published research method {skill['name']} needs a case-study source or confirmation")
        collections[lang] = data

    # English is the source language. New English entries without a Chinese file
    # get an explicit Chinese stub, never a silently untranslated article.
    for section, key in (("work", "projects"), ("journal", "journal"), ("film", "films")):
        english = {item["slug"]: item for item in collections["en"][key]}
        chinese = {item["slug"]: item for item in collections["zh"][key]}
        extra = set(chinese) - set(english)
        if extra:
            raise ValueError(f"Chinese {section} items require English counterparts: {sorted(extra)}")
        for slug in set(english) - set(chinese):
            collections["zh"][key].append(missing_translation(english[slug], section))
            MISSING_TRANSLATIONS.add(f"/{section}/{slug}/")
        if section == "work":
            collections["zh"][key].sort(key=lambda item: (int(item.get("order", "999")), item["slug"]))
        else:
            collections["zh"][key].sort(key=lambda item: (item.get("date", ""), item["slug"]), reverse=True)
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    shutil.copy2(ROOT / "CNAME", OUT / "CNAME")
    routes = []

    def add(path, title, description, body, active="", kind="website"):
        actual = locale_path(path)
        write(actual, shell(title + " | byxiaoyu.", description, actual, body, active, kind))
        if not is_private(path) and not (LANGUAGE == "zh" and path in MISSING_TRANSLATIONS):
            routes.append(actual)

    for lang in ("en", "zh"):
        LANGUAGE = lang
        data = collections[lang]
        projects, journal, films = data["projects"], data["journal"], data["films"]
        add("/", "Olivia Li / Xiaoyu", "Quantitative risk, research, cinema, and the spaces between.", home(projects, journal, data["photos"]))
        add("/work/", "Work & Research", "Financial risk experience, independent quantitative research, and technical expertise.", work_index(projects, data["roles"], data["expertise"]), "/work/")
        for item in projects:
            add(f"/work/{item['slug']}/", item["title"], item["summary"], project_detail(item), "/work/", "article")
        add("/journal/", "Research Notes", "A research blog on portfolio risk, quantitative methods, and financial data.", journal_index(journal), "/journal/")
        for item in journal:
            add(f"/journal/{item['slug']}/", item["title"], item["summary"], article_detail(item, "journal"), "/journal/", "article")
        add("/film/", "Film Notes", "Thoughtful notes on cinema.", film_index(films), "/film/")
        for item in films:
            add(f"/film/{item['slug']}/", item["title"], item["summary"], article_detail(item, "film"), "/film/", "article")
        add("/photography/", "Photography", "A visual notebook for photographs from travel and everyday life.", photography(data["photos"]), "/photography/")
        add("/about/", "About", "Olivia Li (Xiaoyu): financial risk, graduate studies, and a personal journey.", about(data["journey"]), "/about/")
        add("/contact/", "Contact", "Contact Olivia Li by email or on GitHub.", contact(), "/contact/")
        error_path = locale_path("/404.html")
        write(error_path, shell("Page not found | byxiaoyu.", "This page could not be found.", error_path, '<main id="main" class="wrap error-page"><p class="eyebrow">404 / A missing page</p><h1>Somewhere else,<br><em>perhaps.</em></h1><p>This page has moved or never existed.</p>' + link("/", "Return home", "button-link") + "</main>"))
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{esc(SITE_URL + route)}</loc></url>\n" for route in routes) + "</urlset>\n"
    (OUT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    if args.check:
        check_links()
        check_localization()
        check_section_access()
    page_count = sum(1 for _ in OUT.rglob("*.html"))
    print(f"Built {page_count} pages in {OUT}" + ("; links, locales, section access, and CNAME verified" if args.check else ""))


if __name__ == "__main__":
    main()
