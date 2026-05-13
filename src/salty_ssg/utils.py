import yaml
from datetime import datetime
from pathlib import Path
from markdown_it import MarkdownIt

markdown_delimiter = "[=================]"

script_dir = Path(__file__).resolve().parent
site_content_path = script_dir.parent.parent / "site" / "content"

md = (
    MarkdownIt('commonmark', {'breaks':True,'html':True})
)

def load_site_metadata():
  with open(f"{site_content_path}/meta.yml", 'r') as file:
    try:
      meta = yaml.safe_load(file)
      return meta
    except yaml.YAMLError as exc:
      print(f"Error parsing YAML file: {exc}")
      return {}

def load_page_metadata(path):
  page_file_path = f"{site_content_path}/pages/{path}.yml"
  page_file_modified_timestamp = Path(page_file_path).stat().st_mtime
  page_file_modified_timestamp_dateobj = datetime.fromtimestamp(page_file_modified_timestamp)
  date_modified = f"{page_file_modified_timestamp_dateobj.strftime("%Y-%m-%dT%H:%M:%S")}+00:00"

  with open(page_file_path, 'r') as file:
    try:
      meta = yaml.safe_load(file)
      # Get the latest from either yml or md file
      meta["page"]["date_modified"] = date_modified
      return meta["page"]
    except yaml.YAMLError as exc:
      print(f"Error parsing YAML file: {exc}")
      return {}
    
def load_page_content(path):
  page_content_file_path = f"{site_content_path}/pages/{path}.md"
  with open(page_content_file_path, 'r', encoding="utf-8") as file:
    raw_content = file.read()
    content_items = raw_content.split(markdown_delimiter)
    content = [md.render(item) for item in content_items]
    return content
