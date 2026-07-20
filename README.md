<img width=324 height=80 src="https://stephsun.com/static/images/salty-logo-icon-wordmark.png" alt="Logo: Salty">

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

<a href="https://stephsun.com/static/videos/build_1.mp4" target="_blank"><img src="https://stephsun.com/static/images/salty-demo_1_btn.png" alt="Play Demo" width=400 height=320></a>

<a href="https://stephsun.com/static/videos/build_2.mp4" target="_blank"><img src="https://stephsun.com/static/images/salty-demo_2_btn.png" alt="Play Second Demo" width=400 height=320></a>

## Get started

1. Install python3
2. Install poetry
3. `poetry install`
4. `poetry run pytest`
5. Start server: `poetry run poe start`
6. See a sample page: http://127.0.0.1:8000
7. See your API: http://127.0.0.1:8000/index.json
8. See the docs: http://127.0.0.1:8000/docs
9. Edit site/content/meta.yml, site/content/pages/index.yml, site/content/pages/index.md and reload to see your changes
  - **Important:** Keep `domain: http://127.0.0.1:8000` in meta.yml so that local assets render—it will be replaced with your prod domain during builds
  - Tip: Use `[=================]` to add multiple content blocks to any of your content markdowns. `page.content` in your template will be an array of HTML blocks split on that delimiter

Or with test coverage:

1. `poetry run coverage run -m pytest`
2. `poetry run coverage report`

## Site setup

1. Copy .env.example to a new .env file and update `SALTY_TARGET` and `PROD_DOMAIN` with your values.
2. Create an empty directory at your `SALTY_TARGET` location locally.

## Run your first build

Salty generates two kinds of sitemaps out of the box—a private one used by builds and public sitemaps to deploy to production. Salty also generates a robots.txt using the template in site/theme/pages/ and static error pages using the templates and content in the pages/error subfolders.

Preview these artifacts prior to running your build at:

- http://127.0.0.1:8000/sitemaps.json (private sitemap: pages compiled at build time)
- http://127.0.0.1:8000/sitemaps/main.xml (public sitemap: one of the sitemaps compiled at build time)
- http://127.0.0.1:8000/robots.txt
- http://127.0.0.1:8000/error/404/
- http://127.0.0.1:8000/error/500/

Build your first static site at `SALTY_TARGET`:

`poetry run poe build --checkall`

(Without `--checkall` flag, Salty won't check dynamic path pages for errors before running the build.)

Your static site files should now exist in your target folder. If you open them in a browser, they will likely be missing static assets as base tag is set to `PROD_DOMAIN` now. Start a server in the root of your target folder and replace base tag href value with your local domain and port to spot check the compiled files before deploying.