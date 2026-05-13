# Salty SSG

A perfectly seasoned Static Site Generator

You:
- Maintain content in Markdown files
- Maintain metadata in YAML files
- Maintain a simple theme of templates, styles, and scripts without framework bloat and constant maintenance

Let Salty do the rest:
- Recompile individual pages to HTML when underlying content or designs change
- Recompile XML sitemaps with new dates
- Trigger global updates as needed

## Get started

1. Install python3
2. Install poetry
3. `poetry install`
4. `poetry run pytest`
5. In /src/salty_ssg, run `poetry run uvicorn main:app --reload`
6. See a sample page: http://127.0.0.1:8000
7. See your API: http://127.0.0.1:8000/index.json
8. See the docs: http://127.0.0.1:8000/docs
9. Edit site/content/meta.yml, site/content/pages/index.yml, site/content/pages/index.md and reload to see your changes