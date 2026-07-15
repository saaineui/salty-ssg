import urllib.request
from urllib.error import HTTPError
from typing import Any
import re
from salty_ssg.settings import settings

static_folder = "static"

def get_route_status(url: str) -> int:
  try:
    with urllib.request.urlopen(url) as response:
      return response.status
  except HTTPError as exc:
    return exc.code

def get_routes_errors(sitemaps_data: dict[str: Any], checkall: bool = False) -> bool:
  routes_errors = []

  robots_url = f"{settings.salty_source}/robots.txt"
  robots_route_status = get_route_status(robots_url)
  if robots_route_status != 200:
    routes_errors.append({"route": robots_url, "error": robots_route_status})

  for sitemap_name in sitemaps_data.keys():
    sitemap_url = f"{settings.salty_source}/sitemaps/{sitemap_name}.xml"
    sitemap_route_status = get_route_status(sitemap_url)
    if sitemap_route_status != 200:
      routes_errors.append({"route": sitemap_url, "error": sitemap_route_status})

    if checkall or sitemap_name == "main":
      urlset = sitemaps_data[sitemap_name]

      for url in urlset:
        local_url = re.sub(settings.prod_domain, settings.salty_source, url["loc"])
        route_status = get_route_status(local_url)
        if route_status != 200:
          routes_errors.append({"route": local_url, "error": route_status})
  
  return routes_errors

def url_to_folder(url: str):
  path = re.sub(settings.prod_domain, "", url)
  return re.sub(r"^/|/$", "", path)

def get_folders(sitemaps_data: dict[str: Any]):
  folders = [static_folder]

  for sitemap_name in sitemaps_data:
    urlset = sitemaps_data[sitemap_name]
    for url in urlset:
      folder = url_to_folder(url["loc"])

      if folder != "":
        folders.append(folder)

  return folders