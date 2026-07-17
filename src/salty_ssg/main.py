import json

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from salty_ssg.utils import load_site_metadata, load_page_metadata, load_page_content, load_page_breadcrumbs, format_sitemaps_data, load_microsite_sitemap_urls
from salty_ssg.utils_schema import get_schema
from salty_ssg.settings import settings

script_dir = Path(__file__).resolve().parent
theme_path = script_dir.parent.parent / "site" / "theme"

app = FastAPI()
app.mount("/static", StaticFiles(directory=f"{theme_path}/static"), name="static")

templates = Jinja2Templates(directory=f"{theme_path}/pages")

##################
# Landing pages: #
##################
# Homepage
@app.get("/index.json")
async def get_homepage_context():
    context = load_site_metadata()
    page = load_page_metadata("index")
    breadcrumbs = load_page_breadcrumbs("index", False)
    page["content"] = load_page_content("index")
    context["page"] = page
    page["schema"] = get_schema(context, breadcrumbs)
    return context

@app.get("/", response_class=HTMLResponse)
async def get_homepage(request: Request):
    context = await get_homepage_context()
    return templates.TemplateResponse(
        request=request, name="_index.html", context=context
    )

#########
# Blog: #
#########
# Sample dynamic slug pages (microsite)
@app.get("/blog/{slug}.json")
async def get_page_context(slug: str):
    context = load_site_metadata()
    page = load_page_metadata(f"blog/{slug}")
    breadcrumbs = load_page_breadcrumbs(f"blog/{slug}", False)
    page["content"] = load_page_content(f"blog/{slug}")
    page["type"] = "article"
    context["page"] = page
    page["schema"] = get_schema(context, breadcrumbs)
    return context

@app.get("/blog/{slug}/", response_class=HTMLResponse)
async def get_page(slug: str, request: Request):
    context = await get_page_context(slug)
    
    # Typically you would use a dedicated template here, like blog/[slug].html
    return templates.TemplateResponse(
        request=request, name="_default.html", context=context
    )

################
# Error pages: #
################
@app.get("/error/{code}.json")
async def get_error_page_context(code: str):
    context = load_site_metadata()
    page = load_page_metadata(f"error/{code}")
    context["page"] = page

    page["content"] = load_page_content(f"error/{code}")
    
    return context

@app.get("/error/{code}/", response_class=HTMLResponse)
async def get_error_page(request: Request, code: str):
    context = await get_error_page_context(code)
    return templates.TemplateResponse(
        request=request, name="_default.html", context=context
    )

#############
# Crawling: #
#############
# Basic sitemaps data - urlset will be empty for microsites sitemaps here
async def get_sitemaps():
    return format_sitemaps_data(app.routes)

# Sitemaps data for build process
@app.get("/sitemaps.json")
async def get_sitemaps_json(show_private: bool = True):
    sitemaps_data = format_sitemaps_data(app.routes)

    for name in sitemaps_data:
        if name == "main":
            continue
        sitemaps_data[name] = load_microsite_sitemap_urls(name, show_private)

    return sitemaps_data

# Individual sitemaps for live site
@app.get("/sitemaps/{name}.xml", response_class=Response)
async def get_sitemap_xml(request: Request, name: str):
    sitemaps_data = await get_sitemaps()

    # Return 404 if not a valid sitemap name
    if name not in sitemaps_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )
       
    urlset = sitemaps_data[name] if name == "main" else load_microsite_sitemap_urls(name)

    return templates.TemplateResponse(
        request=request, name="sitemaps/[name].xml", media_type="application/xml", context={"urlset": urlset}
    )

# Sitemaps data for build process
@app.get("/robots.txt")
async def get_robots(request: Request):
    sitemaps_data = await get_sitemaps_json(False)
    sitemaps_names = []
    for sitemap_name in sitemaps_data:
      if len(sitemaps_data[sitemap_name]) > 0:
        sitemaps_names.append(sitemap_name)

    context = {
        "domain": settings.prod_domain,
        "sitemap_names": sitemaps_names
    }

    return templates.TemplateResponse(
        request=request, name="robots.txt", media_type="text/plain", context=context
    )
