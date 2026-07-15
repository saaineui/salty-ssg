from datetime import datetime
from salty_ssg.types import SaltyContext, StrictCrumb

def get_schema(context: SaltyContext, crumbs: list[StrictCrumb]):
  return {
	    "@context": "https://schema.org",
	    "@graph": [
        get_webpage_object(context),
        get_image_object(context),
        get_breadcrumb_list(crumbs, context["page"]["url"]),
        get_website_object(context),
        get_person_object(context)
      ]
    }

def get_webpage_object(context: SaltyContext):
  conditional_entries = {}

  if "is_about" in context["page"] and context["page"]["is_about"]:
    conditional_entries["about"] = {
      "@id": context["author"]["id"]
    }
  
  if "thumbnail" in context["page"] and "url" in context["page"]["thumbnail"]:
    conditional_entries["thumbnailUrl"] = context["page"]["thumbnail"]["url"]

  if "tags" in context["page"]:
    conditional_entries["keywords"] = context["page"]["tags"]
  
  return {
      "@type": "WebPage",
      "@id": context["page"]["url"],
      "url": context["page"]["url"],
      "name": context["page"]["title"],
      "isPartOf": {
        "@id": f"{context["site"]["domain"]}/#website"
      },
      "primaryImageOfPage": {
        "@id": f"{context["page"]["url"]}#primaryimage"
      },
      "image": {
        "@id": f"{context["page"]["url"]}#primaryimage"
      },
      "datePublished": context["page"]["date_published"],
      "dateModified": context["page"]["date_modified"],
      "description": context["page"]["description"],
      "breadcrumb": {
        "@id": f"{context["page"]["url"]}#breadcrumb"
      },
      "inLanguage": context["site"]["locale"],
      "potentialAction": [
        {
          "@type": "ReadAction",
          "target": [
            context["page"]["url"]
          ]
        }
      ]
    } | conditional_entries

def get_image_object(context: SaltyContext):
  if "thumbnail" not in context["page"]:
    return {}
  else:
	  return {
      "@type": "ImageObject",
      "@id": f"{context["page"]["url"]}#primaryimage",
      "url": context["page"]["thumbnail"]["url"],
      "contentUrl": context["page"]["thumbnail"]["url"],
      "width": context["page"]["thumbnail"]["width"],
      "height": context["page"]["thumbnail"]["height"]
    }

def generate_breadcrumb_list_item(crumb: StrictCrumb):
  conditional_entries = {
      "item": crumb["item"]
    } if "item" in crumb else {}

  return {
      "@type": "ListItem",
      "position": crumb["position"],
      "name": crumb["name"]      
    } | conditional_entries

def get_breadcrumb_list(crumbs: list[StrictCrumb], page_url: str):
  return {
      "@type": "BreadcrumbList",
      "@id": f"{page_url}#breadcrumb",
      "itemListElement": [generate_breadcrumb_list_item(crumb) for crumb in crumbs]
    }

def get_website_object(context: SaltyContext):
  return {
      "@type": "WebSite",
      "@id": f"{context["site"]["domain"]}/#website",
      "url": context["site"]["domain"],
      "name": context["site"]["site_name"],
      "description": context["site"]["description"],
      "publisher": {
        "@id": context["author"]["id"]
      },
      "inLanguage": "en-US"
    }

def get_person_object(context: SaltyContext):
  return {
      "@type": [
        "Person",
        "Organization"
      ],
      "@id": context["author"]["id"],
      "name": context["author"]["name"],
      "image": {
        "@type": "ImageObject",
        "@id": context["author"]["image"]["id"],
        "url": context["author"]["image"]["url"],
        "contentUrl": context["author"]["image"]["url"],
        "width": context["author"]["image"]["width"],
        "height": context["author"]["image"]["height"],
        "caption": context["author"]["image"]["caption"]
      },
      "logo": {
        "@id": context["author"]["logo"]["id"],
        "@type": "ImageObject",
        "url": context["author"]["logo"]["url"],
        "contentUrl": context["author"]["logo"]["url"],
        "width": context["author"]["logo"]["width"],
        "height": context["author"]["logo"]["height"],
        "caption": context["author"]["name"]
      },
      "sameAs": context["author"]["same_as"]
    }

