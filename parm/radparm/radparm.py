#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Store radiative properties for radiation modeling.

Created on Tue Nov 15 12:26:39 2016

@author: maxwell
"""

from ..parmfactory import ParmFactory

class RadParm(object):
    """
    Class container to store radiation properties.

    Keeps track of emissivity, albedo, solar geometry, etc.
    """


    def __init__(self, **kwargs):
        """
        Set or specify values of radition properties.

        Possible Keyworded arguments:
            emiss = 1.0  surface greybody lw emissivity
            albdo = 0.3  surface broad sw albedo
            fdayl = 0.5  fractional length of day, or, daylighthrs/24
            coszn = 0.5  cosine of the (mean daily) solar zenith angle
            scons = 1361 solar constant at TOA in W m-2
        """
        self.emiss = kwargs.get('emiss',1.0)
        self.albdo = kwargs.get('albdo',0.3)
        self.fdayl = kwargs.get('fdayl',0.5)
        self.coszn = kwargs.get('coszn',0.5)
        self.scons = kwargs.get('scons',1361.0)
        self.name = self.__class__.__name__

class RadParmFactory(ParmFactory):
    """
    Factory methods for RadParm class objects.

    Extends ParmFactory class.
    """
    _classnames = {'':RadParm,'RadParm':RadParm}
