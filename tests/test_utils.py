import pytest
import re
from unittest.mock import patch
from fastapi.routing import APIRoute
from salty_ssg.utils import load_site_metadata, load_page_metadata, load_page_content, load_page_breadcrumbs, get_microsite_name, format_sitemaps_data, load_microsite_sitemap_urls, sanitize_meta_content

@pytest.fixture
def mock_routes():
  def dummy_docs(): pass
  def dummy_home(): pass
  def dummy_home_json(): pass
  def dummy_dynamic(): pass

  routes = [
    APIRoute(path="/docs", endpoint=dummy_docs, methods=["GET"]),
    APIRoute(path="/", endpoint=dummy_home, methods=["GET"]),
    APIRoute(path="/index.json", endpoint=dummy_home_json, methods=["GET"]),
    APIRoute(path="/fixtures/{slug}/", endpoint=dummy_dynamic, methods=["GET"]),
  ]
  
  return routes

def test_load_site_metadata():
  locale = load_site_metadata()["site"]["locale"]
  assert re.search(r"[a-z]{2}_[A-Z]{2}", locale) != None
  author_name = load_site_metadata()["author"]["name"]
  assert re.search(r"[\w ]+", author_name) != None

def test_load_page_metadata():
  page = load_page_metadata("fixtures/_page")
  assert page["url"] == "https://www.example.com/fixtures/_page/"
  assert re.search(r"^\d{4}-\d{2}-\d{2}", page["date_modified"]) != None

def test_sanitize_meta_content():
  page = {}
  assert sanitize_meta_content(page.get("description")) == ""
  assert sanitize_meta_content('"Quotes" get cleaned') == "&quot;Quotes&quot; get cleaned"

def test_load_page_metadata_missing_key():
  with pytest.raises(TypeError):
    load_page_metadata("fixtures/_error")

  with pytest.raises(TypeError):
    load_page_metadata("fixtures/_error2")

def test_load_page_content():
  content = load_page_content("fixtures/_page")
  assert re.search(r"^<h2>\w+", content[0]) != None

def test_load_page_breadcrumbs():
  breadcrumbs = load_page_breadcrumbs("fixtures/_page", False)
  assert breadcrumbs[1] == {"name": "Page", "position": 2}
  assert breadcrumbs[0]["name"] == "Home"
  assert breadcrumbs[0]["position"] == 1
  assert re.search(r"^http", breadcrumbs[0]["item"])

def test_get_microsite_name():
  assert get_microsite_name("/blog/{slug}/") == "blog"
  assert get_microsite_name("/blog/{slug}") == "blog"
  assert get_microsite_name("blog/{slug}") == "blog"
  assert get_microsite_name("/blog/features/{slug}/") == "blog_features"

def test_load_sitemaps_data(mock_routes):
  sitemaps_data = format_sitemaps_data(mock_routes)

  assert "main" in sitemaps_data
  main_sitemap = sitemaps_data["main"]
  assert "loc" in main_sitemap[0]
  assert re.search(r"^http", main_sitemap[0]["loc"]) != None
  assert "lastmod" in main_sitemap[0]
  assert re.search(r"^\d{4}-\d{2}-\d{2}", main_sitemap[0]["lastmod"]) != None
  
  assert "fixtures" in sitemaps_data
  assert sitemaps_data["fixtures"] == []

@patch("salty_ssg.utils.load_page_metadata")
def test_load_microsite_sitemap_urls(mock_load_page_metadata):
  mock_response = {}
  mock_load_page_metadata.return_value = mock_response

  urls = load_microsite_sitemap_urls("fixtures")

  assert re.search(r"https?://.*?/fixtures/_\w+/", urls[0]["loc"]) != None
  assert re.search(r"^\d{4}-\d{2}-\d{2}", urls[0]["lastmod"]) != None

@patch("salty_ssg.utils.load_page_metadata")
def test_load_microsite_sitemap_urls_with_noindex(mock_load_page_metadata):
  mock_response = {"noindex": True}
  mock_load_page_metadata.return_value = mock_response
  
  urls = load_microsite_sitemap_urls("fixtures")
  assert len(urls) == 0

  urls_show_private = load_microsite_sitemap_urls("fixtures", True)
  assert re.search(r"https?://.*?/fixtures/_\w+/", urls_show_private[0]["loc"]) != None
  assert re.search(r"^\d{4}-\d{2}-\d{2}", urls_show_private[0]["lastmod"]) != None
