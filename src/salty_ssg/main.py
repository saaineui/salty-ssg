from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from salty_ssg.utils import load_site_metadata, load_page_metadata, load_page_content

script_dir = Path(__file__).resolve().parent
theme_path = script_dir.parent.parent / "site" / "theme"

app = FastAPI()
app.mount("/static", StaticFiles(directory=f"{theme_path}/static"), name="static")

templates = Jinja2Templates(directory=f"{theme_path}/pages")

# Homepage
@app.get("/index.json")
# Add types eventually
async def get_homepage_context():
    context = load_site_metadata()
    page = load_page_metadata("_page")
    page["content"] = load_page_content("_page")
    context["page"] = page
    return context

@app.get("/", response_class=HTMLResponse)
async def get_homepage(request: Request):
    context = await get_homepage_context()
    return templates.TemplateResponse(
        request=request, name="index.html", context=context
    )
