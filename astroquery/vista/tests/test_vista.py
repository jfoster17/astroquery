# Licensed under a 3-clause BSD style license - see LICENSE.rst
import os
import requests
from contextlib import contextmanager

from astropy.tests.helper import pytest
from astropy.table import Table
import astropy.coordinates as coord
import astropy.units as u
import numpy.testing as npt

from ... import vista
from ...utils import commons
from ...utils.testing_tools import MockResponse
from ...exceptions import InvalidQueryError

DATA_FILES = {"vo_results": "vo_results.html",
              "image_results": "image_results.html",
              "image": "image.fits",
              "votable": "votable.xml",
              "error": "error.html"
              }


def data_path(filename):
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    return os.path.join(data_dir, filename)


@pytest.fixture
def patch_get(request):
    mp = request.getfuncargvalue("monkeypatch")
    mp.setattr(requests, 'get', get_mockreturn)
    return mp


@pytest.fixture
def patch_get_readable_fileobj(request):
    @contextmanager
    def get_readable_fileobj_mockreturn(filename, **kwargs):
        if "fits" in filename:
            file_obj = open(data_path(DATA_FILES["image"]), "rb")
        else:
            file_obj = open(data_path(DATA_FILES["votable"]), "r")
        yield file_obj
    mp = request.getfuncargvalue("monkeypatch")
    mp.setattr(commons, 'get_readable_fileobj', get_readable_fileobj_mockreturn)
    return mp


@pytest.fixture
def patch_parse_coordinates(request):
    def parse_coordinates_mock_return(c):
        return c
    # This should probably be request, not requests, but this mistake has lead
    # to no errors
    # TODO: determine if this patch is ever used
    mp = requests.getfuncargvalue("monkeypatch")
    mp.setattr(commons, 'parse_coordinates', parse_coordinates_mock_return)
    return mp


def get_mockreturn(url, params=None, timeout=10, **kwargs):
    if "Image" in url:
        filename = DATA_FILES["image_results"]
        url = "Image_URL"
    elif "SQL" in url:
        filename = DATA_FILES["vo_results"]
        url = "SQL_URL"
    elif "error" in url:
        filename = DATA_FILES["error"]
        url = "error.html"
    else:
        raise ValueError("Mismatch: no test made for specified URL")
    print(filename)
    print(url)
    content = open(data_path(filename), "r").read()
    return MockResponse(content=content, url=url, **kwargs)


@pytest.mark.parametrize(('dim', 'expected'),
                        [(5 * u.arcmin, 5),
                        (5 * u.degree, 300),
                        ('0d0m30s', 0.5)
                         ])
def test_parse_dimension(dim, expected):
    out = vista.core._parse_dimension(dim)
    npt.assert_approx_equal(out, expected, significant=3)


def test_get_images(patch_get, patch_get_readable_fileobj):
    image = vista.core.Vista.get_images(commons.ICRSCoordGenerator
                                         (ra=83.633083, dec=22.0145, unit=(u.deg, u.deg)),
                                         frame_type='interleave',
                                         programme_id="GCS", waveband="K",
                                         radius=20*u.arcmin)
    assert image is not None


def test_get_images_async_1():
    payload = vista.core.Vista.get_images_async(commons.ICRSCoordGenerator
                                          (ra=83.633083, dec=22.0145, unit=(u.deg, u.deg)),
        radius=20*u.arcmin,
        get_query_payload=True)
    assert 'xsize' not in payload
    assert 'ysize' not in payload

    payload = vista.core.Vista.get_images_async(commons.ICRSCoordGenerator
                                          (ra=83.633083, dec=22.0145, unit=(u.deg, u.deg)),
        get_query_payload=True)
    assert payload['xsize'] == payload['ysize']
    assert payload['xsize'] == 1

    test_mockreturn = get_mockreturn(vista.core.Vista.ARCHIVE_URL, payload)


def test_get_images_async_2(patch_get, patch_get_readable_fileobj):

    image_urls = vista.core.Vista.get_images_async(commons.ICRSCoordGenerator
                                                     (ra=83.633083, dec=22.0145, unit=(u.deg, u.deg)))
    assert len(image_urls) == 1


def test_get_image_list(patch_get, patch_get_readable_fileobj):
    urls = vista.core.Vista.get_image_list(commons.ICRSCoordGenerator
                                            (ra=83.633083, dec=22.0145, unit=(u.deg, u.deg)),
                                             frame_type='all', waveband='all')
    print(urls)
    assert len(urls) == 1


def test_extract_urls():
    html_in = open(data_path(DATA_FILES["image_results"]), 'rb').read()
    urls = vista.core.Vista.extract_urls(html_in)
    assert len(urls) == 1


def test_query_region(patch_get, patch_get_readable_fileobj):
    table = vista.core.Vista.query_region(commons.GalacticCoordGenerator
                                            (l=10.625, b=-0.38, unit=(u.deg, u.deg)),
                                            radius=6 * u.arcsec)
    assert isinstance(table, Table)
    assert len(table) > 0


def test_query_region_async(patch_get):
    response = vista.core.Vista.query_region_async(commons.GalacticCoordGenerator
                                                     (l=10.625, b=-0.38, unit=(u.deg, u.deg)),
                                                     radius=6 * u.arcsec,
                                                     get_query_payload=True)
    assert response['radius'] == 0.1
    response = vista.core.Vista.query_region_async(commons.GalacticCoordGenerator
                                                     (l=10.625, b=-0.38, unit=(u.deg, u.deg)),
                                                     radius=6 * u.arcsec)
    assert response is not None


def test_check_page_err(patch_get):
    with pytest.raises(InvalidQueryError):
        vista.core.Vista._check_page("error", "dummy")

