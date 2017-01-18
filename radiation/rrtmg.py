#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Class definitions for RRTMG objects in RCE model. Implements bridge between
pyRRTMG API and the RCE model solver requirements.

Created on Tue Nov 15 18:43:23 2016

@author: maxwell
"""


from radiation.radiation import RadModel,Flux
import radiation.pyrrtmg as rr
import numpy as np


class RRTMGModel(RadModel):
    """
    Class construct for pyrrtmg
    """

    def __init__(self,cpdair=None,**kwargs):

        print('ititializing rrtmg object')
        if cpdair is None:
            print(
                "WARNING: cpdair not provided to RRTMGModel. " ,
                "Using pyRRTMG default."
                 )
            rr.lw.init()
            rr.sw.init()
        else:
            rr.lw.init(cpdair)
            rr.sw.init(cpdair)
    def radiation(self,atms,cparm,lwparm, swparm):
        """
        Calculates RRTMG radiation.

        Expects an Atmosphere object with the following variables (size):
            play (n)
            plev (n+1)
            tlay (n)
            tlev (n+1)
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
        (fuir[::-1], fdir[::-1]) = rr.lw.rad(atms.play[::-1], atms.plev[::-1],
                                 atms.tlay[::-1], atms.tlev[::-1],
                                 atms.tsfc,
                                 atms.qlay[::-1], atms.o3lay[::-1],
                                 **cparm, **lwparm)
        (fusw[::-1], fdsw[::-1]) = rr.sw.rad(atms.play[::-1], atms.plev[::-1],
                                 atms.tlay[::-1], atms.tlev[::-1],
                                 atms.tsfc,
                                 atms.qlay[::-1], atms.o3lay[::-1],
                                 **cparm, **swparm)

        return Flux(fuir,fdir,fusw,fdsw)

