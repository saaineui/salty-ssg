import re
from salty_ssg.utils import load_site_metadata, load_page_metadata, load_page_content

def test_load_site_metadata():
  locale = load_site_metadata()["site"]["locale"]
  assert re.search(r"[a-z]{2}_[A-Z]{2}", locale) != None
  author_name = load_site_metadata()["author"]["name"]
  assert re.search(r"[\w ]+", author_name) != None

def test_load_page_metadata():
  page = load_page_metadata("_page")
  assert page["url"] == "https://www.example.com"
  assert re.search(r"^\d{4}-\d{2}-\d{2}", page["date_modified"]) != None

def test_load_page_content():
  content = load_page_content("_page")
  assert re.search(r"^<h2>Why use Salty SSG", content[0]) != None