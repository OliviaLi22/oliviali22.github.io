# Xiaoyu | Personal Website

A personal portfolio for Olivia Li (Xiaoyu), bringing quantitative risk work, independent research, and a few interests beyond finance into one editorial space.

**[Visit byxiaoyu.com](https://byxiaoyu.com)**

## Overview

This site is a long-term home for work and writing, rather than a résumé in website form. The Work page presents experience across investment risk and market risk alongside independent projects. The [Portfolio Risk Decision Engine](https://github.com/OliviaLi22/portfolio-risk-decision-engine) is documented as a research prototype with public source code; the Equity Quant Research Platform is clearly marked as a planned direction. Research Notes provides a public place for work-related writing on methods, data, and portfolio decisions.

Cinema and photography have their own quieter sections. Film entries and gallery illustrations are identified as placeholders until original notes and photographs are added. The site aims to feel like an independent research notebook: precise about evidence, but open to curiosity beyond the models.

## Website features

- **Work & Research:** professional experience, project case studies, and a clearly organized technical toolkit.
- **Research Notes:** a public blog in both languages for quantitative finance and analytical practice.
- **About & Contact:** a concise introduction, personal timeline, and verified ways to connect.
- **Film Notes & Photography:** personal archives behind a simple password screen. The static files remain public, so the screen is a presentation choice rather than secure access control.
- **English & Simplified Chinese:** paired pages with direct URLs for each language, a footer switcher, and translated interface copy.

## Design & technology

Warm ivory backgrounds, forest-green typography, serif headlines, restrained accents, and generous whitespace give the site its editorial character. The layout adapts to smaller screens without changing its visual language.

A small builder written with Python's standard library turns Markdown and JSON content into static pages. Hand-written CSS and a few vanilla JavaScript files handle the interface, language preference, and gallery. GitHub Actions builds the site for GitHub Pages at the custom domain. The repository uses no frontend framework, database, or external build dependency.

## Explore the website

The [live site](https://byxiaoyu.com) is the current visual preview. Start with [Work](https://byxiaoyu.com/work/), [Research Notes](https://byxiaoyu.com/journal/), or [About](https://byxiaoyu.com/about/). The same pages are available in [Simplified Chinese](https://byxiaoyu.com/zh/).

## Documentation

- [Architecture](docs/architecture.md) — how content becomes a bilingual static site
- [Development](docs/development.md) — local preview, build, and validation
- [Deployment](docs/deployment.md) — GitHub Pages, domain, analytics, and privacy
- [Maintenance](docs/maintenance.md) — editing projects, notes, film entries, and photography
