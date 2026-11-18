# Local development

[Back to the project overview](../README.md) · [Architecture](architecture.md) · [Deployment](deployment.md)

## Requirements

Use Python 3.11 to match the [GitHub Actions workflow](../.github/workflows/pages.yml). The build has no `pip` or `npm` dependencies and requires no environment variables. Run the commands below from the repository root. Optional site configuration is documented in [deployment](deployment.md).

## Preview

```sh
python3 preview.py
```

[`preview.py`](../preview.py) builds and validates the site, then prints the exact local address to open. It chooses a free port automatically and serves `dist/`. Add a page path such as `/work/` or `/zh/journal/` to the printed address. Do **not** add `/dist/` to the URL. Press `Ctrl-C` to stop the server.

## Build and validate

```sh
python3 build.py --check
```

The command recreates the ignored `dist/` directory. It checks internal links, one main heading and main region per page, image alt text, duplicate IDs, bilingual page metadata, public versus gated sections, and the generated `CNAME`. A failed check exits with an error describing the affected route or content field. The deployment workflow runs the same command before publishing.

For a build without validation, run `python3 build.py`. The generated files are outputs, not authoring files; edit the source in `content/`, `templates/`, or `assets/` instead.

## Common issues

- **Local 404:** use the exact address printed by `preview.py`. Serving the repository root or adding `/dist/` to the URL will not serve the generated routes correctly.
- **Missing Chinese article:** add the matching file under `content/zh/` with the same filename. Until then, the builder intentionally publishes a labeled translation-pending stub that is excluded from search indexing.
- **Broken local link or missing asset:** correct the source path and rerun `python3 build.py --check`.
- **Content validation error:** check required front matter and structured fields against [maintenance](maintenance.md). Do not edit `dist/` to repair generated output.
