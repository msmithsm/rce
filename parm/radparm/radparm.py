#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Store radiative properties for radiation modeling (RRTMG).


SW and LW parameters are stored separately for speed in calling radiation.
This removes the need for large numbers of dictionary unpackings to find and
extract appropriate values

Created on Tue Nov 15 12:26:39 2016

@author: maxwell
"""

from ..parm import Parm

class SWParm(Parm):
    """
    Dict-like container to store SW radiation properties.

    Keeps track of albedo, solar geometry, etc. Uses variable names
    that are consistent iwth the argumenst to pyRRTMG.
    """

    def __init__(self, albedo=None, fday=None, coszen=None, scon=None):
        """
        Set or specify values of radition properties.

        Possible Keyworded arguments:
            albedo = 0.3  surface broad sw albedo
            fday = 0.5  fractional length of day, or, daylighthrs/24
            coszen = 0.5  cosine of the (mean daily) solar zenith angle
            scon = 1361 solar constant at TOA in W m-2
        """
        cls = self.__class__.__name__
        if albedo is None:
            self.albedo = 0.3
            print(
              "{cls}: using default albedo value of {val}".format(
               cls=cls, val=self.albedo)
               )
        else:
            self.albedo = albedo
        if fday is None:
            self.fday = 0.5
            print(
              "{cls}: using default fday value of {val}".format(
               cls=cls, val=self.fday)
               )
        else:
            self.fday = fday
        if coszen is None:
            self.coszen = 0.5
            print(
              "{cls}: using default coszen value of {val}".format(
               cls=cls, val=self.coszen)
               )
        else:
            self.coszen = coszen
        if scon is None:
            self.scon = 1361.0
            print(
              "{cls}: using default scon value of {val} W m-2".format(
               cls=cls, val=self.scon)
               )
        else:
            self.scon = scon

class LWParm(Parm):
    """
    Dict-like container to store LW radiation properties.
    """

    def __init__(self, emis=None):
        """
        Set LW parameters

        Possible keyword argumens:
            emis = 1.0
        """
        cls = self.__class__.__name__
        if emis is None:
            self.emis = 1.0
            print(
              "{cls}: using default emis value of {val}".format(
               cls=cls, val=self.emis)
               )
        else:
            self.emis = emis

