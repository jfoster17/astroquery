# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import print_function

from astropy.tests.helper import remote_data
from astropy.table import Table
import astropy.coordinates as coord
import astropy.units as u
import requests
import imp
imp.reload(requests)

from ... import vista


@remote_data
class TestVista:
    vista.core.Vista.TIMEOUT = 20

    def test_get_images_1(self):
        images = vista.core.Vista.get_images("m13")
        assert images is not None

    def test_get_images_2(self):
        images = vista.core.Vista.get_images(coord.Galactic
                                               (l=330.1, b=-0.1, unit=(u.deg, u.deg)),
                                               image_width=5 * u.arcmin)
        assert images is not None

    def test_get_images_async(self):
        images = vista.core.Vista.get_images_async("m13")
        assert images is not None

    def test_get_image_list(self):
        urls = vista.core.Vista.get_image_list(coord.ICRS
                                            (ra=83.633083, dec=22.0145, unit=(u.deg, u.deg)),
            frame_type='all', waveband='all')
        assert len(urls) > 0

    def test_query_region_async(self):
        response = vista.core.Vista.query_region_async(coord.Galactic
                                                   (l=340.5, b=-0.38, unit=(u.deg, u.deg)),
            radius=6 * u.arcsec)
        assert response is not None

    def test_query_region(self):
        table = vista.core.Vista.query_region(coord.Galactic
                                                (l=340.5, b=-0.38, unit=(u.deg, u.deg)),
                                                radius=6 * u.arcsec)
        assert isinstance(table, Table)
        assert len(table) > 0
