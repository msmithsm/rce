#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Heating rate calculations

Created on Fri Nov 18 15:05:39 2016

@author: maxwell
"""

__all__ = ['heatingrates']


import atmosphere.constants as c
from   atmosphere import readprof_hr
from   atmosphere import Atmosphere
import numpy as np



class HR(object):
    """
    HR container
    """
    _maxHR = 5.0

    def __init__(self, hrir, hrsw):
        self.hrir = hrir
        self.hrsw = hrsw

    @classmethod
    def fromfile(cls, atms=None, fname=None):
        """
        Read HR profile form file
        """
        zs, hrirs, hrsws = readprof_hr(fname)

        if atms is not None:
            hrir = np.empty(len(atms))
            hrsw = np.empty(len(atms))
            hrir[::-1] = Atmosphere.interp(zs[::-1], hrirs[::-1],atms.z[::-1])
            hrsw[::-1] = Atmosphere.interp(zs[::-1], hrsws[::-1],atms.z[::-1])
        else:
            hrir = hrirs
            hrsw = hrsws

        return cls(hrir,hrsw)

    @property
    def hr(self):
        return self.hrir + self.hrsw


def heatingrates(atms, Flux):
    """
    Calculate heating rates using an Atmosphere() object and a Flux() object.
    """

    if atms.gridstagger:
        return _hr12(atms,Flux)
    else:
        return _hr23(atms,Flux)

def _hr12(atms,flx):
    """
    1st order Heating rate calculation (2nd-order error)
    """
    f = ((c.grav*c.secperdy)/(c.mb2pa*c.cpdair))
    dpinv = 1.0/(atms.plev[:-1] - atms.plev[1:])
    hrir = f*((flx.fir[:-1]-flx.fir[1:])*dpinv)
    hrsw = f*((flx.fsw[:-1]-flx.fsw[1:])*dpinv)


    hrir = np.sign(hrir)*np.minimum(HR._maxHR, np.abs(hrir))
    hrsw = np.sign(hrsw)*np.minimum(HR._maxHR, np.abs(hrsw))

    return HR(hrir,hrsw)


def _hr23(atms,flx):
    """
    2nd order Heatingrate calculation (3rd-order error)
    """

    f = ((c.grav*c.secperdy)/(c.mb2pa*c.cpdair))

    hrir = np.empty(len(atms.plev))
    hrsw = np.empty(len(atms.plev))

    fir = flx.fir.copy()
    fsw = flx.fsw.copy()
#    fir[[-1]] = 0.0
#    fsw[[-1]] = 0.0

    #centered diff in interior
    dprat = (atms.plev[2:]-atms.plev[1:-1])/(atms.plev[1:-1] - atms.plev[:-2])
    dpinv = 1.0/(atms.plev[2:] - atms.plev[:-2])

    c1 = dprat*dpinv
    c2 = (1.0/dprat)*dpinv

    hrir[1:-1] = f*( c1*(fir[1:-1]-fir[:-2])
                    +c2*(fir[2:]-fir[1:-1]) )
    hrsw[1:-1] = f*( c1*(fsw[1:-1]-fsw[:-2])
                    +c2*(fsw[2:]-fsw[1:-1]) )

    #forward diff on edges
    dprat = np.array(
        [(atms.plev[1]-atms.plev[0])/(atms.plev[2]-atms.plev[0]),
         (atms.plev[-2] - atms.plev[-1])/(atms.plev[-3] - atms.plev[-1])]
        )
    dpinv = 1.0/np.array(
                [(atms.plev[1]-atms.plev[2]), (atms.plev[-2]-atms.plev[-3])]
                )
    c1 = dprat*dpinv
    c2 = (1.0/dprat)*dpinv


    hrir[0] = f*(c1[0]*(fir[2]-fir[0]) +c2[0]*(fir[0]-fir[1]))
    hrsw[0] = f*(c1[0]*(fsw[2]-fsw[0]) +c2[0]*(fsw[0]-fsw[1]))


    hrir[-1] = f*(
        c1[1]*(fir[-3]-fir[-1]) +c2[1]*(fir[-1]-fir[-2]) )
    hrsw[-1] = f*(
        c1[1]*(fsw[-3]-fsw[-1]) +c2[1]*(fsw[-1]-fsw[-2]) )

#    #HR is 0 at bottom, since we use a different algorithm for tsfc
#    hrir[-1] = 0
#    hrsw[-1] = 0

    hrir = np.sign(hrir)*np.minimum(HR._maxHR, np.abs(hrir))
    hrsw = np.sign(hrsw)*np.minimum(HR._maxHR, np.abs(hrsw))

    return HR(hrir, hrsw)
