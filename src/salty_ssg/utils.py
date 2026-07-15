import yaml
import re
from datetime import datetime
from pathlib import Path
from markdown_it import MarkdownIt
from typing import cast
from salty_ssg.types import SaltyContext, SaltyPage, StrictCrumb, StrictMeta, is_valid_meta, is_valid_page, StrictSitemapUrl
from fastapi import FastAPI
from fastapi.routing import APIRoute 
from starlette.routing import Route
from salty_ssg.settings import settings

markdown_delimiter = "[=================]"

script_dir = Path(__file__).resolve().parent
site_content_path = script_dir.parent.parent / "site" / "content"

md = (
    MarkdownIt('commonmark', {'breaks':True,'html':True})
)

def get_clean_path(path: str) -> str:
  return "index" if path == "/" or path == "" else re.sub(r"^/|/$", "", path)

def load_site_metadata() -> StrictMeta:
  with open(f"{site_content_path}/meta.yml", 'r') as file:
    try:
      meta = yaml.safe_load(file)
    except yaml.YAMLError as exc:
      raise RuntimeError(f"Error parsing YAML file: {exc}")

    meta = meta or { "site": {}, "author": {} }
    if not is_valid_meta(meta):
      raise TypeError("site/content/meta.yml is missing site and author data")
    
    return cast(StrictMeta, meta)

def get_file_modified_timestamp(path: str) -> float:
  page_file_path = f"{site_content_path}/pages/{path}"

  try:
    return Path(page_file_path).stat().st_mtime
  except FileNotFoundError as exc:
    return -0.1

def timestamp_to_datestring(timestamp: float) -> str:
  page_file_modified_timestamp_dateobj = datetime.fromtimestamp(timestamp)
  return f"{page_file_modified_timestamp_dateobj.strftime("%Y-%m-%dT%H:%M:%S")}+00:00"

def get_last_modified_for_path(path: str) -> str:
  path = get_clean_path(path)
  yml_file_modified_timestamp = get_file_modified_timestamp(path + ".yml")
  md_file_modified_timestamp = get_file_modified_timestamp(path + ".md")
  more_recent_timestamp = yml_file_modified_timestamp if yml_file_modified_timestamp > md_file_modified_timestamp else md_file_modified_timestamp
  return timestamp_to_datestring(more_recent_timestamp)

def sanitize_meta_content(content: str | None) -> str:
  content = content or ""
  # Only " is strictly forbidden from <meta content="" />
  return re.sub('"', '&quot;', content)

def load_page_metadata(path: str) -> SaltyPage:
  path = get_clean_path(path)
  date_modified = get_last_modified_for_path(path)

  with open(f"{site_content_path}/pages/{path}.yml", 'r') as file:
    try:
      meta = yaml.safe_load(file)
    except yaml.YAMLError as exc:
      raise RuntimeError(f"Error parsing YAML file: {exc}")
    
    if "page" not in meta:
      raise TypeError("site/content/pages/{path}.yml is missing data under a nested `page` key")
    
    if not is_valid_page(meta["page"]):
      raise TypeError("site/content/pages/{path}.yml is missing title, url, or date_published")

    # Get the latest from either yml or md file
    meta["page"]["date_modified"] = date_modified
    # We render title and description with "safe" in the template, so sanitize manually
    meta["page"]["title"] = sanitize_meta_content(meta["page"].get("title"))
    meta["page"]["description"] = sanitize_meta_content(meta["page"].get("description"))
    # TODO: Consider rendering author name with safe and sanitizing also
    return cast(SaltyPage, meta["page"])

def load_page_breadcrumbs(path: str, has_item: bool) -> list[StrictCrumb]:
  try:
    page_metadata = load_page_metadata(path)
    page_breadcrumb = page_metadata["breadcrumb"]
    if has_item:
      page_breadcrumb["item"] = page_metadata["url"]
  except FileNotFoundError as exc:
    page_breadcrumb = {}

  page_breadcrumbs = [] if page_breadcrumb == {} else [page_breadcrumb]

  if path == "index":
    return page_breadcrumbs
  else:
    new_path = re.sub(r'/.*?$', '', path) if re.search(r'/', path) else "index"
    return load_page_breadcrumbs(new_path, True) + page_breadcrumbs
    
def load_page_content(path: str) -> list[str]:
  page_content_file_path = f"{site_content_path}/pages/{path}.md"
  with open(page_content_file_path, 'r', encoding="utf-8") as file:
    raw_content = file.read()
    content_items = raw_content.split(markdown_delimiter)
    content = [md.render(item) for item in content_items]
    return content
  
def get_microsite_name(path: str) -> str:
  microsite_name = re.sub(r'^/|/\{.*?\}', "", path)
  microsite_name = re.sub(r'/$', "", microsite_name)
  return re.sub("/", "_", microsite_name)

def format_sitemaps_data(routes: list[Route | APIRoute]) -> dict[str: list[StrictSitemapUrl]]:
  sitemaps_data = {"main": []}

  for route in routes:
    if route.path.startswith(("/docs", "/redoc", "/sitemaps", "/static", "/robots.txt")):
      continue

    if route.path.endswith((".json")):
      continue

    lastmod = get_last_modified_for_path(route.path)

    if "{" in route.path:
      microsite_name = get_microsite_name(route.path)
      if microsite_name not in sitemaps_data:
        sitemaps_data[microsite_name] = []
    else:
      page_metadata = load_page_metadata(route.path)
      if "noindex" not in page_metadata or not page_metadata["noindex"]:
        sitemaps_data["main"].append({"loc": f"{settings.prod_domain}{route.path}", "lastmod": lastmod})
  
  return sitemaps_data

def path_to_sitemap_url(pathname: str) -> StrictSitemapUrl:
  return {
    "loc": f"{settings.prod_domain}{pathname}",
    "lastmod": get_last_modified_for_path(pathname)
  }

def load_microsite_sitemap_urls(microsite_name: str, show_private: bool = False) -> list[StrictSitemapUrl]:
  directory = re.sub("_", "/", microsite_name)
  parent_path_obj = Path(f"{site_content_path}/pages/{directory}")
  unique_paths = list(set([f"/{directory}/{re.sub(r'\.\w+$', "", path.name)}/" for path in parent_path_obj.iterdir()]))

  if show_private:
    return [path_to_sitemap_url(path) for path in unique_paths]

  public_paths = []

  for path in unique_paths:
    page_metadata = load_page_metadata(path)
    if "noindex" not in page_metadata or not page_metadata["noindex"]:
      public_paths.append(path_to_sitemap_url(path))

  return public_paths
