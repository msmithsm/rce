#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Class definitions for Fu Objects in RCE model. Implements bridge between
fupy API and the RCE model solver requirements.

Created on Mon Dec  5 03:35:12 2016

@author: maxwell
"""


from radiation.radiation import RadModel,Flux
from radiation.fupy import fupy
import numpy as np


class FuModel(RadModel):
    """
    Class construct for pyrrtmg
    """

    def __init__(self,**kwargs):

        print('ititializing fu object')
        fupy.init()

    def radiation(self,atms,cparm,lwparm, swparm):
        """
        Calculates Fu radiation.

        Expects an Atmosphere object with the following variables (size):
            plev (n+1)
            tlev (n+1)
            atms.tsfc
            qlay (n)
            o3lay (n)
        Expects a ChemParm object with the following scalars:
            co2
            ch4
            n2o
            o2
            cfc11
            cfc12
            cfc22
            ccl4
        Expects a LWParm object with the following scalars:
            emis
        Expects a SWParm object with the following scalars:
            albedo
            fday
            coszen
            scon

        Returns a Flux object with short and longwave fluxes
        """
        fuir = np.empty(len(atms.plev))
        fdir = np.empty(len(atms.plev))
        fusw = np.empty(len(atms.plev))
        fdsw = np.empty(len(atms.plev))

        # flip indices, since rrtm expects pressure to decrease with index,
        # while the Atmosphere class expects pressure to increase with index.
        (fuir, fdir, fusw, fdsw) = fupy.rad(
            atms.plev, atms.tlev, atms.tsfc,
            atms.qlev, atms.o3lev, **cparm, **lwparm,**swparm
            )

        return Flux(fuir,fdir,fusw,fdsw)

