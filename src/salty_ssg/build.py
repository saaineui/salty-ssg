import socket
import subprocess
import time
import argparse
import json
import re
import urllib.request
import os

from pathlib import Path
from typing import Any
from shutil import copytree, ignore_patterns

from salty_ssg.settings import settings
from salty_ssg.utils_build import get_routes_errors, get_folders, static_folder

static_source = "../../site/theme/static"

def load_sitemaps_data() -> dict[str: Any]:
  with urllib.request.urlopen(f"{settings.salty_source}/sitemaps.json") as response:
    if response.status != 200:
      raise RuntimeError(f"Sitemaps fetch failed with {response.status}")
    
    raw_data = response.read().decode("utf-8")
    return json.loads(raw_data)

def is_port_in_use(host: str, port: int) -> bool:
  # Check if a given host and port are accepting TCP connections.
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.settimeout(1.0)
    return s.connect_ex((host, port)) == 0

def ensure_server_running(host: str, port: int):
  if is_port_in_use(host, port):
    return None

  print(f"Starting the staging site on {host}:{port}...")

  # Spawn the process in the background
  process = subprocess.Popen(
    ["poetry", "run", "uvicorn", "main:app", f"--host={host}", f"--port={port}"]
  )

  time.sleep(2)
  return process

def save_sitemaps(sitemaps_data: dict[str: Any]):
  for sitemap_name in sitemaps_data.keys():
    sitemap_url = f"{settings.salty_source}/sitemaps/{sitemap_name}.xml"
    with urllib.request.urlopen(sitemap_url) as response:
      sitemap_xml = response.read().decode('utf-8')

      # Skip empty sitemaps
      if re.search("<url>", sitemap_xml) == None:
        continue

      Path(f"{settings.salty_target}{sitemap_name}-sitemap.xml").write_text(sitemap_xml, encoding="utf-8")

def save_robots():
  with urllib.request.urlopen(f"{settings.salty_source}/robots.txt") as response:
    robots_doc = response.read().decode('utf-8')
    Path(f"{settings.salty_target}robots.txt").write_text(robots_doc, encoding="utf-8")

def save_page(prod_url: str):
  target_filename = re.sub(f"{settings.prod_domain}/", settings.salty_target, prod_url) + "index.html"

  with urllib.request.urlopen(re.sub(settings.prod_domain, settings.salty_source, prod_url)) as response:
    doc = response.read().decode('utf-8')

    # Scrub local URLs
    doc = re.sub(settings.salty_source, settings.prod_domain, doc)

    Path(target_filename).write_text(doc, encoding="utf-8")

def save_pages(sitemaps_data: dict[str: Any]):
  for sitemap_name in sitemaps_data:
    for url in sitemaps_data[sitemap_name]:
      save_page(url["loc"])

def main():
  # Parse user inputs
  parser = argparse.ArgumentParser()
  parser.add_argument(
    "--autokill",
    action="store_true",
    help="Stop staging site server once done (only has effect if the server is started by the build process)"
  )
  parser.add_argument(
    "--checkall",
    action="store_true",
    help="Check all links in sitemap before running build (default is skipping microsite paths)"
  )
  args = parser.parse_args()

  # Get our source host and port
  source_pattern = r"https?://(?P<host>[\w\-\.]+):(?P<port>\d+)"
  source_matches = re.search(source_pattern, settings.salty_source)

  if source_matches == None:
    raise RuntimeError(f"SALTY_SOURCE is not a properly formatted local URL with host and port (i.e. http://127.0.0.1:8000): {settings.salty_source}")

  source = source_matches.groupdict()

  # Start server if it's not running yet
  server_process = ensure_server_running(source["host"], int(source["port"]))

  print("Loading sitemaps data...")
  sitemaps_data = load_sitemaps_data()
  print("Sitemaps found:")
  print(sitemaps_data)

  routes_errors = get_routes_errors(sitemaps_data, args.checkall)
  if len(routes_errors) > 0:
    print("Route checker failed, fix the following page errors and try again:")
    raise RuntimeError(routes_errors)
  
  print(f"Saving sitemaps and robots.txt to {settings.salty_target}...")
  save_sitemaps(sitemaps_data)
  save_robots()

  print(f"Creating folders as needed in {settings.salty_target}...")
  folders = get_folders(sitemaps_data)

  for folder in folders:
    print(f"- {folder}")
    os.makedirs(f"{settings.salty_target}{folder}", exist_ok=True)

  print(f"Copying static assets in {static_source} to {settings.salty_target}static/...")
  copytree(static_source, f"{settings.salty_target}{static_folder}", ignore=ignore_patterns('.DS_Store', '.keep'), dirs_exist_ok=True)

  print(f"Saving page html to {settings.salty_target}...")
  save_pages(sitemaps_data)

  if args.autokill and server_process != None:
    print(f"Stopping the staging site on {source["host"]}:{source["port"]}...")
    server_process.terminate()

################
# Main process #
################
if __name__ == "__main__":
  main()