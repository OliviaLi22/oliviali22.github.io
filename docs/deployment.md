# Deployment, domain, and privacy

[Back to the project overview](../README.md) · [Local development](development.md) · [Architecture](architecture.md)

## GitHub Pages

The [Pages workflow](../.github/workflows/pages.yml) runs `python3 build.py --check` on pull requests and pushes to `main`. Pull requests validate without deploying. A push to `main`, or a manual workflow run on `main`, uploads `dist/` and deploys it to GitHub Pages. Review a change before merging or pushing it to `main`.

In **Repository Settings → Pages → Build and deployment**, the source should be **GitHub Actions**. The repository root is source code; the workflow publishes the generated `dist/` artifact. After a deployment, check the workflow result and open both `/work/` and `/zh/work/` on the public domain.

## Custom domain and DNS

The root [`CNAME`](../CNAME) associates the site with `byxiaoyu.com`; the builder copies it into `dist/`, and the build check verifies its value. Keep both this file and the custom-domain setting in GitHub Pages. Cloudflare manages DNS outside this repository. The workflow does not edit Cloudflare records or Pages settings, and this documentation does not prescribe DNS values that have not been verified here.

## Cloudflare Web Analytics

The optional `cloudflare_web_analytics_token` field is centralized in [`site.json`](../site.json). It is currently empty, so the builder emits no analytics script. To enable analytics, create a Web Analytics site in Cloudflare, insert its real 32-character token, and rebuild. The builder then inserts Cloudflare's official beacon script. Avoid adding a second snippet if Cloudflare already injects one for the domain.

Cloudflare can report page views, provider-defined unique visitors, popular pages, referrers, and geographic trends. These reports do not identify individual visitors. The site adds no analytics cookies of its own.

## Personal-section gate

Film Notes and Photography use a password screen. The expected password is stored as a SHA-256 hash in `site.json`, and a successful unlock is remembered in `sessionStorage` for the current browser tab. To replace the hash, run the command below and paste the result into `personal_gate_sha256`:

```sh
python3 -c 'import getpass,hashlib; print(hashlib.sha256(getpass.getpass("New password: ").encode()).hexdigest())'
```

This is **visual gating, not secure access control**. GitHub Pages serves static files publicly, and generated HTML and repository source can reveal the content. Never place private credentials, personal data, or confidential employer material in this repository. A genuinely private section would need authenticated hosting such as [Cloudflare Access](https://developers.cloudflare.com/cloudflare-one/access-controls/policies/app-paths/). See also [GitHub Pages security guidance](https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https).
