import re, copy
from salty_ssg.utils_schema import get_webpage_object, get_image_object, get_breadcrumb_list, get_website_object, get_person_object, get_schema

test_context = {
  "site": {
    "domain": "https://www.example.com",
    "site_name": "Saul Tee's Website",
    "description": "Personal website",
    "locale": "en_US"
  },
  "author": {
    "name": "Saul Tee",
    "id": "https://www.example.com/#/schema/person/1",
    "same_as": [
      "https://www.example.com"
    ],
    "logo": {
      "id": "https://www.example.com/#/schema/logo/image",
      "url": "https://www.example.com/assets/images/logo.jpg",
      "width": 180,
      "height": 80,
    },
    "image": {
      "id": "https://www.example.com/#primaryimage",
      "url": "https://www.example.com/assets/images/profile.jpg",
      "width": 80,
      "height": 80,
      "caption": "Saul Tee"
    }
  },
  "page": {
    "title": "Lorem - About Ipsum",
    "breadcrumb": {
      "name": "Home",
      "position": 1
    },
    "description": "Lorem ipsum aloha mahalo.",
    "url": "https://www.example.com/about/",
    "date_published": "2022-08-08T15:17:00+00:00",
    "date_modified": "2022-11-12T15:11:00+00:00",
    "thumbnail": {
      "url": "https://www.example.com/assets/images/profile.jpg",
      "width": 80,
      "height": 80
    },
    "tags": [
      "SSG",
      "Python"
    ]
  }
}

def test_get_webpage_object():
  test_context_copy = copy.deepcopy(test_context)

  webpage_object = get_webpage_object(test_context_copy)
  assert webpage_object["@id"] == test_context_copy["page"]["url"]
  assert webpage_object["image"]["@id"] == "https://www.example.com/about/#primaryimage"
  assert webpage_object["thumbnailUrl"] == test_context_copy["page"]["thumbnail"]["url"]
  assert webpage_object["keywords"] == test_context_copy["page"]["tags"]
  assert "about" not in webpage_object

  test_context_copy["page"]["is_about"] = True
  del test_context_copy["page"]["thumbnail"]
  del test_context_copy["page"]["tags"]
  webpage_object_2 = get_webpage_object(test_context_copy)
  assert "about" in webpage_object_2
  assert "thumbnailUrl" not in webpage_object_2
  assert "keywords" not in webpage_object_2

def test_get_image_object():
  image_object = get_image_object(test_context)
  assert image_object["@id"] == f"{test_context["page"]["url"]}#primaryimage"

def test_get_empty_image_object():
  image_object = get_image_object({"page": {}})
  assert image_object == {}

def test_get_breadcrumb_list():
  breadcrumb_list = get_breadcrumb_list([test_context["page"]["breadcrumb"]], test_context["site"]["domain"])
  assert breadcrumb_list["itemListElement"][0]["position"] == 1

def test_get_website_object():
  website_object = get_website_object(test_context)
  assert website_object["url"] == test_context["site"]["domain"]

def test_get_person_object():
  person_object = get_person_object(test_context)
  assert person_object["name"] == test_context["author"]["name"]

def test_get_schema():
  schema = get_schema(test_context, [])
  assert schema["@context"] == "https://schema.org"

