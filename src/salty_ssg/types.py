from typing import TypedDict, Any, TypeGuard

class StrictSite(TypedDict):
  locale: str
  locale_dash: str
  type: str
  site_name: str
  domain: str
  description: str | None
  icons: dict[str, str] | None

class StrictImage(TypedDict):
    id: str
    url: str
    width: int
    height: int
    caption: str | None
    type: str | None

class StrictAuthor(TypedDict):
  id: str
  same_as: list[str]
  logo: StrictImage
  image: StrictImage

class StrictCrumb(TypedDict):
   name: str
   position: int
   item: str | None

class StrictPage(TypedDict):
  title: str
  description: str
  url: str
  date_published: str
  date_modified: str | None
  breadcrumb: StrictCrumb | None
  is_about: bool | None
  thumbnail: StrictImage | None
  tags: list[str] | None
  content: list[str] | None
  schema: dict[str, Any] | None
   
SaltySite = StrictSite | dict[str, Any]
SaltyAuthor = StrictAuthor | dict[str, Any]
SaltyPage = StrictPage | dict[str, Any]

class StrictMeta:
   site: SaltySite
   author: SaltyAuthor   

class SaltyContext(TypedDict):
   site: SaltySite
   author: SaltyAuthor
   page: SaltyPage

class StrictSitemapUrl:
   loc: str
   lastmod: str

def is_valid_meta(meta: Any) -> TypeGuard[StrictMeta]:
  return (
    isinstance(meta, dict) 
    and "site" in meta 
    and "author" in meta
  )

def is_valid_page(page: Any) -> TypeGuard[SaltyPage]:
  return (
    isinstance(page, dict) 
    and "title" in page 
    and "description" in page
    and "url" in page
    and "date_published" in page
  )