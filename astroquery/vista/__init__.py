# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
VISTA Image and Catalog Query Tool
-----------------------------------
.. topic:: Revision History

    Contributed by Jonathan Foster (jonathan.bruce.foster@gmail.com)

    :Based on the UKIDSS version originally contributed by:

        Thomas Robitalle (thomas.robitaille@gmail.com)

        Adam Ginsburg (adam.g.ginsburg@gmail.com)
"""
from astropy.config import ConfigurationItem

VISTA_SERVER = ConfigurationItem('vista_server', ["http://horus.roe.ac.uk:8080/vdfs/"],
                                  'Name of the VISTA mirror to use.')
VISTA_TIMEOUT = ConfigurationItem('timeout', 60, 'time limit for connecting to VISTA server')

from .core import Vista,VistaClass,clean_catalog

__all__ = ['Vista','VistaClass','clean_catalog']
