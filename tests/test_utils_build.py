from unittest.mock import patch, MagicMock
from urllib.error import HTTPError
import io
from salty_ssg.utils_build import get_route_status, get_routes_errors, get_folders
from salty_ssg.settings import settings

mock_timestamp = "2026-06-29T20:36:54+00:00"
sitemaps_data_mock = {
  "main": [
    {
      "loc": f"{settings.prod_domain}/about/",
      "lastmod": mock_timestamp
    }
  ],
  "posts": [
    {
      "loc": f"{settings.prod_domain}/posts/hello/",
      "lastmod": mock_timestamp
    }
  ]
}

@patch("salty_ssg.utils_build.urllib.request.urlopen")
def test_get_route_status_success(mock_urlopen):
  mock_response = MagicMock()
  mock_response.status = 200
  mock_urlopen.return_value.__enter__.return_value = mock_response

  assert get_route_status(f"{settings.salty_source}/about/") == 200

@patch("salty_ssg.utils_build.urllib.request.urlopen")
def test_get_route_status_error(mock_urlopen):
  mock_urlopen.side_effect = HTTPError(
    url=f"{settings.salty_source}/abut/",
    code=404,
    msg="Not Found",
    hdrs={},
    fp=io.BytesIO(b"Not Found")
  )

  assert get_route_status(f"{settings.salty_source}/abut/") == 404

@patch("salty_ssg.utils_build.urllib.request.urlopen")
def test_get_routes_errors_with_errors(mock_urlopen):
  mock_urlopen.side_effect = HTTPError(
    url=f"{settings.salty_source}/borked/",
    code=500,
    msg="Internal Server Error",
    hdrs={},
    fp=io.BytesIO(b"Internal Server Error")
  )
  expected_routes_errors = [
    {
      "route": f"{settings.salty_source}/robots.txt",
      "error": 500
    },
    {
      "route": f"{settings.salty_source}/sitemaps/main.xml",
      "error": 500
    },
    {
      "route": f"{settings.salty_source}/about/",
      "error": 500
    },
    {
      "route": f"{settings.salty_source}/sitemaps/posts.xml",
      "error": 500
    }
  ]

  assert get_routes_errors(sitemaps_data_mock) == expected_routes_errors

  expected_routes_errors.append({
    "route": f"{settings.salty_source}/posts/hello/",
    "error": 500
  })

  assert get_routes_errors(sitemaps_data_mock, True) == expected_routes_errors

@patch("salty_ssg.utils_build.urllib.request.urlopen")
def test_get_routes_errors(mock_urlopen):
  mock_response = MagicMock()
  mock_response.status = 200
  mock_urlopen.return_value.__enter__.return_value = mock_response

  assert get_routes_errors(sitemaps_data_mock) == []
  assert get_routes_errors(sitemaps_data_mock, True) == []

def test_get_folders():
  expected_folders = [
    "static",
    "about",
    "posts/hello"
  ]
  assert get_folders(sitemaps_data_mock) == expected_folders