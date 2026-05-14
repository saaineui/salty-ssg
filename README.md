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

Or with test coverage:

1. `poetry run coverage run -m pytest`
2. `poetry run coverage report`

## Site setup

1. Copy .env.example to a new .env file and update `SALTY_TARGET` and `PROD_DOMAIN` with your values.
2. Create an empty directory at your `SALTY_TARGET` location locally.

## Run your first build

From within src/salty_ssg, run:

`poetry run python build.py --checkall`

Your static site files should now exist in your target folder. If you open them in a browser, they will likely be missing styles as base tag is set to `PROD_DOMAIN` now. 